from config import controller_config, credential_config
from timer import Timer
from app.helpers.util import int_or_default

DEFAULT_CRED_TIMEOUT = 20
DEFAULT_MAG_TIMEOUT = 10
DEFAULT_BUZZER_TIMEOUT = 10
MAX_PIN_LENGH = 6

def initialise():
    '''initialise events'''
    controller_config_json = controller_config.read()
    gpio_pins = controller_config_json['GPIOPins']
    timeout = controller_config_json['TIMEOUT']

    entrance1 = controller_config_json['EntranceName']['E1']
    entrance2 = controller_config_json['EntranceName']['E2']

    E1_Mag= int(gpio_pins["E1_Mag"])
    E1_Button= int(gpio_pins["E1_Button"])

    E2_Mag= int(gpio_pins["E2_Mag"])
    E2_Button= int(gpio_pins["E2_Button"])

    mag_E1_allowed_to_open = False
    mag_E2_allowed_to_open = False

    cred_E1_IN_timer = Timer()  
    cred_E1_OUT_timer = Timer()  
    mag_E1_timer = Timer()
    buzzer_E1_timer = Timer()

    cred_E2_IN_timer = Timer()  
    cred_E2_OUT_timer = Timer()  
    mag_E2_timer = Timer()
    buzzer_E2_timer = Timer()

    cred_timeout_e1 = int_or_default(timeout['CRED_TIMEOUT_E1'], DEFAULT_CRED_TIMEOUT)
    cred_timeout_e2 = int_or_default(timeout['CRED_TIMEOUT_E2'], DEFAULT_CRED_TIMEOUT)
    mag_timeout_e1 = int_or_default(timeout['MAG_TIMEOUT_E1'], DEFAULT_MAG_TIMEOUT)
    mag_timeout_e2 = int_or_default(timeout['MAG_TIMEOUT_E2'], DEFAULT_MAG_TIMEOUT)
    buzzer_timeout_e1 = int_or_default(timeout['BUZZER_TIMEOUT_E1'], DEFAULT_BUZZER_TIMEOUT)
    buzzer_timeout_e2 = int_or_default(timeout['BUZZER_TIMEOUT_E2'], DEFAULT_BUZZER_TIMEOUT)