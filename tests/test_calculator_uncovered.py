import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError
from app.operations import Addition
from app.calculator_memento import CalculatorMemento

def test_calculator_init_logs_warning_when_history_fails(monkeypatch, caplog, tmp_path):
    # Prevent logging from being reconfigured
    monkeypatch.setattr("app.calculator.Calculator._setup_logging", lambda self: None)

    # Force load_history to raise an exception
    def fake_load_history(self):
        raise Exception("boom")

    monkeypatch.setattr("app.calculator.Calculator.load_history", fake_load_history)

    caplog.set_level(logging.WARNING)

    config = CalculatorConfig(base_dir=tmp_path)

    # Act
    calc = Calculator(config=config)

    # Assert
    assert any("Could not load existing history: boom" in msg for msg in caplog.messages)
    
    # 103-106
def test_setup_logging_error_is_printed_and_reraised(monkeypatch, capsys, tmp_path):
    # Force logging.basicConfig to raise an exception
    def fake_basic_config(*args, **kwargs):
        raise Exception("logging failed")

    monkeypatch.setattr("logging.basicConfig", fake_basic_config)

    config = CalculatorConfig(base_dir=tmp_path)

    # Act + Assert: Calculator init should raise because _setup_logging re-raises
    with pytest.raises(Exception, match="logging failed"):
        Calculator(config=config)

    # Capture printed output
    captured = capsys.readouterr()

    # Assert the error message was printed
    assert "Error setting up logging: logging failed" in captured.out
    
    # 219
def test_history_is_trimmed_when_exceeding_max_size(monkeypatch, tmp_path):
    # Prevent history from loading from disk
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)

    # Set max_history_size to 1 so popping happens immediately
    config = CalculatorConfig(base_dir=tmp_path, max_history_size=1)
    calc = Calculator(config=config)

    # Set operation strategy
    calc.set_operation(Addition())

    # Perform first operation
    calc.perform_operation("1", "1")
    assert len(calc.history) == 1

    # Perform second operation — this should trigger history.pop(0)
    calc.perform_operation("2", "2")

    # Now history should still be size 1, but the first entry should be gone
    assert len(calc.history) == 1
    assert calc.history[0].operand1 == Decimal("2")
    assert calc.history[0].operand2 == Decimal("2")

# 230 - 233
def test_perform_operation_raises_operation_error_on_unexpected_exception(monkeypatch, tmp_path):
    # Prevent history from loading
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)

    class BadOperation:
        def __str__(self):
            return "BadOperation"
        def execute(self, a, b):
            raise Exception("unexpected boom")

    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)

    # Set the bad operation strategy
    calc.set_operation(BadOperation())

    # Act + Assert: perform_operation should wrap the exception in OperationError
    with pytest.raises(OperationError) as exc:
        calc.perform_operation("1", "2")

    # Verify the message is correct
    assert "Operation failed: unexpected boom" in str(exc.value)

    # 268 - 275
def test_save_history_raises_operation_error_on_failure(monkeypatch, tmp_path):
    # Prevent history from loading
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)

    # Force pandas to_csv to fail
    def fake_to_csv(*args, **kwargs):
        raise Exception("csv write failed")

    monkeypatch.setattr("pandas.DataFrame.to_csv", fake_to_csv)

    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)

    # Add one fake calculation to history so DataFrame path is taken
    class FakeCalc:
        operation = "Add"
        operand1 = "1"
        operand2 = "2"
        result = "3"
        timestamp = datetime.now()

    calc.history.append(FakeCalc())

    # Act + Assert
    with pytest.raises(OperationError) as exc:
        calc.save_history()

    assert "Failed to save history: csv write failed" in str(exc.value)

# 268 - 270
def test_save_history_creates_empty_csv_when_history_empty(monkeypatch, tmp_path, caplog):
    # Prevent logging from being reconfigured
    monkeypatch.setattr("app.calculator.Calculator._setup_logging", lambda self: None)
    # Prevent loading existing history
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)

    caplog.set_level(logging.INFO)

    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)

    # Ensure history is empty
    assert calc.history == []

    # Act
    calc.save_history()

    # Assert CSV file exists
    assert config.history_file.exists()

    # Read CSV using pandas for stable comparison
    import pandas as pd
    df = pd.read_csv(config.history_file)

    # Assert correct headers
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]

    # Assert no rows
    assert df.empty

    # Assert log message was emitted
    assert any("Empty history saved" in msg for msg in caplog.messages)

# 309 - 312
def test_load_history_raises_operation_error_on_failure(monkeypatch, tmp_path, caplog):
    # Prevent logging from being reconfigured
    monkeypatch.setattr("app.calculator.Calculator._setup_logging", lambda self: None)

    caplog.set_level(logging.ERROR)

    # Create a fake history file so exists() returns True
    history_file = tmp_path / "history.csv"
    history_file.write_text("operation,operand1,operand2,result,timestamp\n")

    # Patch config to point to this file
    config = CalculatorConfig(base_dir=tmp_path)

    # Force pandas.read_csv to fail
    def fake_read_csv(*args, **kwargs):
        raise Exception("csv load failed")

    monkeypatch.setattr("pandas.read_csv", fake_read_csv)

    calc = Calculator(config=config)

    # Act + Assert
    with pytest.raises(OperationError) as exc:
        calc.load_history()

    assert "Failed to load history: csv load failed" in str(exc.value)

    # Ensure the error was logged
    assert any("Failed to load history: csv load failed" in msg for msg in caplog.messages)

# 324 - 333
def test_get_history_dataframe_returns_correct_dataframe(monkeypatch, tmp_path):
    # Prevent logging and history loading
    monkeypatch.setattr("app.calculator.Calculator._setup_logging", lambda self: None)
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)

    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)

    # Create a fake calculation
    class FakeCalc:
        operation = "Add"
        operand1 = "1"
        operand2 = "2"
        result = "3"
        timestamp = datetime(2024, 1, 1, 12, 0, 0)

    calc.history.append(FakeCalc())

    # Act
    df = calc.get_history_dataframe()

    # Assert DataFrame structure
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]

    # Assert one row
    assert len(df) == 1

    # Assert row contents
    row = df.iloc[0]
    assert row["operation"] == "Add"
    assert row["operand1"] == "1"
    assert row["operand2"] == "2"
    assert row["result"] == "3"
    assert row["timestamp"] == FakeCalc.timestamp

# 344
def test_show_history_formats_entries_correctly(monkeypatch, tmp_path):
    # Prevent logging and history loading
    monkeypatch.setattr("app.calculator.Calculator._setup_logging", lambda self: None)
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)

    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)

    # Create a fake calculation
    class FakeCalc:
        operation = "Add"
        operand1 = "1"
        operand2 = "2"
        result = "3"

    calc.history.append(FakeCalc())

    # Act
    history_strings = calc.show_history()

    # Assert
    assert history_strings == ["Add(1, 2) = 3"]

# 371
def test_undo_returns_false_when_stack_empty(monkeypatch, tmp_path):
    # Disable logging + history loading
    monkeypatch.setattr("app.calculator.Calculator._setup_logging", lambda self: None)
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)

    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)

    # Ensure undo stack is empty
    calc.undo_stack.clear()

    # Act
    result = calc.undo()

    # Assert
    assert result is False

# 390
def test_redo_restores_history(monkeypatch, tmp_path):
    # Disable logging + history loading
    monkeypatch.setattr("app.calculator.Calculator._setup_logging", lambda self: None)
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)

    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)

    # Current history
    calc.history = ["current"]

    # Previous history stored in a memento
    previous_history = ["old1", "old2"]
    memento = CalculatorMemento(previous_history.copy())

    # Push memento onto redo stack
    calc.redo_stack.append(memento)

    # Act
    result = calc.redo()

    # Assert redo succeeded
    assert result is True

    # History should now match the memento
    assert calc.history == previous_history

    # undo_stack should contain the state we just replaced
    assert calc.undo_stack[-1].history == ["current"]

# 390
def test_redo_returns_false_when_stack_empty(monkeypatch, tmp_path):
    # Disable logging + history loading
    monkeypatch.setattr("app.calculator.Calculator._setup_logging", lambda self: None)
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)

    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)

    # Ensure redo stack is empty
    calc.redo_stack.clear()

    # Act
    result = calc.redo()

    # Assert
    assert result is False

 