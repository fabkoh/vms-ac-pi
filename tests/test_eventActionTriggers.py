"""
Tests for src/eventActionTriggers.py.

Covers two independent concerns:

1. sendEmail_function / sendSMS_function — silent exception swallow
   Both functions wrap their HTTP POST in a try/except and must not propagate
   any exception when the backend is unreachable.

2. event_trigger_cb — activated flag prevents re-firing of multi-input events
   When an eventManagement has more than one inputEvent, the ``activated`` dict
   entry must be set to True after the first valid trigger so that subsequent
   calls are suppressed.  This was broken by a typo: the code read
   ``event.get("inputEvent", [])`` (singular) instead of
   ``event.get("inputEvents", [])`` (plural), which always returned an empty
   list and therefore never set the flag.
"""

import datetime
import pytest

import eventActionTriggers
from eventActionTriggerConstants import AUTHENTICATED_SCAN, BOTH_ENTRANCE, create_event

# ---------------------------------------------------------------------------
# Minimal event structure accepted by sendEmail_function / sendSMS_function
# ---------------------------------------------------------------------------
_HTTP_EVENT = {
    "entrance": {"entranceId": 1},
    "inputEvents": [{"inputEventId": 10}],
    "outputActions": [{"outputEventId": 20}],
}

# ---------------------------------------------------------------------------
# Event with two inputEvents — the activated-flag guard applies when len > 1
# ---------------------------------------------------------------------------
_TODAY = datetime.date.today().strftime("%Y-%m-%d")
_EVENT_ID = 99
_MULTI_INPUT_EVENT = {
    "eventsManagementId": _EVENT_ID,
    "triggerSchedule": {_TODAY: [{"starttime": "00:00", "endtime": "23:59"}]},
    "entrance": None,   # → get_entrance_from_event_management returns BOTH_ENTRANCE
    "inputEvents": [
        {"eventActionInputType": {"eventActionInputId": AUTHENTICATED_SCAN}},
        {"eventActionInputType": {"eventActionInputId": AUTHENTICATED_SCAN}},
    ],
    "outputActions": [],
}


# ---------------------------------------------------------------------------
# Autouse fixture: reset module-level state before each test
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_trigger_state():
    eventActionTriggers.activated.clear()
    eventActionTriggers.eventTriggerTime.clear()
    eventActionTriggers.output_events.clear()
    eventActionTriggers.event_trigger_cb.last_call_time = 0
    yield
    eventActionTriggers.activated.clear()
    eventActionTriggers.eventTriggerTime.clear()
    eventActionTriggers.output_events.clear()
    eventActionTriggers.event_trigger_cb.last_call_time = 0


# ---------------------------------------------------------------------------
# sendEmail_function — ConnectionError must not propagate
# ---------------------------------------------------------------------------

class TestSendEmailFunction:

    def test_connection_error_is_swallowed(self, monkeypatch):
        """requests.post raising ConnectionError must be caught silently.

        The ``except Exception`` clause in sendEmail_function must absorb the
        error so the caller is not disrupted when the backend is unreachable.
        """
        monkeypatch.setattr(
            eventActionTriggers.requests, "post",
            lambda *args, **kwargs: (_ for _ in ()).throw(ConnectionError("refused")),
        )
        # Must not raise
        eventActionTriggers.sendEmail_function(_HTTP_EVENT)


# ---------------------------------------------------------------------------
# sendSMS_function — ConnectionError must not propagate
# ---------------------------------------------------------------------------

class TestSendSMSFunction:

    def test_connection_error_is_swallowed(self, monkeypatch):
        """requests.post raising ConnectionError must be caught silently.

        The bare ``except`` clause in sendSMS_function must absorb the error.
        """
        monkeypatch.setattr(
            eventActionTriggers.requests, "post",
            lambda *args, **kwargs: (_ for _ in ()).throw(ConnectionError("refused")),
        )
        # Must not raise
        eventActionTriggers.sendSMS_function(_HTTP_EVENT)


# ---------------------------------------------------------------------------
# event_trigger_cb — activated flag suppresses re-firing
# ---------------------------------------------------------------------------

class TestEventTriggerCbActivatedFlag:

    def test_multi_input_event_fires_only_once(self, monkeypatch):
        """An event with len(inputEvents) > 1 must set activated[id]=True after
        the first valid trigger so that the second call is suppressed.

        This test verifies the fix for the ``inputEvent`` / ``inputEvents``
        typo: before the fix, the key was always missing → len([]) == 0, the
        flag was never set, and the event fired on every call.
        """
        monkeypatch.setattr(
            eventActionTriggers, "EVENT_ACTION_TRIGGERS_DATA", [_MULTI_INPUT_EVENT]
        )
        queued = []
        monkeypatch.setattr(
            eventActionTriggers, "queue_output", lambda e: queued.append(e)
        )
        monkeypatch.setattr(eventActionTriggers, "flush_output", lambda: None)

        trigger = create_event(AUTHENTICATED_SCAN, BOTH_ENTRANCE)

        # First call — event must be queued and activated flag set
        eventActionTriggers.event_trigger_cb(trigger)
        assert len(queued) == 1, "First call must queue the event"
        assert eventActionTriggers.activated.get(_EVENT_ID) is True, (
            "activated flag must be True after first valid fire"
        )

        # Reset debounce so the next call is not filtered by the 1-second cooldown
        eventActionTriggers.event_trigger_cb.last_call_time = 0

        # Second call — must be suppressed by the activated flag
        eventActionTriggers.event_trigger_cb(trigger)
        assert len(queued) == 1, (
            "Second call must be suppressed: activated flag must prevent re-firing"
        )
