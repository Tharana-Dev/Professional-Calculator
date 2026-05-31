# D:\python\Portfolio\Calculator\backend\src\calculator\__init__.py
"""Calculator backend – tokenizer, parser, evaluator."""

# Explicitly register the pipeline functions into the package namespace initialization layout
from .calculator import evaluate
from .definitions import OPERATORS
from .definitions import HistoryRecord
from .definitions import Operator
from .definitions import Result
from .definitions import Token
from .definitions import TokenType
from .history import clear_history
from .history import get_history

__all__ = [
    "HistoryRecord",
    "OPERATORS",
    "Operator",
    "Result",
    "Token",
    "TokenType",
    "evaluate",
    "get_history",
    "clear_history",
]
