import threading
import time
import pigpio 
import json
from datetime import datetime
import os
import gc
from lock import config_lock
from executor import thread_pool_executor

path = os.path.dirname(os.path.abspath(__file__))


'''
   1. script to initialise GPIO pins and all variables, import from config.json
   2. includes class decoder
   3. includes function to detect events 
   3. includes class Timer
'''

config = None

GPIOpins = None

Fire =None
Relay_1 =None
Relay_2 =None

E1_IN_D0=None
E1_IN_D1=None
E1_IN_Buzz=None
E1_IN_Led=None
E1_OUT_D0=None
E1_OUT_D1=None
E1_OUT_Buzz=None
E1_OUT_Led=None
E1_Mag=None
E1_Button=None

E2_IN_D0=None
E2_IN_D1=None
E2_IN_Buzz=None
E2_IN_Led=None
E2_OUT_D0=None
E2_OUT_D1=None
E2_OUT_Buzz=None
E2_OUT_Led=None
E2_Mag=None
E2_Button=None

#initialising pi
pi = pigpio.pi()

Gen_In_1=None
Gen_Out_1=None
Gen_In_2=None
Gen_Out_2=None
Gen_In_3=None
Gen_Out_3=None

def update_config():
   '''call program.update_config() after calling this'''
   global config, GPIOpins, Fire, Relay_1, Relay_2, E1_IN_D0, E1_IN_D1, E1_IN_Buzz, \
      E1_IN_Led, E1_OUT_D0, E1_OUT_D1, E1_OUT_Buzz, E1_OUT_Led, E1_Mag, E1_Button, \
      E2_IN_D0, E2_IN_D1, E2_IN_Buzz, E2_IN_Led, E2_OUT_D0, E2_OUT_D1, E2_OUT_Buzz, \
      E2_OUT_Led, E2_Mag, E2_Button, Gen_In_1, Gen_Out_1, Gen_In_2, Gen_Out_2, \
      Gen_In_3, Gen_Out_3

   with config_lock:
      f=open(path+'/json/config.json')
      config=json.load(f)
      f.close()

   GPIOpins = config["GPIOpins"]

   Fire = int(GPIOpins["Fire"])
   Relay_1 = int(GPIOpins["Relay_1"])
   Relay_2 = int(GPIOpins["Relay_2"])

   E1_IN_D0= int(GPIOpins["E1_IN_D0"])
   E1_IN_D1= int(GPIOpins["E1_IN_D1"])
   E1_IN_Buzz= int(GPIOpins["E1_IN_Buzz"])
   E1_IN_Led= int(GPIOpins["E1_IN_Led"])
   E1_OUT_D0= int(GPIOpins["E1_OUT_D0"])
   E1_OUT_D1= int(GPIOpins["E1_OUT_D1"])
   E1_OUT_Buzz= int(GPIOpins["E1_OUT_Buzz"])
   E1_OUT_Led= int(GPIOpins["E1_OUT_Led"])
   E1_Mag= int(GPIOpins["E1_Mag"])
   E1_Button= int(GPIOpins["E1_Button"])

   E2_IN_D0= int(GPIOpins["E2_IN_D0"])
   E2_IN_D1= int(GPIOpins["E2_IN_D1"])
   E2_IN_Buzz= int(GPIOpins["E2_IN_Buzz"])
   E2_IN_Led= int(GPIOpins["E2_IN_Led"])
   E2_OUT_D0= int(GPIOpins["E2_OUT_D0"])
   E2_OUT_D1= int(GPIOpins["E2_OUT_D1"])
   E2_OUT_Buzz= int(GPIOpins["E2_OUT_Buzz"])
   E2_OUT_Led= int(GPIOpins["E2_OUT_Led"])
   E2_Mag= int(GPIOpins["E2_Mag"])
   E2_Button= int(GPIOpins["E2_Button"])
   
   #initialising E1
   pi.set_mode(E1_Button, pigpio.INPUT)
   pi.set_mode(E1_Mag, pigpio.INPUT) 
   pi.set_mode(E1_IN_Buzz, pigpio.OUTPUT) 
   pi.set_mode(E1_IN_Led, pigpio.OUTPUT) 
   pi.set_mode(E1_OUT_Buzz, pigpio.OUTPUT) 
   pi.set_mode(E1_OUT_Led, pigpio.OUTPUT) 

   #initialising E2
   pi.set_mode(E2_Button, pigpio.INPUT)
   pi.set_mode(E2_Mag, pigpio.INPUT) 
   pi.set_mode(E2_IN_Buzz, pigpio.OUTPUT) 
   pi.set_mode(E2_IN_Led, pigpio.OUTPUT) 
   pi.set_mode(E2_OUT_Buzz, pigpio.OUTPUT) 
   pi.set_mode(E2_OUT_Led, pigpio.OUTPUT) 

   #initialising Fire
   pi.set_mode(Fire, pigpio.INPUT)

   try:
      Gen_In_1= int(GPIOpins["Gen_In_1"])
      pi.set_mode(Gen_In_1, pigpio.INPUT)    
   except:
      pass

   try:
      Gen_Out_1= int(GPIOpins["Gen_Out_1"])
      pi.set_mode(Gen_Out_1, pigpio.OUTPUT) 
   except:
      pass

   try:
      Gen_In_2= int(GPIOpins["Gen_In_2"])
      pi.set_mode(Gen_In_2, pigpio.INPUT)    
   except:
      pass

   try:
      Gen_Out_2= int(GPIOpins["Gen_Out_2"])
      pi.set_mode(Gen_Out_2, pigpio.OUTPUT) 
   except:pass

   try:
      Gen_In_3= int(GPIOpins["Gen_In_3"])
      pi.set_mode(Gen_In_3, pigpio.INPUT)    
   except:pass

   try:
      Gen_Out_3= int(GPIOpins["Gen_Out_3"])
      pi.set_mode(Gen_Out_1, pigpio.OUTPUT) 

   except:
      pass

update_config() # initialise

class decoder:

   #callback refers to the function that is being called when the wiegand reader reads an input 
   #entrance refers to the particular entrance and reader e.g. E1R1
   def __init__(self, pi, gpio_0, gpio_1, callback, entrance, bit_timeout=5):


      self.pi = pi
      self.gpio_0 = gpio_0
      self.gpio_1 = gpio_1

      self.callback = callback

      self.bit_timeout = bit_timeout

      self.entrance = entrance

      self.in_code = False

      self.pi.set_mode(gpio_0, pigpio.INPUT)
      self.pi.set_mode(gpio_1, pigpio.INPUT)

      self.pi.set_pull_up_down(gpio_0, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpio_1, pigpio.PUD_UP)
    
      self.cb_0 = self.pi.callback(gpio_0, pigpio.FALLING_EDGE, self._cb)
      self.cb_1 = self.pi.callback(gpio_1, pigpio.FALLING_EDGE, self._cb)        
    
    

   def _cb(self, gpio, level,tick):

      """
      Accumulate bits until both gpios 0 and 1 timeout.
      """

      if level < pigpio.TIMEOUT:

         if self.in_code == False:
            self.bits = 1
            self.num = 0

            self.in_code = True
            self.code_timeout = 0
            self.pi.set_watchdog(self.gpio_0, self.bit_timeout)
            self.pi.set_watchdog(self.gpio_1, self.bit_timeout)
         else:
            self.bits += 1
            self.num = self.num << 1

         if gpio == self.gpio_0:
            self.code_timeout = self.code_timeout & 2 # clear gpio 0 timeout
         else:
            self.code_timeout = self.code_timeout & 1 # clear gpio 1 timeout
            self.num = self.num | 1

      else:

         if self.in_code:

            if gpio == self.gpio_0:
               self.code_timeout = self.code_timeout | 1 # timeout gpio 0
            else:
               self.code_timeout = self.code_timeout | 2 # timeout gpio 1

            if self.code_timeout == 3: # both gpios timed out
               self.pi.set_watchdog(self.gpio_0, 0)
               self.pi.set_watchdog(self.gpio_1, 0)
               self.in_code = False
               self.callback(self.bits, self.num,self.entrance)
               return



   def cancel(self):

      """
      Cancel the Wiegand decoder.
      """

      self.cb_0.cancel()
      self.cb_1.cancel()

'''
Buzzer / led will ring if
their variable == True or time.now() <= their_variable_time
this allows for perpetual buzzing (mag contact open) or timed buzzing (eventAction)
'''

E1_buzzer=False
E1_led=False
E2_buzzer=False
E2_led=False

# initialise to 0 ie 1 Jan 1970
E1_buzzer_time=0
E1_led_time=0
E2_buzzer_time=0
E2_led_time=0

gpio_pins_bcm = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]


def activate_buzz_led(entrance) :
   global E1_buzzer,E1_led,E2_buzzer,E2_led
   print("buzzzzzing and led on")
   # for pin in gpio_pins_bcm:
   #    pi.set_mode(pin, pigpio.OUTPUT)
   #    pi.write(pin, 0)
   # pi.write(E1_OUT_Buzz,1)
   # pi.write(E1_IN_Buzz,1)
   # pi.write(E1_OUT_Buzz,1)
   # pi.write(E1_IN_Buzz,1)
   # pi.write(E1_OUT_Led,1)
   # pi.write(E1_IN_Led,1)
   # pi.write(E2_OUT_Led,1)
   # pi.write(E2_IN_Led,1)
   # if entrance == "E1":
   #    E1_buzzer=True
   #    E1_led=True

   # if entrance == "E2":
   #    E2_buzzer=True
   #    E2_led=True

def deactivate_buzz_led(entrance) :
   global E1_buzzer,E1_led,E2_buzzer,E2_led
   if entrance == "E1":
      E1_buzzer=False
      E1_led=False
   
   if entrance == "E2":
      E2_buzzer=False
      E2_led=False

# activate_buzz_led("E1")

# Function to test a pin
def test_pin(pin, duration=2):
    pi.set_mode(pin, pigpio.OUTPUT)
    print(f"Testing {pin}")
    pi.write(pin, 1)  # Turn on
    time.sleep(0.1)  # Short delay before reading back the state
    # Verify the pin is high
    if pi.read(pin) == 1:
        print(f"Pin {pin} is HIGH")
    else:
        print(f"Error: Pin {pin} is not HIGH as expected")
    time.sleep(duration - 0.1)
    pi.write(pin, 0)  # Turn off
    # Verify the pin is low
    time.sleep(0.1)
    if pi.read(pin) == 0:
        print(f"Pin {pin} is LOW")
    else:
        print(f"Error: Pin {pin} is not LOW as expected")
    print(f"Tested {pin}\n")


# Test each pin
# for pin in gpio_pins_bcm:
#     test_pin(pin)

def entrance_id_to_entrance(entrance_id):
   '''Helper function to convert entrance_id to "E1" | "E2"
   
   Args:
      entrance_id: int

   Returns:
      "E1" | "E2"
   '''
   entrance_name = config.get("EntranceName",{})
   if entrance_name.get("E1",None) == entrance_id:
      return "E1"
   if entrance_name.get("E2",None) == entrance_id:
      return "E2"
   # implicit None

def activate_buzz(entrance,t):
   '''Helper function for eventActionTriggers

   entrance: entrance to activate buzzer (either BOTH_ENTRANCES or entrance_id)
   t: time to run buzzer in seconds (int)
   '''
   import eventActionTriggerConstants
   global E1_buzzer_time,E2_buzzer_time

   if entrance is eventActionTriggerConstants.BOTH_ENTRANCE:
      end_time=time.time()+t
      E1_buzzer_time=max(E1_buzzer_time,end_time)
      E2_buzzer_time=max(E2_buzzer_time,end_time)
      return

   ent = entrance_id_to_entrance(entrance)
   if ent == "E1":
      E1_buzzer_time=max(E1_buzzer_time,time.time()+t)
   elif ent == "E2":
      E2_buzzer_time=max(E2_buzzer_time,time.time()+t)

def activate_led(entrance,t):
   '''Helper function for eventActionTriggers

   entrance: entrance to activate led (either BOTH_ENTRANCE or entrance_id)
   t: time to run buzzer in seconds(int)
   '''
   import eventActionTriggerConstants
   global E1_led_time,E2_led_time

   if entrance is eventActionTriggerConstants.BOTH_ENTRANCE:
      end_time=time.time()+t
      E1_led_time=max(E1_led_time,end_time)
      E2_led_time=max(E2_led_time,end_time)
      return

   ent=entrance_id_to_entrance(entrance)
   if ent == "E1":
      E1_led_time=max(E1_led_time,time.time()+t)
   elif ent == "E2":
      E2_led_time=max(E2_led_time,time.time()+t)

def check_for_led_and_buzzer():
    '''Continuous checks the variables above to see if to activate/deactivate buzzer/led'''
    def helper(active,t,pin1,pin2):
        '''helper function to activate pins

            Args: (example)
                active: E1_buzzer
                t: E1_buzzer_time
                pin1: E1_IN_Buzz
                pin2: E1_OUT_Buzz
        '''
        if active or time.time() <= t:
            pi.write(pin1,1)
            pi.write(pin2,1)
        else:
            pi.write(pin1,0)
            pi.write(pin2,0)
    while True:            
        helper(E1_buzzer,E1_buzzer_time,E1_IN_Buzz,E1_OUT_Buzz)
        helper(E1_led,E1_led_time,E1_IN_Led,E2_OUT_Led)
        helper(E2_buzzer,E2_buzzer_time,E2_IN_Buzz,E2_OUT_Buzz)
        helper(E2_led,E2_led_time,E2_IN_Led,E2_OUT_Led)
        time.sleep(1)
        gc.collect()


thread_pool_executor.submit(check_for_led_and_buzzer)
# threading.Thread(target=check_for_led_and_buzzer)
