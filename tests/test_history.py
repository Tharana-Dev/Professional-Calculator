import pytest
import json
from pathlib import Path
from collections import deque
from calculator import history
from calculator.definitions import HistoryRecord

# Redirect storage to a temporary file for testing
TEST_FILE = Path("_test_history.json")

@pytest.fixture(autouse=True)
def setup_teardown():
    """Ensures each test uses a clean test file and resets memory."""
    history.HISTORY_FILE = TEST_FILE
    history.clear_history() 
    yield
    if TEST_FILE.exists():
        TEST_FILE.unlink()

def test_add_and_get_history():
    """1. Basic add and retrieve functionality."""
    rec = HistoryRecord(expression="2+2", result="4.0", timestamp="2023-01-01")
    history.add_record(rec)
    results = history.get_history()
    assert len(results) == 1
    assert results[0].expression == "2+2"

def test_history_limit():
    """2. Verify only the last 10 records are kept (sliding window)."""
    for i in range(15):
        history.add_record(HistoryRecord(f"{i}+1", str(i+1), "t"))
    results = history.get_history()
    assert len(results) == 10
    assert results[0].expression == "5+1"  # 0 through 4 should be gone

def test_clear_history():
    """3. Verify memory and file cleanup."""
    history.add_record(HistoryRecord("1+1", "2", "t"))
    history.clear_history()
    assert len(history.get_history()) == 0
    assert not TEST_FILE.exists()

def test_persistence_load():
    """4. Verify data survives a manual reload from disk."""
    rec = HistoryRecord("10/2", "5.0", "now")
    history.add_record(rec)
    reloaded = history._load_history()
    assert len(reloaded) == 1
    assert reloaded[0].expression == "10/2"

def test_corrupt_json_handling():
    """5. Verify resilience against malformed JSON syntax."""
    with open(TEST_FILE, "w") as f:
        f.write("{ invalid json ...")
    reloaded = history._load_history()
    assert len(reloaded) == 0

def test_empty_file_handling():
    """6. Verify resilience against 0-byte files."""
    TEST_FILE.touch()
    reloaded = history._load_history()
    assert len(reloaded) == 0

def test_schema_mismatch_handling():
    """7. Verify resilience against valid JSON with wrong fields."""
    with open(TEST_FILE, "w") as f:
        json.dump([{"wrong_field": "data"}], f)
    reloaded = history._load_history()
    assert len(reloaded) == 0

def test_get_history_integrity():
    """8. Verify get_history() returns a copy, not the internal deque."""
    history.add_record(HistoryRecord("1+1", "2", "t"))
    results = history.get_history()
    results.clear()
    assert len(history.get_history()) == 1

def test_deque_initialization():
    """9. Verify internal history is initialized as a deque."""
    assert isinstance(history._history, deque)

def test_file_writing_format():
    """10. Verify JSON is written with proper indentation/structure."""
    history.add_record(HistoryRecord("2+2", "4", "t"))
    content = TEST_FILE.read_text()
    assert '"expression": "2+2"' in content
    assert '"result": "4"' in content

def test_max_capacity_disk_check():
    """11. Verify the physical file also only contains 10 records."""
    for i in range(12):
        history.add_record(HistoryRecord(str(i), "res", "t"))
    with open(TEST_FILE, "r") as f:
        data = json.load(f)
    assert len(data) == 10
