"""
Tests for events.reader_detects_bits().

This is the Pi's core access-control function: it receives raw Wiegand bits from
a card/PIN reader, looks up the credential in credOccur, evaluates the auth method
and schedule, and either opens the door (trigger_relay_*) or logs an unauthorised
attempt.

Strategy:
- monkeypatch events.credOccur with controlled in-memory data via _make_credoccur()
- monkeypatch relay.trigger_relay_one / trigger_relay_two to capture door-open calls
- monkeypatch eventsMod.* to suppress network/log calls while tracking invocations
- autouse fixture resets all module-level credential/pin/timer state before each test
  and pins events.tzlocal to UTC so verify_datetime's rrule date comparison is
  consistent regardless of host timezone

Auth modes tested:
  "Card"        — single factor, card only
  "Pin"         — single factor, PIN only
  "Card + Pin"  — AND: both factors required before door opens
  "Card / Pin"  — OR: either factor alone is sufficient

Card UID computation (same formula as events.py line 565):
    UID = "0" + str(int(f"{wiegand_value:026b}"[1:25], 2))
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import timezone
from freezegun import freeze_time

import events
import relay
import eventsMod

# ---------------------------------------------------------------------------
# Precompute a known card UID
# ---------------------------------------------------------------------------
_CARD_WIEGAND_VALUE = 12_345_678
_VALID_CARD_UID = "0" + str(int(f"{_CARD_WIEGAND_VALUE:026b}"[1:25], 2))
_PERSON_ID = 42
_GROUP_ID = 10
_ENTRANCE_NAME = 1  # matches config.json "EntranceName": {"E1": 1}

# A 24/7 RRULE schedule (always open)
_ALWAYS_OPEN = {
    "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1",
    "starttime": "00:00",
    "endtime": "24:00",
}

# ---------------------------------------------------------------------------
# Base credOccur fixture — entrance 1, Card auth, one person
# ---------------------------------------------------------------------------
def _make_credoccur(auth_method="Card", extra_credentials=None):
    creds = {_VALID_CARD_UID: {"PersonId": _PERSON_ID, "IsPerm": True,
                                "EndDate": None, "AccessGroup": _GROUP_ID}}
    if extra_credentials:
        creds.update(extra_credentials)
    return {
        "Entrances": [{
            "Entrance": _ENTRANCE_NAME,
            "EntranceSchedule": _ALWAYS_OPEN,
            "EntranceDetails": {
                "Antipassback": "No",
                "Zone": None,
                "AuthenticationDevices": {
                    "IN": {
                        "Masterpassword": "999999",
                        "Direction": "IN",
                        "defaultAuthMethod": auth_method,
                        "AuthMethod": [],
                    },
                    "OUT": {
                        "Masterpassword": False,
                        "Direction": "OUT",
                        "defaultAuthMethod": auth_method,
                        "AuthMethod": [],
                    },
                },
                "AccessGroups": [{
                    "GroupId": _GROUP_ID,
                    "Persons": [_PERSON_ID],
                    "Schedule": _ALWAYS_OPEN,
                }],
            },
            "ThirdPartyOptions": "N.A.",
            "isActive": True,
        }],
        "CredentialLookup": creds,
    }


# ---------------------------------------------------------------------------
# Autouse fixture: reset all module-level state before every test
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_events_state(monkeypatch):
    # Pin tzlocal to UTC so verify_datetime's rrule date comparisons are
    # consistent regardless of the host machine's local timezone offset.
    monkeypatch.setattr(events, "tzlocal", lambda: timezone.utc)
    events.credentials_E1_IN.clear()
    events.credentials_E1_OUT.clear()
    events.credentials_E2_IN.clear()
    events.credentials_E2_OUT.clear()
    events.pinsvalue_E1_IN.clear()
    events.pinsvalue_E1_OUT.clear()
    events.pinsvalue_E2_IN.clear()
    events.pinsvalue_E2_OUT.clear()
    events.mag_E1_allowed_to_open = False
    events.mag_E2_allowed_to_open = False
    for timer in (
        events.timeout_cred_E1_IN, events.timeout_cred_E1_OUT,
        events.timeout_cred_E2_IN, events.timeout_cred_E2_OUT,
    ):
        if timer.status():
            timer.stop()
    yield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def scan_card(entrance="E1_IN"):
    events.reader_detects_bits(26, _CARD_WIEGAND_VALUE, entrance)


def enter_pin(pin_str, entrance="E1_IN"):
    for ch in pin_str:
        events.reader_detects_bits(4, int(ch), entrance)
    events.reader_detects_bits(4, 11, entrance)  # submit (value 11)


# ---------------------------------------------------------------------------
# Test: valid card → door opens
# ---------------------------------------------------------------------------
def test_valid_card_opens_door(monkeypatch):
    monkeypatch.setattr(events, "credOccur", _make_credoccur("Card"))
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    monkeypatch.setattr(eventsMod, "record_auth_scans", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    scan_card("E1_IN")

    assert len(opened) == 1, "relay must fire once for a valid card"
    assert events.mag_E1_allowed_to_open is True


# ---------------------------------------------------------------------------
# Test: unknown card → door stays closed, wrong-cred feedback
# ---------------------------------------------------------------------------
def test_unknown_card_does_not_open_door(monkeypatch):
    monkeypatch.setattr(events, "credOccur", _make_credoccur("Card"))
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    unauth_calls = []
    monkeypatch.setattr(eventsMod, "record_unauth_scans",
                        lambda *a, **kw: unauth_calls.append(1))
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    # Send an unknown card value
    unknown_value = 99_999_999
    events.reader_detects_bits(26, unknown_value, "E1_IN")

    assert len(opened) == 0
    assert len(unauth_calls) == 1


# ---------------------------------------------------------------------------
# Test: master password → door opens regardless of person lookup
# ---------------------------------------------------------------------------
def test_master_password_opens_door(monkeypatch):
    monkeypatch.setattr(events, "credOccur", _make_credoccur("Card"))
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    master_calls = []
    monkeypatch.setattr(eventsMod, "record_masterpassword_used",
                        lambda *a, **kw: master_calls.append(1))
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    # Master password is "999999" in _make_credoccur
    for digit in "999999":
        events.reader_detects_bits(4, int(digit), "E1_IN")
    events.reader_detects_bits(4, 11, "E1_IN")  # submit

    assert len(opened) == 1
    assert len(master_calls) == 1


# ---------------------------------------------------------------------------
# Test: valid card but schedule inactive → door denied
# ---------------------------------------------------------------------------
@freeze_time("2024-03-15 12:00:00")  # noon UTC — safely outside any 23:00–23:01 window
def test_valid_card_outside_schedule_denied(monkeypatch):
    monkeypatch.setattr(events, "tzlocal", lambda: timezone.utc)
    closed_schedule = {
        "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1",
        "starttime": "23:00",
        "endtime": "23:01",  # extremely narrow window — almost always closed
    }
    cred_occur = _make_credoccur("Card")
    # Replace the access group schedule with the closed one
    cred_occur["Entrances"][0]["EntranceDetails"]["AccessGroups"][0]["Schedule"] = closed_schedule
    monkeypatch.setattr(events, "credOccur", cred_occur)

    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    unauth_calls = []
    monkeypatch.setattr(eventsMod, "record_unauth_scans",
                        lambda *a, **kw: unauth_calls.append(1))
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    scan_card("E1_IN")

    assert len(opened) == 0


# ---------------------------------------------------------------------------
# Test: PIN submit flow (auth method = "Pin")
# ---------------------------------------------------------------------------
def test_valid_pin_opens_door(monkeypatch):
    pin = "1234"
    cred_occur = _make_credoccur("Pin", extra_credentials={pin: {
        "PersonId": _PERSON_ID, "IsPerm": True, "EndDate": None, "AccessGroup": _GROUP_ID
    }})
    monkeypatch.setattr(events, "credOccur", cred_occur)
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    monkeypatch.setattr(eventsMod, "pin_only_used", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    enter_pin(pin, "E1_IN")

    assert len(opened) == 1


def test_pin_clear_resets_digits(monkeypatch):
    monkeypatch.setattr(events, "credOccur", _make_credoccur("Pin"))
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)
    monkeypatch.setattr(eventsMod, "invalid_pin_used", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "record_unauth_scans", lambda *a, **kw: None)

    # Enter some digits then clear (value 10)
    for digit in "123":
        events.reader_detects_bits(4, int(digit), "E1_IN")
    events.reader_detects_bits(4, 10, "E1_IN")  # clear

    assert len(events.pinsvalue_E1_IN) == 0


# ---------------------------------------------------------------------------
# Test: AND auth — card alone is not enough (waiting for PIN)
# ---------------------------------------------------------------------------
def test_card_plus_pin_and_method_needs_both(monkeypatch):
    pin = "5678"
    cred_occur = _make_credoccur("Card + Pin", extra_credentials={pin: {
        "PersonId": _PERSON_ID, "IsPerm": True, "EndDate": None, "AccessGroup": _GROUP_ID
    }})
    monkeypatch.setattr(events, "credOccur", cred_occur)
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    # Card alone → should NOT open (waiting for PIN)
    scan_card("E1_IN")
    assert len(opened) == 0, "Card alone must not open door in Card+PIN AND mode"
    assert "Card" in events.credentials_E1_IN  # card credential is stored


# ---------------------------------------------------------------------------
# Test: AuthMethod schedule overrides defaultAuthMethod
# ---------------------------------------------------------------------------
@freeze_time("2024-03-15 12:00:00")
def test_authmethod_schedule_overrides_default(monkeypatch):
    monkeypatch.setattr(events, "tzlocal", lambda: timezone.utc)
    pin = "1234"
    cred_occur = _make_credoccur("Card", extra_credentials={pin: {
        "PersonId": _PERSON_ID, "IsPerm": True, "EndDate": None, "AccessGroup": _GROUP_ID
    }})
    # Inject a scheduled AuthMethod that overrides defaultAuthMethod="Card" with "Pin"
    cred_occur["Entrances"][0]["EntranceDetails"]["AuthenticationDevices"]["IN"]["AuthMethod"] = [
        {"Method": "Pin", "Schedule": _ALWAYS_OPEN},
    ]
    monkeypatch.setattr(events, "credOccur", cred_occur)

    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    monkeypatch.setattr(eventsMod, "record_unauth_scans", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "pin_only_used", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    # Card scan: scheduled auth method is now Pin → card is rejected
    scan_card("E1_IN")
    assert len(opened) == 0, "Card must NOT open door when scheduled auth method overrides to Pin"

    # Correct PIN → door opens
    enter_pin(pin, "E1_IN")
    assert len(opened) == 1, "Correct PIN must open door when scheduled auth method is Pin"


# ---------------------------------------------------------------------------
# Test: scan at entrance not present in credOccur → graceful denial
# ---------------------------------------------------------------------------
def test_entrance_not_in_credoccur_gracefully_denied(monkeypatch):
    """If credOccur has no entry for the scanned entrance (e.g. E1 reader fires
    but credOccur only describes E2), the `if not entrance_details` guard must
    call record_unauth_scans and return without opening the door.
    This covers mis-sync / config mismatch scenarios.
    """
    # credOccur describes entrance ID 2 (E2) only — E1 is absent
    credoccur_e2_only = {
        "Entrances": [{"Entrance": 2, "EntranceSchedule": _ALWAYS_OPEN,
                       "EntranceDetails": {"AuthenticationDevices": {}, "AccessGroups": []},
                       "ThirdPartyOptions": "N.A.", "isActive": True}],
        "CredentialLookup": {},
    }
    monkeypatch.setattr(events, "credOccur", credoccur_e2_only)
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    unauth_calls = []
    monkeypatch.setattr(eventsMod, "record_unauth_scans",
                        lambda *a, **kw: unauth_calls.append(1))
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    scan_card("E1_IN")  # E1 not in credOccur

    assert len(opened) == 0, "Door must not open for unrecognised entrance"
    assert len(unauth_calls) == 1, "Unrecognised entrance must record unauth scan"


# ---------------------------------------------------------------------------
# Test: two overlapping AuthMethod schedules both active — first one wins
# ---------------------------------------------------------------------------
@freeze_time("2024-03-15 12:00:00")
def test_two_active_authmethod_schedules_first_one_wins(monkeypatch):
    """When two AuthMethod schedule entries are simultaneously active, the Pi picks
    the FIRST one and breaks — the second is never evaluated.

    Setup: defaultAuthMethod="Card", but AuthMethod list has:
      [{"Method": "Pin", "Schedule": ALWAYS_OPEN},
       {"Method": "Card", "Schedule": ALWAYS_OPEN}]
    Both schedules are active. The loop breaks on the first → auth_method_name="Pin".
    A card scan must be rejected; only a valid PIN opens the door.
    """
    monkeypatch.setattr(events, "tzlocal", lambda: timezone.utc)
    pin = "1234"
    cred_occur = _make_credoccur("Card", extra_credentials={pin: {
        "PersonId": _PERSON_ID, "IsPerm": True, "EndDate": None, "AccessGroup": _GROUP_ID
    }})
    # Two overlapping active schedules: first wins
    cred_occur["Entrances"][0]["EntranceDetails"]["AuthenticationDevices"]["IN"]["AuthMethod"] = [
        {"Method": "Pin",  "Schedule": _ALWAYS_OPEN},
        {"Method": "Card", "Schedule": _ALWAYS_OPEN},
    ]
    monkeypatch.setattr(events, "credOccur", cred_occur)

    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    monkeypatch.setattr(eventsMod, "record_unauth_scans", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "pin_only_used", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    # Card rejected — first schedule made auth_method "Pin"
    scan_card("E1_IN")
    assert len(opened) == 0, "Card must be rejected when first active schedule selects Pin"

    # Correct PIN opens door
    enter_pin(pin, "E1_IN")
    assert len(opened) == 1, "Correct PIN must open door when first active schedule is Pin"


# ---------------------------------------------------------------------------
# Test: OR auth ("Card / Pin") — card alone is sufficient
# ---------------------------------------------------------------------------
def test_or_auth_card_alone_opens_door(monkeypatch):
    monkeypatch.setattr(events, "credOccur", _make_credoccur("Card / Pin"))
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    monkeypatch.setattr(eventsMod, "record_auth_scans", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    scan_card("E1_IN")

    assert len(opened) == 1, \
        "Card alone must open door in OR (Card / Pin) auth mode"


# ---------------------------------------------------------------------------
# Test: PIN buffer overflow — MAX_PIN_LENGTH guard caps pinsvalue growth
# ---------------------------------------------------------------------------
def test_pin_overflow_is_rejected(monkeypatch):
    """Entering more than MAX_PIN_LENGTH digits without a submit must not grow
    the pinsvalue buffer beyond MAX_PIN_LENGTH + 1 entries.

    The guard ``if len(pinsvalue) > MAX_PIN_LENGTH: return False`` in
    ``process_pin_value`` enforces this cap.  The door must also stay closed
    because no submit signal (value 11) is ever sent.
    """
    monkeypatch.setattr(events, "credOccur", _make_credoccur("Pin"))
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))

    # Enter well over MAX_PIN_LENGTH digits without pressing submit
    for digit in range(events.MAX_PIN_LENGTH + 4):
        events.reader_detects_bits(4, digit % 10, "E1_IN")

    assert len(opened) == 0, "Door must stay closed without a submit signal"
    assert len(events.pinsvalue_E1_IN) <= events.MAX_PIN_LENGTH + 1, (
        "pinsvalue must not grow beyond MAX_PIN_LENGTH + 1 entries"
    )
