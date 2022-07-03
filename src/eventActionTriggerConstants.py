'''
This file contains the eventActionInputId and eventActionOutputId of eventActions
DO NOT MODIFY THESE VALUES UNLESS THE JAVA SIDE IS MODIFIED AS WELL
'''

# input
# non timer
AUTHENTICATED_SCAN=1
UNAUTHENTICATED_SCAN=2
EXIT_BUTTON_PRESSED=3
CONTACT_OPEN_WITHOUT_AUTHENTICATION=4
CONTACT_OPEN_WITH_AUTHENTICATION=5
EXTERNAL_ALARM=6
GEN_IN_1=7
GEN_IN_2=8
GEN_IN_3=9
# timer
CONTACT_OPEN=10


# # id of timer based input events
# TIMED_EVENTS={CONTACT_OPEN} # set for better performance
def input_is_timed(event_action_trigger):
    '''return if input is timed (ie contact open)
    
    Args:
        event_action_trigger (check eventActionTriggerConstants.py): event_action id
        
    Returns:
        is_timed (bool): if the event_action_trigger is timed
    '''

    return event_action_trigger == CONTACT_OPEN
