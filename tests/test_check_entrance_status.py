"""
Tests for events.check_entrance_status().

Strategy:
- Monkeypatch events.E1_entrance_schedule / E1_thirdPartyOption directly
  (these module-level globals are what check_entrance_status() reads)
- Monkeypatch relay.lock_unlock_entrance_one to capture calls
- Monkeypatch relay.lock_unlock_entrance_two so E2 calls don't error
- Use @freeze_time + monkeypatch events.tzlocal to control time in verify_datetime
"""

import pytest
from datetime import timezone
from freezegun import freeze_time

import events
import relay

# A 24/7 schedule that is always open
_ALWAYS_OPEN = {
    "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1",
    "starttime": "00:00",
    "endtime": "24:00",
}

# An extremely narrow window (23:00–23:01) — closed at noon UTC
_CLOSED_SCHEDULE = {
    "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1",
    "starttime": "23:00",
    "endtime": "23:01",
}


@freeze_time("2024-03-15 12:00:00")
def test_closed_entrance_schedule_locks_entrance(monkeypatch):
    monkeypatch.setattr(events, "tzlocal", lambda: timezone.utc)
    monkeypatch.setattr(events, "E1_entrance_schedule", _CLOSED_SCHEDULE)
    monkeypatch.setattr(events, "E1_thirdPartyOption", "N.A.")
    monkeypatch.setattr(events, "E2_entrance_schedule", _CLOSED_SCHEDULE)
    monkeypatch.setattr(events, "E2_thirdPartyOption", "N.A.")

    e1_calls = []
    monkeypatch.setattr(relay, "lock_unlock_entrance_one",
                        lambda tpo, unlock: e1_calls.append(unlock))
    monkeypatch.setattr(relay, "lock_unlock_entrance_two",
                        lambda tpo, unlock: None)

    events.check_entrance_status()

    assert len(e1_calls) == 1
    assert e1_calls[0] is False, \
        "Closed schedule (23:00–23:01) at noon UTC must lock entrance (unlock=False)"


@freeze_time("2024-03-15 12:00:00")
def test_open_entrance_schedule_unlocks_entrance(monkeypatch):
    monkeypatch.setattr(events, "tzlocal", lambda: timezone.utc)
    monkeypatch.setattr(events, "E1_entrance_schedule", _ALWAYS_OPEN)
    monkeypatch.setattr(events, "E1_thirdPartyOption", "N.A.")
    monkeypatch.setattr(events, "E2_entrance_schedule", _CLOSED_SCHEDULE)
    monkeypatch.setattr(events, "E2_thirdPartyOption", "N.A.")

    e1_calls = []
    monkeypatch.setattr(relay, "lock_unlock_entrance_one",
                        lambda tpo, unlock: e1_calls.append(unlock))
    monkeypatch.setattr(relay, "lock_unlock_entrance_two",
                        lambda tpo, unlock: None)

    events.check_entrance_status()

    assert len(e1_calls) == 1
    assert e1_calls[0] is True, \
        "Open schedule (00:00–24:00) at noon UTC must unlock entrance (unlock=True)"
