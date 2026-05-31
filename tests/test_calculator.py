"""Unit tests for the calculator facade – error handling and history logging."""

import pytest
from decimal import Decimal
from calculator.calculator import evaluate
from calculator.history import get_history, clear_history


@pytest.fixture(autouse=True)
def clean_state():
    """Automatically clears history before every test."""
    clear_history()


def test_evaluate_success():
    """Valid expression returns successful Result with correct Decimal."""
    result = evaluate("2 + 2")
    assert result.success is True
    assert result.value == Decimal("4")
    assert result.error is None


def test_evaluate_tokenizer_error():
    """Illegal characters caught and returned as Result(success=False)."""
    result = evaluate("2 + &")
    assert result.success is False
    assert "illegal" in result.error.lower()
    assert result.value is None


def test_evaluate_parser_error():
    """Mismatched parentheses caught."""
    result = evaluate("2 + )")
    assert result.success is False
    assert "unexpected ')'" in result.error.lower()   # tokenizer catches this

def test_evaluate_evaluator_error():
    """Division by zero caught."""
    result = evaluate("5 / 0")
    assert result.success is False
    assert "division by zero" in result.error.lower()


def test_history_recorded_on_success():
    """Facade sends successful calculations to history."""
    evaluate("10 * 5")
    history = get_history()
    assert len(history) == 1
    assert history[0].expression == "10 * 5"
    assert history[0].result == "50"


def test_history_recorded_on_failure():
    """Failed attempts logged with 'Error:' prefix."""
    evaluate("invalid_input")
    history = get_history()
    assert len(history) == 1
    assert history[0].expression == "invalid_input"
    assert history[0].result.startswith("Error:")