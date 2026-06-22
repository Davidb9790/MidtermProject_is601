import pytest
from decimal import Decimal
from app.calculation import Calculation
from app.exceptions import OperationError

def test_calculate_raises_operation_error_on_invalid_operation_execution():
    # Create Calculation instance WITHOUT running __post_init__
    calc = object.__new__(Calculation)
    calc.operation = "Power"
    calc.operand1 = Decimal("2")
    calc.operand2 = Decimal("1000000")

    with pytest.raises(OperationError, match="Calculation failed"):
        calc.calculate()

def test_str_representation():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    s = str(calc)
    assert "Addition(2, 3) = 5" in s

def test_repr_representation_hits_return_line():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    r = repr(calc)
    assert "Calculation(operation='Addition'" in r
