"""
Tests for eventsMod event-dictionary construction.

The critical assertion is that the correct eventActionTypeId is placed in each
dictionary, since this is what the backend uses to classify audit-log entries.

Known IDs (from data-postgresql.sql and eventsMod.py):
  1  — Authenticated scan     (record_auth_scans)
  2  — Master password used   (record_masterpassword_used)
  3  — Unauthenticated scan   (record_unauth_scans)
 13  — Valid PIN used         (pin_only_used)
 14  — Invalid PIN used       (invalid_pin_used)
"""

import pytest
from unittest.mock import Mock

import eventsMod
import eventActionTriggers

# Event-type ID constants (from data-postgresql.sql)
AUTH_SCAN        = 1
MASTER_PASSWORD  = 2
UNAUTH_SCAN      = 3
PIN_ONLY         = 13
INVALID_PIN      = 14


@pytest.fixture(autouse=True)
def mock_network(monkeypatch):
    """Prevent any actual HTTP calls in all tests in this module."""
    monkeypatch.setattr(eventActionTriggers, "event_trigger_cb", lambda e: None)


# ---------------------------------------------------------------------------
# record_auth_scans  →  eventActionTypeId = 1
# ---------------------------------------------------------------------------

def test_record_auth_scans_eventActionTypeId_is_1(monkeypatch):
    mock_update = Mock()
    monkeypatch.setattr(eventsMod, "update_logs_and_server", mock_update)

    eventsMod.record_auth_scans(42, 10, "Card", 1, "IN")

    mock_update.assert_called_once()
    assert mock_update.call_args[0][0]["eventActionType"]["eventActionTypeId"] == AUTH_SCAN


def test_record_auth_scans_includes_person_and_group(monkeypatch):
    mock_update = Mock()
    monkeypatch.setattr(eventsMod, "update_logs_and_server", mock_update)

    eventsMod.record_auth_scans(42, 10, "Card", 1, "OUT")

    d = mock_update.call_args[0][0]
    assert d["person"]["personId"] == 42
    assert d["accessGroup"]["accessGroupId"] == 10
    assert d["direction"] == "OUT"
    assert d["entrance"]["entranceId"] == 1


# ---------------------------------------------------------------------------
# invalid_pin_used  →  eventActionTypeId = 14
# ---------------------------------------------------------------------------

def test_invalid_pin_used_eventActionTypeId_is_14(monkeypatch):
    mock_update = Mock()
    monkeypatch.setattr(eventsMod, "update_logs_and_server", mock_update)

    eventsMod.invalid_pin_used(1, "IN")

    assert mock_update.call_args[0][0]["eventActionType"]["eventActionTypeId"] == INVALID_PIN


def test_invalid_pin_used_has_no_person_key(monkeypatch):
    mock_update = Mock()
    monkeypatch.setattr(eventsMod, "update_logs_and_server", mock_update)

    eventsMod.invalid_pin_used(1, "IN")

    d = mock_update.call_args[0][0]
    # Failed auth = unknown person; no person reference expected
    assert d.get("person") is None


# ---------------------------------------------------------------------------
# pin_only_used  →  eventActionTypeId = 13
# ---------------------------------------------------------------------------

def test_pin_only_used_eventActionTypeId_is_13(monkeypatch):
    mock_update = Mock()
    monkeypatch.setattr(eventsMod, "update_logs_and_server", mock_update)

    eventsMod.pin_only_used(42, 10, 1, "IN")

    assert mock_update.call_args[0][0]["eventActionType"]["eventActionTypeId"] == PIN_ONLY


def test_pin_only_used_includes_person_and_group(monkeypatch):
    mock_update = Mock()
    monkeypatch.setattr(eventsMod, "update_logs_and_server", mock_update)

    eventsMod.pin_only_used(99, 5, 2, "OUT")

    d = mock_update.call_args[0][0]
    assert d["person"]["personId"] == 99
    assert d["accessGroup"]["accessGroupId"] == 5


# ---------------------------------------------------------------------------
# record_masterpassword_used  →  eventActionTypeId = 2
# ---------------------------------------------------------------------------

def test_record_masterpassword_used_eventActionTypeId_is_2(monkeypatch):
    mock_update = Mock()
    monkeypatch.setattr(eventsMod, "update_logs_and_server", mock_update)

    eventsMod.record_masterpassword_used("Master Pin", 1, "IN")

    assert mock_update.call_args[0][0]["eventActionType"]["eventActionTypeId"] == MASTER_PASSWORD


# ---------------------------------------------------------------------------
# record_unauth_scans  →  eventActionTypeId = 3
# ---------------------------------------------------------------------------

def test_record_unauth_scans_eventActionTypeId_is_3(monkeypatch):
    mock_update = Mock()
    monkeypatch.setattr(eventsMod, "update_logs_and_server", mock_update)

    eventsMod.record_unauth_scans("Card", 1, "IN")

    assert mock_update.call_args[0][0]["eventActionType"]["eventActionTypeId"] == UNAUTH_SCAN
