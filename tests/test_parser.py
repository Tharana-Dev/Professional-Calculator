"""Unit tests for the parser module."""

import pytest
from calculator.parser import to_rpn
from calculator.tokenizer import tokenize
from calculator.definitions import Token, TokenType

def parse(expr: str):
    """Helper: tokenize then parse, returning RPN token list."""
    return to_rpn(tokenize(expr))

def test_simple_addition():
    """3 + 4 → RPN is 3 4 +."""
    rpn = parse("3 + 4")
    assert [t.value for t in rpn] == ["3", "4", "+"]

def test_precedence_multiplication_over_addition():
    """3 + 4 * 2 → RPN 3 4 2 * +."""
    rpn = parse("3 + 4 * 2")
    assert [t.value for t in rpn] == ["3", "4", "2", "*", "+"]

def test_precedence_parentheses():
    """(3 + 4) * 2 → RPN 3 4 + 2 *."""
    rpn = parse("(3 + 4) * 2")
    assert [t.value for t in rpn] == ["3", "4", "+", "2", "*"]

def test_power_right_associative():
    """2 ^ 3 ^ 4 → RPN 2 3 4 ^ ^."""
    rpn = parse("2 ^ 3 ^ 4")
    assert [t.value for t in rpn] == ["2", "3", "4", "^", "^"]

def test_unary_minus_at_start():
    """-5 + 3 → RPN 5 UNARY_MINUS 3 +."""
    rpn = parse("-5 + 3")
    assert rpn[0].value == "5"
    assert rpn[1].token_type == TokenType.UNARY_MINUS
    assert rpn[2].value == "3"
    assert rpn[3].token_type == TokenType.ADD

def test_sqrt():
    """√(4) → RPN 4 SQRT."""
    rpn = parse("√(4)")
    assert [t.value for t in rpn] == ["4", "√"]
    assert rpn[1].token_type == TokenType.SQRT

def test_percent_postfix():
    """5% + 2 → RPN 5 PERCENT 2 +."""
    rpn = parse("5% + 2")
    assert rpn[0].value == "5"
    assert rpn[1].token_type == TokenType.PERCENT
    assert rpn[2].value == "2"
    assert rpn[3].token_type == TokenType.ADD

def test_implicit_multiplication():
    """5(3) → Parser sees implicit *, so RPN should be 5 3 *."""
    rpn = parse("5(3)")
    assert [t.value for t in rpn] == ["5", "3", "*"]

def test_mismatched_parens_missing_left():
    """3 + 4) → should raise SyntaxError."""
    with pytest.raises(SyntaxError):
        parse("3 + 4)")

def test_mismatched_parens_missing_right():
    """(3 + 4 → should raise SyntaxError."""
    with pytest.raises(SyntaxError):
        parse("(3 + 4")
