import src.eventActionTriggers as EAT
import src.eventActionTriggerConstants as EATC

def test_event_action_triggers_queue_output():
    event = EATC.create_event(EATC.AUTHENTICATED_SCAN, 1)
    EAT.queue_output(event)

    assert len(EAT.output_events) == 1