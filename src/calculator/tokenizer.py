# D:\python\Portfolio\Calculator\backend\src\calculator\tokenizer.py

"""Convert a raw string expression into a list of Token objects."""

from .definitions import Token
from .definitions import TokenType


def tokenize(expr: str) -> list[Token]:
    """
    Convert a raw expression string into a list of tokens.

    Args:
        expr: The arithmetic expression, e.g. "3 + 4 * (2 - 1) / √(9)".

    Returns:
        A list of Token objects in the order they appear.

    Raises:
        ValueError: If an illegal character or malformed number is encountered.
    """
    tokens: list[Token] = []
    i = 0
    n = len(expr)
    expect_operand = True

    while i < n:
        ch = expr[i]

        # Skip whitespace
        if ch.isspace():
            i += 1
            continue

        # --- Number ---
        if ch.isdigit() or ch == ".":
            start_pos = i
            num_str: list[str] = []
            seen_dot = False

            while i < n and (expr[i].isdigit() or (expr[i] == "." and not seen_dot)):
                if expr[i] == ".":
                    seen_dot = True
                num_str.append(expr[i])
                i += 1

            num_value = "".join(num_str)
            if num_value == ".":
                raise ValueError(f"Invalid number format at position {start_pos}")

            tokens.append(Token(TokenType.NUMBER, num_value, start_pos))
            expect_operand = False

            # Implicit multiplication check (skip whitespace to look ahead)
            temp_i = i
            while temp_i < n and expr[temp_i].isspace():
                temp_i += 1
            if temp_i < n and (expr[temp_i].isdigit() or expr[temp_i] in ".(√"):
                tokens.append(Token(TokenType.MULTIPLY, "*", temp_i))
                expect_operand = True

        # --- Operators, parentheses, sqrt, percent ---
        else:
            if ch == "(":
                if not expect_operand:
                    raise ValueError(f"Unexpected '(' at position {i}")
                tokens.append(Token(TokenType.LPAREN, ch, i))
                expect_operand = True
                i += 1
            elif ch == ")":
                if expect_operand:
                    raise ValueError(f"Unexpected ')' at position {i}")
                tokens.append(Token(TokenType.RPAREN, ch, i))
                expect_operand = False
                i += 1

                # Implicit multiplication check (skip whitespace to look ahead)
                temp_i = i
                while temp_i < n and expr[temp_i].isspace():
                    temp_i += 1
                if temp_i < n and (expr[temp_i].isdigit() or expr[temp_i] in ".(√"):
                    tokens.append(Token(TokenType.MULTIPLY, "*", temp_i))
                    expect_operand = True

            elif ch == "√":
                if not expect_operand:
                    raise ValueError(f"Unexpected '√' at position {i}")
                tokens.append(Token(TokenType.SQRT, ch, i))
                expect_operand = True
                i += 1
            elif ch == "%":
                if expect_operand:
                    raise ValueError(f"Unexpected '%' at position {i}")
                tokens.append(Token(TokenType.PERCENT, ch, i))
                expect_operand = False
                i += 1

                # Implicit multiplication check (skip whitespace to look ahead)
                temp_i = i
                while temp_i < n and expr[temp_i].isspace():
                    temp_i += 1
                if temp_i < n and (expr[temp_i].isdigit() or expr[temp_i] in ".(√"):
                    tokens.append(Token(TokenType.MULTIPLY, "*", temp_i))
                    expect_operand = True

            elif ch == "+":
                if expect_operand:  # skip unary +
                    i += 1
                    continue
                tokens.append(Token(TokenType.ADD, ch, i))
                expect_operand = True
                i += 1

            elif ch == "*":
                if expect_operand:
                    raise ValueError(f"Unexpected '*' at position {i}")
                tokens.append(Token(TokenType.MULTIPLY, ch, i))
                expect_operand = True
                i += 1

            elif ch == "/":
                if expect_operand:
                    raise ValueError(f"Unexpected '/' at position {i}")
                tokens.append(Token(TokenType.DIVIDE, ch, i))
                expect_operand = True
                i += 1

            elif ch == "^":
                if expect_operand:
                    raise ValueError(f"Unexpected '^' at position {i}")
                tokens.append(Token(TokenType.POWER, ch, i))
                expect_operand = True
                i += 1

            elif ch == "-":
                if expect_operand:
                    tokens.append(Token(TokenType.UNARY_MINUS, ch, i))
                else:
                    tokens.append(Token(TokenType.SUBTRACT, ch, i))
                expect_operand = True
                i += 1

            else:
                raise ValueError(f"Illegal character '{ch}' at position {i}")

    return tokens
