# D:\python\Portfolio\Calculator\backend\src\calculator\parser.py

"""Convert an infix token list into Reverse Polish Notation (RPN)."""

from .definitions import OPERATORS
from .definitions import Token
from .definitions import TokenType


def to_rpn(tokens: list[Token]) -> list[Token]:
    """
    Transform a list of tokens in infix order into RPN using the shunting-yard algorithm.
    Args:
        tokens: List of Token objects from the tokenizer.
    Returns:
        A list of Token objects in postfix (RPN) order.
    Raises:
        SyntaxError: If the expression contains mismatched parentheses.
    """

    output: list[Token] = []
    operator_stack: list[Token] = []

    for token in tokens:
        if token.token_type == TokenType.NUMBER:
            output.append(token)

        elif token.token_type == TokenType.LPAREN:
            operator_stack.append(token)

        elif token.token_type == TokenType.RPAREN:
            while operator_stack and operator_stack[-1].token_type != TokenType.LPAREN:
                output.append(operator_stack.pop())
            if not operator_stack:
                raise SyntaxError("Mismatched parentheses: missing '('")
            operator_stack.pop()  # discard the '('

        elif token.token_type in OPERATORS:
            # Prefix unary operators (UNARY_MINUS, SQRT) must NOT pop other operators.
            # They bind directly to the following operand.
            if token.token_type in (TokenType.UNARY_MINUS, TokenType.SQRT):
                operator_stack.append(token)
                continue

            current_op = OPERATORS[token.token_type]

            while operator_stack:
                top_token = operator_stack[-1]
                if top_token.token_type not in OPERATORS:
                    break
                top_op = OPERATORS[top_token.token_type]

                if (top_op.precedence > current_op.precedence) or (
                    top_op.precedence == current_op.precedence
                    and top_op.associativity == "left"
                ):
                    output.append(operator_stack.pop())
                else:
                    break

            operator_stack.append(token)

        else:
            # Unknown token (should not happen with our tokenizer)
            pass

    # Check for unmatched '('
    for token in operator_stack:
        if token.token_type == TokenType.LPAREN:
            raise SyntaxError("Mismatched parentheses: missing ')'")

    while operator_stack:
        output.append(operator_stack.pop())

    return output
