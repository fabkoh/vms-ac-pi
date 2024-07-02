import sys

import eventActionTriggers as EAT
import eventActionTriggerConstants as EATC

sys.path.insert(1, '/home/unicon/vms-ac-pi/src')

def test_event_action_triggers_queue_output():
    event = EATC.create_event(EATC.AUTHENTICATED_SCAN, 1)
    EAT.queue_output(event)

    assert len(EAT.output_events) == 1