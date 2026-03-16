"""
Integration test for eventsMod.update() log-file persistence.

Tests the overflow-truncation path: when the JSON file contains more than
MAX_JSON_LENGTH entries, clear_file_storage() deletes the first half before
update() appends the new event.

This is a real data-loss path (first MAX_JSON_LENGTH//2 events are permanently
dropped) that has never been tested.  The test exercises the full call chain:
  update() → clear_file_storage() → file rewrite → append new event
"""

import json
import threading
import pytest

import eventsMod


@pytest.fixture
def log_file(tmp_path):
    """Create a writable log file in tmp_path and return its path string."""
    f = tmp_path / "test_log.json"
    f.write_text("[]")
    return str(f)


def test_update_truncates_first_half_when_over_max_length(log_file):
    """
    When the log file has MAX_JSON_LENGTH + 1 events, calling update() must:
      1. Detect the overflow in clear_file_storage()
      2. Delete the first MAX_JSON_LENGTH // 2 events
      3. Append the new event to what remains

    Expected final count: MAX_JSON_LENGTH - MAX_JSON_LENGTH // 2 + 1
    (i.e. kept second half of original + 1 new event)
    """
    max_len = eventsMod.MAX_JSON_LENGTH
    assert max_len is not None and max_len > 1, \
        "MAX_JSON_LENGTH must be set (check config.json archivedMAXlength)"

    # Write max_len + 1 events so the overflow condition triggers
    initial_events = [{"id": i} for i in range(max_len + 1)]
    with open(log_file, "w") as f:
        json.dump(initial_events, f)

    new_event = {"id": "new", "type": "test_overflow"}
    lock = threading.Lock()
    eventsMod.update(log_file, lock, new_event)

    with open(log_file) as f:
        result = json.load(f)

    half = int(max_len / 2)
    expected_count = (max_len + 1) - half + 1  # initial - deleted first half + new event
    assert len(result) == expected_count, (
        f"Expected {expected_count} events after overflow truncation "
        f"(deleted first {half} of {max_len + 1}), got {len(result)}"
    )

    # The new event must be the last one
    assert result[-1] == new_event, "New event must be appended after truncation"

    # The first retained event should be at index `half` of the original list
    assert result[0] == initial_events[half], (
        f"First retained event must be original[{half}] after deleting first {half}"
    )
