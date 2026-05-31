"""
FACADE: calculator.py
The single entry point for the CLI, GUI, and API.
Orchestrates: Tokenize -> Parse -> Evaluate -> History Logging.
"""

import datetime

from .definitions import HistoryRecord
from .definitions import Result
from .evaluator import evaluate_rpn
from .history import add_record
from .parser import to_rpn
from .tokenizer import tokenize


def evaluate(expression: str) -> Result:
    """
    Takes a raw string, runs it through the full pipeline,
    records it in history, and returns a Result namedtuple.
    """
    timestamp = datetime.datetime.now().isoformat()

    try:
        # 1. Tokenize the input string into parts
        tokens = tokenize(expression)

        # 2. Convert tokens to Reverse Polish Notation (Shunting-yard)
        rpn = to_rpn(tokens)

        # 3. Calculate the mathematical result from RPN
        raw_result = evaluate_rpn(rpn)

        # 4. Final value (already a Decimal from evaluator)
        final_value = raw_result
        result_str = str(final_value)

        # 5. Success Logging: Create and store the history record
        record = HistoryRecord(
            expression=expression,
            result=result_str,
            timestamp=timestamp,
        )
        add_record(record)

        return Result(success=True, value=final_value, error=None)

    except (ValueError, SyntaxError, ArithmeticError) as e:
        # 6. Error Mapping: Convert any internal exception into a Result
        error_msg = str(e)

        # 7. Error Logging: Even failures get recorded in history
        record = HistoryRecord(
            expression=expression,
            result=f"Error: {error_msg}",
            timestamp=timestamp,
        )
        add_record(record)

        return Result(success=False, value=None, error=error_msg)

    except Exception as e:
        # 8. Catch-all for unexpected system crashes
        error_msg = f"Unexpected system error: {str(e)}"
        return Result(success=False, value=None, error=error_msg)
