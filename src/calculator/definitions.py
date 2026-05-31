# D:\python\Portfolio\Calculator\backend\src\calculator\definitions.py

"""Core data types and operator table for the calculator."""

from decimal import Decimal
from enum import Enum
from enum import auto
from typing import Literal
from typing import NamedTuple
from typing import Optional

__all__ = [
    "TokenType",
    "Token",
    "Operator",
    "Result",
    "HistoryRecord",
    "OPERATORS",
]


class TokenType(Enum):
    """Kinds of tokens that can appear in a calculator expression."""

    NUMBER = auto()
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    POWER = auto()
    UNARY_MINUS = auto()
    SQRT = auto()
    PERCENT = auto()
    LPAREN = auto()
    RPAREN = auto()


class Token(NamedTuple):
    """
    A single token produced by the tokenizer.
    Attributes:
        token_type: The kind of token.
        value: The original text that created this token.
        pos: Character index where this token starts in the expression.
    """

    token_type: TokenType
    value: str
    pos: int


class Operator(NamedTuple):
    """
    Precedence and associativity of an operator.
    Attributes:
        precedence: Higher values bind more tightly.
        associativity: 'left' or 'right'.
    """

    precedence: int
    associativity: Literal["left", "right"]


class Result(NamedTuple):
    """
    Container for calculation outcome.
    Attributes:
        success: True if calculation produced a value
        value: The computed Decimal result, or None
        error: An error message string, or None
    """

    success: bool
    value: Optional[Decimal] = None
    error: Optional[str] = None


class HistoryRecord(NamedTuple):
    """
    A record of one calculation stored in history.
    Attributes:
        expression: The original input string.
        result: The final displayed result or error message.
        timestamp: ISO-8601 formatted time when the record was created.
    """

    expression: str
    result: str
    timestamp: str


# Lookup table: TokenType → Operator metadata
# "left" / "right" indicates associativity for binary operators.
# For unary operators:
#   - "right" for prefix (√, unary_minus) — binds to what follows
#   - "left" for postfix (%) — binds to what precedes
OPERATORS: dict[TokenType, Operator] = {
    TokenType.ADD: Operator(1, "left"),
    TokenType.SUBTRACT: Operator(1, "left"),
    TokenType.MULTIPLY: Operator(2, "left"),
    TokenType.DIVIDE: Operator(2, "left"),
    TokenType.POWER: Operator(3, "right"),
    TokenType.UNARY_MINUS: Operator(4, "right"),  # prefix
    TokenType.SQRT: Operator(5, "right"),  # prefix
    TokenType.PERCENT: Operator(6, "left"),  # postfix, highest precedence
}
