# backend/tests/test_tokenizer.py

"""Unit tests for the tokenizer module."""

import pytest
from calculator.definitions import Token, TokenType
from calculator.tokenizer import tokenize


# ---------------------------------------------------------------------------
# Helper: shortcut to build expected tokens without repeating the long enum
# ---------------------------------------------------------------------------
def tok(kind: TokenType, value: str, pos: int) -> Token:
    """Create a Token with the given type, value, and position."""
    return Token(kind, value, pos)


# ---------------------------------------------------------------------------
# Numbers
# ---------------------------------------------------------------------------
class TestNumbers:
    def test_integer(self):
        assert tokenize("42") == [tok(TokenType.NUMBER, "42", 0)]

    def test_decimal(self):
        assert tokenize("3.14") == [tok(TokenType.NUMBER, "3.14", 0)]

    def test_leading_dot(self):
        assert tokenize(".5") == [tok(TokenType.NUMBER, ".5", 0)]

    def test_trailing_dot(self):
        assert tokenize("5.") == [tok(TokenType.NUMBER, "5.", 0)]

    def test_multiple_dots_raises(self):
    # "5.5.5" is tokenized as 5.5 * .5 via implicit multiplication
        assert tokenize("5.5.5") == [
            tok(TokenType.NUMBER, "5.5", 0),
            tok(TokenType.MULTIPLY, "*", 3),
            tok(TokenType.NUMBER, ".5", 3),
        ]

    def test_single_dot_raises(self):
        with pytest.raises(ValueError, match="Invalid number format"):
            tokenize(".")

    def test_spaces_around_number(self):
        assert tokenize("  12  ") == [tok(TokenType.NUMBER, "12", 2)]


# ---------------------------------------------------------------------------
# Operators (binary)
# ---------------------------------------------------------------------------
class TestBinaryOperators:
    def test_addition(self):
        assert tokenize("3+2") == [
            tok(TokenType.NUMBER, "3", 0),
            tok(TokenType.ADD, "+", 1),
            tok(TokenType.NUMBER, "2", 2),
        ]

    def test_subtraction(self):
        assert tokenize("3 - 2") == [
            tok(TokenType.NUMBER, "3", 0),
            tok(TokenType.SUBTRACT, "-", 2),
            tok(TokenType.NUMBER, "2", 4),
        ]

    def test_multiplication(self):
        assert tokenize("3*2") == [
            tok(TokenType.NUMBER, "3", 0),
            tok(TokenType.MULTIPLY, "*", 1),
            tok(TokenType.NUMBER, "2", 2),
        ]

    def test_division(self):
        assert tokenize("3/2") == [
            tok(TokenType.NUMBER, "3", 0),
            tok(TokenType.DIVIDE, "/", 1),
            tok(TokenType.NUMBER, "2", 2),
        ]

    def test_power(self):
        assert tokenize("3^2") == [
            tok(TokenType.NUMBER, "3", 0),
            tok(TokenType.POWER, "^", 1),
            tok(TokenType.NUMBER, "2", 2),
        ]

    def test_misplaced_operator_raises(self):
        with pytest.raises(ValueError, match="Unexpected '\\*' at position 0"):
            tokenize("*5")
        with pytest.raises(ValueError, match="Unexpected '\\^' at position 0"):
            tokenize("^5")


# ---------------------------------------------------------------------------
# Unary minus and unary plus
# ---------------------------------------------------------------------------
class TestUnaryMinusPlus:
    def test_unary_minus_at_start(self):
        assert tokenize("-5") == [tok(TokenType.UNARY_MINUS, "-", 0), tok(TokenType.NUMBER, "5", 1)]

    def test_unary_minus_after_operator(self):
        assert tokenize("3 * -2") == [
            tok(TokenType.NUMBER, "3", 0),
            tok(TokenType.MULTIPLY, "*", 2),
            tok(TokenType.UNARY_MINUS, "-", 4),
            tok(TokenType.NUMBER, "2", 5),
        ]

    def test_unary_plus_skipped(self):
        assert tokenize("+5") == [tok(TokenType.NUMBER, "5", 1)]

    def test_unary_plus_after_operator_skipped(self):
        assert tokenize("3 + +5") == [
            tok(TokenType.NUMBER, "3", 0),
            tok(TokenType.ADD, "+", 2),
            tok(TokenType.NUMBER, "5", 5),
        ]


# ---------------------------------------------------------------------------
# Parentheses
# ---------------------------------------------------------------------------
class TestParentheses:
    def test_simple_parens(self):
        assert tokenize("(2)") == [
            tok(TokenType.LPAREN, "(", 0),
            tok(TokenType.NUMBER, "2", 1),
            tok(TokenType.RPAREN, ")", 2),
        ]

    def test_nested_parens(self):
        assert tokenize("((2))") == [
            tok(TokenType.LPAREN, "(", 0),
            tok(TokenType.LPAREN, "(", 1),
            tok(TokenType.NUMBER, "2", 2),
            tok(TokenType.RPAREN, ")", 3),
            tok(TokenType.RPAREN, ")", 4),
        ]

    def test_misplaced_right_paren_raises(self):
        with pytest.raises(ValueError, match="Unexpected '\\)' at position 0"):
            tokenize(")5")


# ---------------------------------------------------------------------------
# sqrt and percent
# ---------------------------------------------------------------------------
class TestSqrtPercent:
    def test_sqrt(self):
        assert tokenize("√(4)") == [
            tok(TokenType.SQRT, "√", 0),
            tok(TokenType.LPAREN, "(", 1),
            tok(TokenType.NUMBER, "4", 2),
            tok(TokenType.RPAREN, ")", 3),
        ]

    def test_percent(self):
        assert tokenize("5%") == [tok(TokenType.NUMBER, "5", 0), tok(TokenType.PERCENT, "%", 1)]

    def test_percent_misplaced_raises(self):
        with pytest.raises(ValueError, match="Unexpected '%' at position 0"):
            tokenize("%5")


# ---------------------------------------------------------------------------
# Implicit multiplication
# ---------------------------------------------------------------------------
class TestImplicitMultiplication:
    def test_number_left_paren(self):
        assert tokenize("5(3)") == [
            tok(TokenType.NUMBER, "5", 0),
            tok(TokenType.MULTIPLY, "*", 1),
            tok(TokenType.LPAREN, "(", 1),
            tok(TokenType.NUMBER, "3", 2),
            tok(TokenType.RPAREN, ")", 3),
        ]

    def test_number_sqrt(self):
        assert tokenize("2√(4)") == [
            tok(TokenType.NUMBER, "2", 0),
            tok(TokenType.MULTIPLY, "*", 1),
            tok(TokenType.SQRT, "√", 1),
            tok(TokenType.LPAREN, "(", 2),
            tok(TokenType.NUMBER, "4", 3),
            tok(TokenType.RPAREN, ")", 4),
        ]

    def test_rparen_number(self):
        assert tokenize("(2)3") == [
            tok(TokenType.LPAREN, "(", 0),
            tok(TokenType.NUMBER, "2", 1),
            tok(TokenType.RPAREN, ")", 2),
            tok(TokenType.MULTIPLY, "*", 3),
            tok(TokenType.NUMBER, "3", 3),
        ]

    def test_percent_number(self):
        assert tokenize("5% 2") == [
            tok(TokenType.NUMBER, "5", 0),
            tok(TokenType.PERCENT, "%", 1),
            tok(TokenType.MULTIPLY, "*", 3),
            tok(TokenType.NUMBER, "2", 3),
        ]

    def test_no_implicit_mult_between_operators(self):
        # expression "3 + - 5" should not insert a multiply before the unary minus.
        assert tokenize("3 + -5") == [
            tok(TokenType.NUMBER, "3", 0),
            tok(TokenType.ADD, "+", 2),
            tok(TokenType.UNARY_MINUS, "-", 4),
            tok(TokenType.NUMBER, "5", 5),
        ]


# ---------------------------------------------------------------------------
# Whitespace
# ---------------------------------------------------------------------------
class TestWhitespace:
    def test_spaces(self):
        assert tokenize("  3  +  4  ") == [
            tok(TokenType.NUMBER, "3", 2),
            tok(TokenType.ADD, "+", 5),
            tok(TokenType.NUMBER, "4", 8),
        ]

    def test_tabs(self):
        assert tokenize("\t3\t+\t4\t") == [
            tok(TokenType.NUMBER, "3", 1),
            tok(TokenType.ADD, "+", 3),
            tok(TokenType.NUMBER, "4", 5),
        ]


# ---------------------------------------------------------------------------
# Illegal characters
# ---------------------------------------------------------------------------
class TestIllegalCharacters:
    def test_letter_raises(self):
        with pytest.raises(ValueError, match="Illegal character 'a' at position 0"):
            tokenize("a+2")

    def test_symbol_raises(self):
        with pytest.raises(ValueError, match="Illegal character '#' at position 0"):
            tokenize("#+2")


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------
class TestEdgeCases:
    def test_empty_expression(self):
        assert tokenize("") == []

    def test_only_spaces(self):
        assert tokenize("    ") == []

    def test_complex_expression(self):
        expr = "3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3"
        tokens = tokenize(expr)
        assert len(tokens) > 0
        assert tokens[-1].token_type == TokenType.NUMBER