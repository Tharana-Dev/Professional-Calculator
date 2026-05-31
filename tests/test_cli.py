"""
Unit tests for the CLI helper logic.
"""

from calculator.cli import _is_critical_error

def test_is_critical_error_normal():
    """Verify that syntax errors are not classified as critical."""
    assert _is_critical_error("Illegal character '&'") is False
    assert _is_critical_error("Mismatched parentheses") is False

def test_is_critical_error_div_zero():
    """Verify division by zero is critical."""
    assert _is_critical_error("Division by zero") is True

def test_is_critical_error_overflow():
    """Verify result overflow is critical."""
    # Matches the 'too large' keyword from the backend
    assert _is_critical_error("Result too large") is True

def test_is_critical_error_system():
    """Verify unexpected system errors are critical."""
    assert _is_critical_error("Unexpected system error: database down") is True

def test_is_critical_error_negative_sqrt():
    """Verify negative square root is handled as a normal error."""
    assert _is_critical_error("Square root of negative number") is False

def test_is_critical_error_empty():
    """Verify empty strings return False."""
    assert _is_critical_error("") is False
