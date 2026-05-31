# D:\python\Portfolio\Calculator\backend\src\calculator\history.py

"""Persistent calculation history – last 10 records stored in JSON."""

import json
from collections import deque
from pathlib import Path

from .definitions import HistoryRecord

# The history file is stored in the current working directory
HISTORY_FILE = Path("calculator_history.json")


def _load_history() -> deque[HistoryRecord]:
    """
    Internal helper to load history from disk.
    Returns an empty deque if the file is missing, empty, or corrupted.
    """
    # Check if file exists and has content (handles empty 0-byte files)
    if not HISTORY_FILE.exists() or HISTORY_FILE.stat().st_size == 0:
        return deque(maxlen=10)

    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)

        # Reconstruct HistoryRecord objects (handles TypeError/KeyError if keys are wrong)
        records = [HistoryRecord(**item) for item in data]
        return deque(records, maxlen=10)

    except (json.JSONDecodeError, TypeError, KeyError):
        # Fallback for malformed JSON or schema mismatches
        return deque(maxlen=10)


def _save_history() -> None:
    """Internal helper to persist the current _history deque to disk."""
    # Convert NamedTuple records to dictionaries for JSON serialization
    data = [record._asdict() for record in _history]
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# Initialize the in-memory history when the module is imported
_history = _load_history()


def add_record(record: HistoryRecord) -> None:
    """Store a calculation record and persist to disk."""
    _history.append(record)
    _save_history()


def get_history() -> list[HistoryRecord]:
    """Return all stored records as a list (most recent last)."""
    return list(_history)


def clear_history() -> None:
    """Delete all stored history from memory and disk."""
    _history.clear()
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
