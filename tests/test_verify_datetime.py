"""
Tests for events.verify_datetime().

Uses freezegun to control "now".  All frozen times use UTC because the test
runner in CI (Ubuntu) defaults to UTC.  The RRULE DTSTARTs also use UTC (Z
suffix) to avoid timezone-induced date mismatches.
"""

import pytest
from datetime import timezone
from freezegun import freeze_time

import events  # conftest.py pre-mocked pigpio so this import is safe


@pytest.fixture(autouse=True)
def force_utc(monkeypatch):
    """
    Force events.tzlocal() to return UTC so freeze_time frozen times match the
    schedule strings exactly, regardless of what timezone the machine is in.
    """
    monkeypatch.setattr("events.tzlocal", lambda: timezone.utc)

# ---------------------------------------------------------------------------
# Fixture schedules
# ---------------------------------------------------------------------------

DAILY_24_7 = {
    "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1;WKST=MO",
    "starttime": "00:00",
    "endtime": "24:00",
}

DAILY_BUSINESS = {
    "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1;WKST=MO",
    "starttime": "09:00",
    "endtime": "17:00",
}

WEEKDAY_ONLY = {
    "rrule": (
        "DTSTART:20200101T000000Z\n"
        "RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;WKST=MO"
    ),
    "starttime": "08:00",
    "endtime": "18:00",
}


# ---------------------------------------------------------------------------
# Basic window tests
# ---------------------------------------------------------------------------

@freeze_time("2024-03-15 12:00:00")  # Friday, midday
def test_within_window_returns_true():
    assert events.verify_datetime(DAILY_BUSINESS) is True


@freeze_time("2024-03-15 08:59:00")  # just before 09:00
def test_before_window_start_returns_false():
    assert events.verify_datetime(DAILY_BUSINESS) is False


@freeze_time("2024-03-15 17:01:00")  # just after 17:00
def test_after_window_end_returns_false():
    assert events.verify_datetime(DAILY_BUSINESS) is False


@freeze_time("2024-03-15 09:00:00")  # exactly at start boundary (inclusive)
def test_at_start_boundary_returns_true():
    assert events.verify_datetime(DAILY_BUSINESS) is True


@freeze_time("2024-03-15 17:00:00")  # exactly at end boundary (inclusive per <=)
def test_at_end_boundary_returns_true():
    assert events.verify_datetime(DAILY_BUSINESS) is True


# ---------------------------------------------------------------------------
# 24:00 end-time edge case
# ---------------------------------------------------------------------------

@freeze_time("2024-03-15 23:59:30")
def test_24_00_endtime_late_night_returns_true():
    """endtime '24:00' should be treated as 23:59:59 — still open at 23:59."""
    assert events.verify_datetime(DAILY_24_7) is True


@freeze_time("2024-03-15 00:01:00")  # 00:00:00 exactly triggers RRULE boundary issue
def test_24_00_endtime_midnight_start_returns_true():
    """24/7 schedule should be open just after midnight."""
    assert events.verify_datetime(DAILY_24_7) is True


# ---------------------------------------------------------------------------
# RRULE weekday filter
# ---------------------------------------------------------------------------

@freeze_time("2024-03-15 12:00:00")  # Friday (weekday)
def test_weekday_rrule_on_friday_returns_true():
    assert events.verify_datetime(WEEKDAY_ONLY) is True


@freeze_time("2024-03-16 12:00:00")  # Saturday — excluded
def test_weekday_rrule_on_saturday_returns_false():
    assert events.verify_datetime(WEEKDAY_ONLY) is False


# ---------------------------------------------------------------------------
# Missing / malformed schedule — must return False, never raise
# ---------------------------------------------------------------------------

def test_missing_all_keys_returns_false():
    assert events.verify_datetime({}) is False


def test_missing_starttime_returns_false():
    assert events.verify_datetime(
        {"rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY", "endtime": "17:00"}
    ) is False


def test_missing_endtime_returns_false():
    assert events.verify_datetime(
        {"rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY", "starttime": "09:00"}
    ) is False


def test_malformed_rrule_returns_false_not_exception():
    schedule = {"rrule": "NOT_A_VALID_RRULE", "starttime": "09:00", "endtime": "17:00"}
    result = events.verify_datetime(schedule)
    # Must not raise — exception is swallowed and False is returned
    assert result is False


def test_none_schedule_returns_false():
    # Legacy code paths pass None-like empty dicts
    assert events.verify_datetime({"rrule": None, "starttime": "09:00", "endtime": "17:00"}) is False
