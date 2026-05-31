"""Integration tests – full pipeline from expression string to result."""

import pytest
from decimal import Decimal
from calculator.calculator import evaluate


def test_order_of_operations():
    """3 + 4 * 2 = 11 (precedence)."""
    result = evaluate("3 + 4 * 2")
    assert result.success is True
    assert result.value == Decimal("11")


def test_square_root():
    """√(9) + 2 = 5."""
    result = evaluate("√(9) + 2")
    assert result.success is True
    assert result.value == Decimal("5")


def test_implicit_multiplication():
    """-5(3) = -15."""
    result = evaluate("-5(3)")
    assert result.success is True
    assert result.value == Decimal("-15")


def test_right_associativity_power():
    """2 ^ 3 ^ 2 = 512."""
    result = evaluate("2 ^ 3 ^ 2")
    assert result.success is True
    assert result.value == Decimal("512")


def test_percentage():
    """10% + 3 = 3.1."""
    result = evaluate("10% + 3")
    assert result.success is True
    assert result.value == Decimal("3.1")


@pytest.mark.parametrize("expr, expected", [
    ("2 + 3 * 4", Decimal("14")),
    ("(2 + 3) * 4", Decimal("20")),
    ("√(16)", Decimal("4")),
    ("-5 + 3", Decimal("-2")),
    ("5% * 200", Decimal("10")),
])
def test_various_scenarios(expr, expected):
    """Batch of mixed scenarios."""
    result = evaluate(expr)
    assert result.value == expected