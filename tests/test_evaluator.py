import pytest
from decimal import Decimal
from calculator.evaluator import evaluate_rpn
from calculator.definitions import Token, TokenType

# --- Basic Success Tests ---

def test_single_number():
    rpn = [Token(TokenType.NUMBER, "42", 0)]
    assert evaluate_rpn(rpn) == Decimal("42")

def test_simple_addition():
    rpn = [
        Token(TokenType.NUMBER, "3", 0),
        Token(TokenType.NUMBER, "4", 0),
        Token(TokenType.ADD, "+", 0)
    ]
    assert evaluate_rpn(rpn) == Decimal("7")

def test_simple_subtraction():
    rpn = [
        Token(TokenType.NUMBER, "5", 0),
        Token(TokenType.NUMBER, "3", 0),
        Token(TokenType.SUBTRACT, "-", 0)
    ]
    assert evaluate_rpn(rpn) == Decimal("2")

def test_simple_multiplication():
    rpn = [
        Token(TokenType.NUMBER, "4", 0),
        Token(TokenType.NUMBER, "7", 0),
        Token(TokenType.MULTIPLY, "*", 0)
    ]
    assert evaluate_rpn(rpn) == Decimal("28")

def test_simple_division():
    rpn = [
        Token(TokenType.NUMBER, "10", 0),
        Token(TokenType.NUMBER, "4", 0),
        Token(TokenType.DIVIDE, "/", 0)
    ]
    assert evaluate_rpn(rpn) == Decimal("2.5")

def test_power():
    rpn = [
        Token(TokenType.NUMBER, "2", 0),
        Token(TokenType.NUMBER, "3", 0),
        Token(TokenType.POWER, "^", 0)
    ]
    assert evaluate_rpn(rpn) == Decimal("8")

# --- Unary Operators ---

def test_unary_minus():
    rpn = [Token(TokenType.NUMBER, "5", 0), Token(TokenType.UNARY_MINUS, "-", 0)]
    assert evaluate_rpn(rpn) == Decimal("-5")

def test_sqrt():
    rpn = [Token(TokenType.NUMBER, "9", 0), Token(TokenType.SQRT, "√", 0)]
    assert evaluate_rpn(rpn) == Decimal("3")

def test_percent():
    rpn = [Token(TokenType.NUMBER, "50", 0), Token(TokenType.PERCENT, "%", 0)]
    assert evaluate_rpn(rpn) == Decimal("0.5")

# --- Error Tests (Using pytest.raises) ---

def test_division_by_zero():
    rpn = [Token(TokenType.NUMBER, "5", 0), Token(TokenType.NUMBER, "0", 0), Token(TokenType.DIVIDE, "/", 0)]
    with pytest.raises(ArithmeticError, match="Division by zero"):
        evaluate_rpn(rpn)

def test_power_non_integer_exponent():
    rpn = [Token(TokenType.NUMBER, "4", 0), Token(TokenType.NUMBER, "0.5", 0), Token(TokenType.POWER, "^", 0)]
    with pytest.raises(ArithmeticError, match="Exponent must be an integer"):
        evaluate_rpn(rpn)

def test_sqrt_negative():
    rpn = [Token(TokenType.NUMBER, "-4", 0), Token(TokenType.SQRT, "√", 0)]
    with pytest.raises(ArithmeticError, match="Square root of negative number"):
        evaluate_rpn(rpn)

# --- Complex End-to-End ---

def test_complex_expression():
    # (3 + 4) * 2 ^ 3 => 3 4 + 2 3 ^ *
    rpn = [
        Token(TokenType.NUMBER, "3", 0),
        Token(TokenType.NUMBER, "4", 0),
        Token(TokenType.ADD, "+", 0),
        Token(TokenType.NUMBER, "2", 0),
        Token(TokenType.NUMBER, "3", 0),
        Token(TokenType.POWER, "^", 0),
        Token(TokenType.MULTIPLY, "*", 0)
    ]
    assert evaluate_rpn(rpn) == Decimal("56")
