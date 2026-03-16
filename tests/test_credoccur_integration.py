"""
Integration tests for POST /api/credOccur.

Unlike test_api.py (which stubs out update_credOccur / check_entrance_status),
these tests let both functions run real code and assert on actual side effects:

  - events module globals (credOccur, E1_entrance_schedule)
  - relay.lock_unlock_entrance_one called with the correct unlock flag
  - reader_detects_bits() using globals that were set by the POST

The Flask test client is used so the full api.post_credOccur() code path runs
(file write → events.update_credOccur() → events.check_entrance_status()).
"""

import json
from datetime import timezone

import pytest
from freezegun import freeze_time

import api as flask_api
import events
import relay
import eventsMod

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Entrance 1 name as per src/json/config.json  EntranceName.E1 = 1
_E1_NAME = 1

# 24/7 RRULE — always open at any frozen time
_ALWAYS_OPEN = {
    "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1",
    "starttime": "00:00",
    "endtime": "24:00",
}

# Narrow window that is always closed at noon (our frozen test time)
_ALWAYS_CLOSED_AT_NOON = {
    "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1",
    "starttime": "23:00",
    "endtime": "23:01",
}

# Card Wiegand value and derived UID (same formula as events.py line 565)
_CARD_WIEGAND_VALUE = 12_345_678
_VALID_CARD_UID = "0" + str(int(f"{_CARD_WIEGAND_VALUE:026b}"[1:25], 2))
_PERSON_ID = 42
_GROUP_ID = 10


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    flask_api.app.config["TESTING"] = True
    with flask_api.app.test_client() as c:
        yield c


@pytest.fixture
def integration_setup(tmp_path, monkeypatch):
    """
    Wire both api.path and events.path to tmp_path so that:
      - api.post_credOccur() writes to tmp_path/json/credOccur.json
      - events.update_credOccur() reads from the same file
    Also pins tzlocal to UTC for consistent schedule evaluation, and
    suppresses relay calls for entrance 2 (not under test).
    """
    (tmp_path / "json").mkdir()
    monkeypatch.setattr(flask_api, "path", str(tmp_path))
    monkeypatch.setattr(events, "path", str(tmp_path))
    monkeypatch.setattr(events, "tzlocal", lambda: timezone.utc)
    monkeypatch.setattr(relay, "lock_unlock_entrance_two", lambda *a, **kw: None)
    return tmp_path


def _make_credoccur(entrance_schedule, credential_uid=None):
    """Build a minimal but structurally complete credOccur document for E1."""
    creds = {}
    if credential_uid:
        creds[credential_uid] = {
            "PersonId": _PERSON_ID,
            "IsPerm": True,
            "EndDate": None,
            "AccessGroup": _GROUP_ID,
        }
    return {
        "Entrances": [{
            "Entrance": _E1_NAME,
            "EntranceSchedule": entrance_schedule,
            "EntranceDetails": {
                "Antipassback": "No",
                "Zone": None,
                "AuthenticationDevices": {
                    "IN": {
                        "Masterpassword": False,
                        "Direction": "IN",
                        "defaultAuthMethod": "Card",
                        "AuthMethod": [],
                    },
                    "OUT": {
                        "Masterpassword": False,
                        "Direction": "OUT",
                        "defaultAuthMethod": "Card",
                        "AuthMethod": [],
                    },
                },
                "AccessGroups": [{
                    "GroupId": _GROUP_ID,
                    "Persons": [_PERSON_ID],
                    "Schedule": entrance_schedule,
                }],
            },
            "ThirdPartyOptions": "N.A.",
            "isActive": True,
        }],
        "CredentialLookup": creds,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@freeze_time("2024-03-15 12:00:00")
def test_post_credoccur_with_open_schedule_unlocks_entrance(client, integration_setup, monkeypatch):
    """
    POSTing a credOccur with an always-open EntranceSchedule must:
      1. Update events.E1_entrance_schedule to the posted schedule
      2. Update events.credOccur with the posted data
      3. Call relay.lock_unlock_entrance_one with unlock=True
    """
    unlock_calls = []
    monkeypatch.setattr(
        relay, "lock_unlock_entrance_one",
        lambda thirdParty=None, unlock=False: unlock_calls.append(unlock),
    )

    data = _make_credoccur(_ALWAYS_OPEN)
    resp = client.post(
        "/api/credOccur",
        data=json.dumps(data),
        content_type="application/json",
    )

    assert resp.status_code == 200
    assert events.E1_entrance_schedule == _ALWAYS_OPEN
    assert events.credOccur["Entrances"][0]["Entrance"] == _E1_NAME
    assert len(unlock_calls) == 1
    assert unlock_calls[0] is True, "Always-open schedule must call unlock=True"


@freeze_time("2024-03-15 12:00:00")
def test_post_credoccur_with_closed_schedule_locks_entrance(client, integration_setup, monkeypatch):
    """
    POSTing a credOccur with a schedule closed at noon must call
    relay.lock_unlock_entrance_one with unlock=False.
    """
    unlock_calls = []
    monkeypatch.setattr(
        relay, "lock_unlock_entrance_one",
        lambda thirdParty=None, unlock=False: unlock_calls.append(unlock),
    )

    data = _make_credoccur(_ALWAYS_CLOSED_AT_NOON)
    resp = client.post(
        "/api/credOccur",
        data=json.dumps(data),
        content_type="application/json",
    )

    assert resp.status_code == 200
    assert len(unlock_calls) == 1
    assert unlock_calls[0] is False, "Closed schedule must call unlock=False"


@freeze_time("2024-03-15 12:00:00")
def test_post_credoccur_updates_credoccur_global_for_reader(client, integration_setup, monkeypatch):
    """
    POSTing a credOccur with a known credential must update the module-level
    globals used by reader_detects_bits().  Calling reader_detects_bits() after
    the POST must trigger the relay — proving the globals set by the POST are the
    ones actually consumed by the reader access-control logic.
    """
    monkeypatch.setattr(relay, "lock_unlock_entrance_one", lambda *a, **kw: None)

    relay_fired = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: relay_fired.append(1))
    monkeypatch.setattr(eventsMod, "record_auth_scans", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "record_unauth_scans", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda *a, **kw: None)

    # Reset reader state so no leftover credentials from other tests interfere
    events.credentials_E1_IN.clear()
    events.pinsvalue_E1_IN.clear()
    if events.timeout_cred_E1_IN.status():
        events.timeout_cred_E1_IN.stop()

    data = _make_credoccur(_ALWAYS_OPEN, credential_uid=_VALID_CARD_UID)
    resp = client.post(
        "/api/credOccur",
        data=json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 200

    # Verify the CredentialLookup global was updated
    assert _VALID_CARD_UID in events.credOccur.get("CredentialLookup", {}), (
        "CredentialLookup global must contain the posted credential UID"
    )

    # Simulate a card scan — reader_detects_bits must use the globals set by the POST
    events.reader_detects_bits(26, _CARD_WIEGAND_VALUE, "E1_IN")

    assert len(relay_fired) == 1, (
        "relay must fire when card matches the CredentialLookup posted via /api/credOccur"
    )
