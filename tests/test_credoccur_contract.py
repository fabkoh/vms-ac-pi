"""
Tests for the full credOccur read-and-execute contract across multiple entrances.

Complements test_reader_detects_bits.py (which uses a single E1 entrance). Here we
build a two-entrance credOccur document (E1 and E2) and verify that reader_detects_bits()
correctly enforces access-group membership, entrance-specific AccessGroups lists,
group schedule gating, and AND auth multi-factor flows.

credOccur structure mirrors what ControllerService.createJsonDocument() produces:
  - Top-level "Entrances" list: one entry per physical entrance
  - Each entrance has "EntranceDetails.AccessGroups": only groups with access to THAT entrance
  - Top-level "CredentialLookup": all valid credentials, keyed by UID, with AccessGroup FK

Entrance IDs match config.json ("EntranceName": {"E1": 1, "E2": 2}).
E1 → ID 1, opens via relay.trigger_relay_one
E2 → ID 2, opens via relay.trigger_relay_two

Covered scenarios:
  1. Card tied to Group A (E1 only) opens E1.
  2. Same card is denied at E2 because Group A is absent from E2's AccessGroups list.
  3. Card is denied at its own entrance when the access-group schedule is closed.
  4. AND auth (Card + Pin): card alone waits for PIN; combined → door opens at E2.
"""

import pytest
from datetime import timezone
from freezegun import freeze_time

import events
import relay
import eventsMod

# ---------------------------------------------------------------------------
# Constants — two persons, two groups, two entrances
# ---------------------------------------------------------------------------
_PERSON_A = 10
_PERSON_B = 20
_GROUP_A = 1   # has access to E1 only
_GROUP_B = 2   # has access to E2 only

_CARD_A_VALUE = 12_345_678
_CARD_A_UID = "0" + str(int(f"{_CARD_A_VALUE:026b}"[1:25], 2))

_CARD_B_VALUE = 87_654_321
_CARD_B_UID = "0" + str(int(f"{_CARD_B_VALUE:026b}"[1:25], 2))

_PIN_B = "5678"

_E1_ID = 1   # matches config.json "EntranceName": {"E1": 1}
_E2_ID = 2   # matches config.json "EntranceName": {"E2": 2}

_ALWAYS_OPEN = {
    "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1",
    "starttime": "00:00",
    "endtime": "24:00",
}

_ALWAYS_CLOSED = {
    "rrule": "DTSTART:20200101T000000Z\nRRULE:FREQ=DAILY;INTERVAL=1",
    "starttime": "23:00",
    "endtime": "23:01",  # extremely narrow — always closed at noon UTC
}


def _make_two_entrance_credoccur(e1_group_schedule=_ALWAYS_OPEN, e2_auth_method="Card"):
    """Build a two-entrance credOccur document.

    Group A → E1 only.  Group B → E2 only.
    Card A belongs to Person A / Group A.
    Card B and Pin B belong to Person B / Group B.
    """
    return {
        "Entrances": [
            {
                "Entrance": _E1_ID,
                "EntranceSchedule": _ALWAYS_OPEN,
                "EntranceDetails": {
                    "Antipassback": "No",
                    "Zone": "ZoneId",
                    "AuthenticationDevices": {
                        "IN":  {"Masterpassword": False, "Direction": "IN",
                                "defaultAuthMethod": "Card", "AuthMethod": []},
                        "OUT": {"Masterpassword": False, "Direction": "OUT",
                                "defaultAuthMethod": "Card", "AuthMethod": []},
                    },
                    "AccessGroups": [
                        {"GroupId": _GROUP_A, "Persons": [_PERSON_A],
                         "Schedule": e1_group_schedule},
                    ],
                },
                "ThirdPartyOptions": "N.A.",
                "isActive": True,
            },
            {
                "Entrance": _E2_ID,
                "EntranceSchedule": _ALWAYS_OPEN,
                "EntranceDetails": {
                    "Antipassback": "No",
                    "Zone": "ZoneId",
                    "AuthenticationDevices": {
                        "IN":  {"Masterpassword": False, "Direction": "IN",
                                "defaultAuthMethod": e2_auth_method, "AuthMethod": []},
                        "OUT": {"Masterpassword": False, "Direction": "OUT",
                                "defaultAuthMethod": "Card", "AuthMethod": []},
                    },
                    "AccessGroups": [
                        {"GroupId": _GROUP_B, "Persons": [_PERSON_B],
                         "Schedule": _ALWAYS_OPEN},
                    ],
                },
                "ThirdPartyOptions": "N.A.",
                "isActive": True,
            },
        ],
        "CredentialLookup": {
            _CARD_A_UID: {"PersonId": _PERSON_A, "IsPerm": True,
                          "EndDate": None, "AccessGroup": _GROUP_A},
            _CARD_B_UID: {"PersonId": _PERSON_B, "IsPerm": True,
                          "EndDate": None, "AccessGroup": _GROUP_B},
            _PIN_B:      {"PersonId": _PERSON_B, "IsPerm": True,
                          "EndDate": None, "AccessGroup": _GROUP_B},
        },
    }


# ---------------------------------------------------------------------------
# Autouse fixture: reset module-level state + pin tzlocal to UTC
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_events_state(monkeypatch):
    # Pin tzlocal to UTC so verify_datetime's rrule date comparison is consistent
    # regardless of the host machine's local timezone.
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
# Test 1: card opens its own entrance
# ---------------------------------------------------------------------------
def test_card_opens_own_entrance(monkeypatch):
    """Person A's card (Group A → E1 only) opens E1 via trigger_relay_one."""
    monkeypatch.setattr(events, "credOccur", _make_two_entrance_credoccur())
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    monkeypatch.setattr(eventsMod, "record_auth_scans", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    events.reader_detects_bits(26, _CARD_A_VALUE, "E1_IN")

    assert len(opened) == 1, "Card A must open E1"
    assert events.mag_E1_allowed_to_open is True


# ---------------------------------------------------------------------------
# Test 2: card denied at wrong entrance (group not in that entrance's list)
# ---------------------------------------------------------------------------
def test_card_denied_at_wrong_entrance(monkeypatch):
    """Person A's card (Group A → E1) is denied at E2 because Group A is absent
    from E2's AccessGroups list — the Pi enforces per-entrance group membership."""
    monkeypatch.setattr(events, "credOccur", _make_two_entrance_credoccur())
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_two", lambda *a, **kw: opened.append(1))
    unauth_calls = []
    monkeypatch.setattr(eventsMod, "record_unauth_scans",
                        lambda *a, **kw: unauth_calls.append(1))
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    events.reader_detects_bits(26, _CARD_A_VALUE, "E2_IN")

    assert len(opened) == 0, "Card A must not open E2 (group has no access)"
    assert len(unauth_calls) == 1, "Unauthorised scan must be recorded"


# ---------------------------------------------------------------------------
# Test 3: card denied when group schedule is inactive
# ---------------------------------------------------------------------------
@freeze_time("2024-03-15 12:00:00")  # noon UTC — outside the 23:00–23:01 closed window
def test_card_denied_when_group_schedule_inactive(monkeypatch):
    """Person A's card is valid and Group A covers E1, but the access-group schedule
    is closed at the scan time → the door must not open."""
    monkeypatch.setattr(events, "tzlocal", lambda: timezone.utc)
    monkeypatch.setattr(events, "credOccur",
                        _make_two_entrance_credoccur(e1_group_schedule=_ALWAYS_CLOSED))
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    unauth_calls = []
    monkeypatch.setattr(eventsMod, "record_unauth_scans",
                        lambda *a, **kw: unauth_calls.append(1))
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    events.reader_detects_bits(26, _CARD_A_VALUE, "E1_IN")

    assert len(opened) == 0, "Door must not open when access-group schedule is inactive"
    assert len(unauth_calls) == 1


# ---------------------------------------------------------------------------
# Test 4: AND auth full flow — card registers, PIN completes → door opens at E2
# ---------------------------------------------------------------------------
def test_card_and_pin_full_flow_opens_door(monkeypatch):
    """AND auth (Card + Pin) at E2: card alone leaves door closed while waiting for PIN;
    entering the correct PIN completes the flow and opens the door via trigger_relay_two."""
    monkeypatch.setattr(events, "credOccur",
                        _make_two_entrance_credoccur(e2_auth_method="Card + Pin"))
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_two", lambda *a, **kw: opened.append(1))
    monkeypatch.setattr(eventsMod, "record_auth_scans", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    # Card alone → AND mode, waiting for PIN
    events.reader_detects_bits(26, _CARD_B_VALUE, "E2_IN")
    assert len(opened) == 0, "Card alone must not open door in Card+Pin AND mode"
    assert "Card" in events.credentials_E2_IN, "Card credential must be stored"

    # PIN digits followed by submit (value 11)
    for digit in _PIN_B:
        events.reader_detects_bits(4, int(digit), "E2_IN")
    events.reader_detects_bits(4, 11, "E2_IN")

    assert len(opened) == 1, "Card + PIN must open door in AND mode"
    assert events.mag_E2_allowed_to_open is True


# ---------------------------------------------------------------------------
# Test 5: person's access group is the SECOND entry in AccessGroups list
# ---------------------------------------------------------------------------
def test_card_matches_second_access_group_in_list(monkeypatch):
    """The Pi uses next() to find a group by GroupId regardless of list position.
    Even if the matching AccessGroup is the SECOND entry, the door must open.

    Setup: E1's AccessGroups = [Group X (unrelated), Group A (Person A's group)].
    Person A's card has AccessGroup=Group A. Group A is at index 1, not 0.
    """
    _GROUP_X = 99  # an unrelated group at position 0

    credoccur = _make_two_entrance_credoccur()
    # Prepend an unrelated group so Group A is now at index 1
    credoccur["Entrances"][0]["EntranceDetails"]["AccessGroups"] = [
        {"GroupId": _GROUP_X, "Persons": [], "Schedule": _ALWAYS_OPEN},
        {"GroupId": _GROUP_A, "Persons": [_PERSON_A], "Schedule": _ALWAYS_OPEN},
    ]
    monkeypatch.setattr(events, "credOccur", credoccur)
    opened = []
    monkeypatch.setattr(relay, "trigger_relay_one", lambda *a, **kw: opened.append(1))
    monkeypatch.setattr(eventsMod, "record_auth_scans", lambda *a, **kw: None)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", lambda d: None)

    events.reader_detects_bits(26, _CARD_A_VALUE, "E1_IN")

    assert len(opened) == 1, \
        "Card must open door even when matching AccessGroup is not the first in the list"
