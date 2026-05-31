# D:\python\Portfolio\Calculator\backend\src\calculator\evaluator.py

"""Evaluate an RPN token list and return a Decimal result."""

import math
from decimal import Decimal
from decimal import InvalidOperation
from decimal import Overflow

from .definitions import Token
from .definitions import TokenType


def evaluate_rpn(rpn: list[Token]) -> Decimal:
    """
    Evaluate a list of tokens in Reverse Polish Notation (RPN).

    Args:
        rpn: List of Token objects in postfix order.

    Returns:
        The computed result as a Decimal.

    Raises:
        ArithmeticError: Division by zero, negative square root,
                         non‑integer exponent, or invalid RPN structure.
    """
    stack: list[Decimal] = []

    for token in rpn:
        if token.token_type == TokenType.NUMBER:
            stack.append(Decimal(token.value))

        elif token.token_type == TokenType.ADD:
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)

        elif token.token_type == TokenType.SUBTRACT:
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)

        elif token.token_type == TokenType.MULTIPLY:
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)

        elif token.token_type == TokenType.DIVIDE:
            b = stack.pop()
            a = stack.pop()
            if b == 0:
                raise ArithmeticError("Division by zero")
            stack.append(a / b)

        elif token.token_type == TokenType.POWER:
            exponent = stack.pop()  # Decimal
            base = stack.pop()  # Decimal
            # Check that exponent is an integer value
            if exponent != int(exponent):
                raise ArithmeticError("Exponent must be an integer")
            try:
                stack.append(base ** int(exponent))
            except (OverflowError, InvalidOperation, Overflow):
                raise ArithmeticError("Result too large")

        elif token.token_type == TokenType.UNARY_MINUS:
            operand = stack.pop()
            stack.append(-operand)

        elif token.token_type == TokenType.SQRT:
            operand = stack.pop()
            if operand < 0:
                raise ArithmeticError("Square root of negative number")
            result_float = math.sqrt(float(operand))
            stack.append(Decimal(str(result_float)))

        elif token.token_type == TokenType.PERCENT:
            operand = stack.pop()
            stack.append(operand / Decimal(100))

        else:
            # Should not happen with valid RPN
            raise ArithmeticError(f"Unexpected token type in RPN: {token.token_type}")

    if len(stack) != 1:
        raise ArithmeticError("Invalid RPN: stack does not contain exactly one value")

    return stack[0]
