from config import ControllerConfig
import pigpio
from app.helpers.util import int_or_default

controller_config_json = ControllerConfig.read()
gpio_pins = controller_config_json['GPIOpins']

# in global namespace for main.py
Fire = int(gpio_pins['Fire'])
Relay_1 = int(gpio_pins['Relay_1'])
Relay_2 = int(gpio_pins['Relay_2'])

E1_IN_D0= int(gpio_pins['E1_IN_D0'])
E1_IN_D1= int(gpio_pins['E1_IN_D1'])
E1_IN_Buzz= int(gpio_pins['E1_IN_Buzz'])
E1_IN_Led= int(gpio_pins['E1_IN_Led'])
E1_OUT_D0= int(gpio_pins['E1_OUT_D0'])
E1_OUT_D1= int(gpio_pins['E1_OUT_D1'])
E1_OUT_Buzz= int(gpio_pins['E1_OUT_Buzz'])
E1_OUT_Led= int(gpio_pins['E1_OUT_Led'])
E1_Mag= int(gpio_pins['E1_Mag'])
E1_Button= int(gpio_pins['E1_Button'])

E2_IN_D0= int(gpio_pins['E2_IN_D0'])
E2_IN_D1= int(gpio_pins['E2_IN_D1'])
E2_IN_Buzz= int(gpio_pins['E2_IN_Buzz'])
E2_IN_Led= int(gpio_pins['E2_IN_Led'])
E2_OUT_D0= int(gpio_pins['E2_OUT_D0'])
E2_OUT_D1= int(gpio_pins['E2_OUT_D1'])
E2_OUT_Buzz= int(gpio_pins['E2_OUT_Buzz'])
E2_OUT_Led= int(gpio_pins['E2_OUT_Led'])
E2_Mag= int(gpio_pins['E2_Mag'])
E2_Button= int(gpio_pins['E2_Button'])

# gen pins might not have a profile
Gen_In_1 = int_or_default(gpio_pins['Gen_In_1'], None)
Gen_In_2 = int_or_default(gpio_pins['Gen_In_2'], None)
Gen_In_3 = int_or_default(gpio_pins['Gen_In_3'], None)
Gen_Out_1 = int_or_default(gpio_pins['Gen_Out_1'], None)
Gen_Out_2 = int_or_default(gpio_pins['Gen_Out_2'], None)
Gen_Out_3 = int_or_default(gpio_pins['Gen_Out_3'], None)

pi = pigpio.pi()
in_pins = [E1_Button, E1_Mag, 
           E2_Button, E2_Mag, 
           Gen_In_1, Gen_In_2, Gen_In_3]
out_pins = [E1_IN_Buzz, E1_IN_Led, E1_OUT_Buzz, E1_OUT_Led,
            E2_IN_Buzz, E2_IN_Led, E2_OUT_Buzz, E2_OUT_Led,
            Gen_Out_1, Gen_Out_2, Gen_Out_3]

for pin in in_pins:
    if pin is not None:
        pi.set_mode(pin, pigpio.INPUT)

for pin in out_pins:
    if pin is not None:
        pi.set_mode(pin, pigpio.OUTPUT)

def activate_buzz_led() :
   pi.write(E1_IN_Buzz,1)
   pi.write(E1_IN_Led,1)
   pi.write(E1_OUT_Buzz,1)
   pi.write(E1_OUT_Led,1)
   pi.write(E2_IN_Buzz,1)
   pi.write(E2_IN_Led,1)
   pi.write(E2_OUT_Buzz,1)
   pi.write(E2_OUT_Led,1)

def deactivate_buzz_led() :
   pi.write(E1_IN_Buzz,0)
   pi.write(E1_IN_Led,0)
   pi.write(E1_OUT_Buzz,0)
   pi.write(E1_OUT_Led,0)
   pi.write(E2_IN_Buzz,0)
   pi.write(E2_IN_Led,0)
   pi.write(E2_OUT_Buzz,0)
   pi.write(E2_OUT_Led,0)