import builtins
import pytest

from app.calculator_repl import calculator_repl
from app.exceptions import OperationError, ValidationError


# Utility: capture printed output
class PrintCapture:
    def __init__(self):
        self.lines = []

    def __call__(self, *args, **kwargs):
        self.lines.append(" ".join(str(a) for a in args))


# Utility: fake calculator object for REPL tests
class FakeCalc:
    def __init__(self):
        self.history = ["Add(1, 2) = 3"]
        self.config = None  # REPL expects this attribute

    def show_history(self):
        return self.history

    def clear_history(self):
        self.history = []

    def undo(self):
        return True

    def redo(self):
        return True

    def save_history(self):
        pass

    def load_history(self):
        pass

    def perform_operation(self, a, b):
        return 999  # predictable fake result

    def set_operation(self, op):
        pass

    def add_observer(self, obs):
        pass



# ---------------------------------------------------------
# TESTS
# ---------------------------------------------------------

def test_repl_help(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["help", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: FakeCalc())

    calculator_repl()

    assert any("Available commands:" in line for line in printed.lines)


def test_repl_unknown_command(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["foobar", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: FakeCalc())

    calculator_repl()

    assert any("Unknown command: 'foobar'" in line for line in printed.lines)


def test_repl_history(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["history", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: FakeCalc())

    calculator_repl()

    assert any("Add(1, 2) = 3" in line for line in printed.lines)


def test_repl_clear(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["clear", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    calc = FakeCalc()
    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: calc)

    calculator_repl()

    assert calc.history == []


def test_repl_undo(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["undo", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    calc = FakeCalc()
    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: calc)

    calculator_repl()

    assert any("Operation undone" in line for line in printed.lines)



def test_repl_redo(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["redo", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    calc = FakeCalc()
    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: calc)

    calculator_repl()

    assert any("Operation redone" in line for line in printed.lines)



def test_repl_add_cancel(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["add", "cancel", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: FakeCalc())

    calculator_repl()

    assert any("Operation cancelled" in line for line in printed.lines)


def test_repl_add_full(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["add", "5", "7", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: FakeCalc())

    calculator_repl()

    assert any("Result: 999" in line for line in printed.lines)

# 63
def test_repl_history_empty(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    # Simulate: history → exit
    inputs = iter(["history", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # Fake calculator with EMPTY history
    class EmptyHistoryCalc(FakeCalc):
        def __init__(self):
            self.history = []
            self.config = None

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: EmptyHistoryCalc())

    calculator_repl()

    # Assert the exact line at 63 was printed
    assert any("No calculations in history" in line for line in printed.lines)



    #89
def test_repl_redo_nothing_to_redo(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    # redo → exit
    inputs = iter(["redo", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # Fake calculator where redo() returns False
    class NoRedoCalc(FakeCalc):
        def redo(self):
            return False

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: NoRedoCalc())

    calculator_repl()

    # Assert the exact line at 89 was printed
    assert any("Nothing to redo" in line for line in printed.lines)

    # 94- 99
def test_repl_save_error(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    # save → exit
    inputs = iter(["save", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # Fake calculator where save_history() raises an exception
    class SaveErrorCalc(FakeCalc):
        def save_history(self):
            raise Exception("disk error")

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: SaveErrorCalc())

    calculator_repl()

    # Assert the error message printed
    assert any("Error saving history: disk error" in line for line in printed.lines)

    # 96
def test_repl_save_success(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    # save → exit
    inputs = iter(["save", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # Fake calculator where save_history() succeeds
    class SaveSuccessCalc(FakeCalc):
        def save_history(self):
            return None  # no exception = success

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: SaveSuccessCalc())

    calculator_repl()

    # Assert the success message printed
    assert any("History saved successfully" in line for line in printed.lines)

    # 103
def test_repl_load_success(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["load", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    class LoadSuccessCalc(FakeCalc):
        def load_history(self):
            return None  # no exception

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: LoadSuccessCalc())

    calculator_repl()

    assert any("History loaded successfully" in line for line in printed.lines)

    # 106
def test_repl_load_error(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    inputs = iter(["load", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    class LoadErrorCalc(FakeCalc):
        def load_history(self):
            raise Exception("file missing")

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: LoadErrorCalc())

    calculator_repl()

    assert any("Error loading history: file missing" in line for line in printed.lines)

    # 135 - 140
def test_repl_operation_cancel_second_number(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    # Input sequence:
    # 1. "add" → enter operation block
    # 2. "5" → first number
    # 3. "cancel" → triggers lines 135–140
    # 4. "exit" → end REPL
    inputs = iter(["add", "5", "cancel", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # Patch Calculator to use FakeCalc
    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: FakeCalc())

    # Patch OperationFactory so it doesn't crash before reaching second-number cancel
    monkeypatch.setattr(
        "app.calculator_repl.OperationFactory.create_operation",
        lambda cmd: None
    )

    calculator_repl()

    assert any("Operation cancelled" in line for line in printed.lines)



    # 81
def test_repl_undo_nothing_to_undo(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    # undo → exit
    inputs = iter(["undo", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # FakeCalc where undo() returns False
    class NoUndoCalc(FakeCalc):
        def undo(self):
            return False

    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: NoUndoCalc())

    calculator_repl()

    assert any("Nothing to undo" in line for line in printed.lines)

    # 135 - 137
def test_repl_operation_unexpected_exception(monkeypatch):
    printed = PrintCapture()
    monkeypatch.setattr(builtins, "print", printed)

    # Inputs:
    inputs = iter(["add", "5", "10", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # FakeCalc that raises an unexpected exception
    class BoomCalc(FakeCalc):
        def perform_operation(self, a, b):
            raise RuntimeError("boom")  # <-- IMPORTANT: not OperationError

    # Patch Calculator to use BoomCalc
    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: BoomCalc())

    # Patch OperationFactory so it doesn't crash before perform_operation
    monkeypatch.setattr(
        "app.calculator_repl.OperationFactory.create_operation",
        lambda cmd: None
    )

    calculator_repl()

    assert any("Unexpected error: boom" in line for line in printed.lines)

