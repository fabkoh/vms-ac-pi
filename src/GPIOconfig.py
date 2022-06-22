import pigpio 
import json
from datetime import datetime
import os
path = os.path.dirname(os.path.abspath(__file__))


'''
   1. script to initialise GPIO pins and all variables, import from config.json
   2. includes class decoder
   3. includes function to detect events 
   3. includes class Timer
'''

fileconfig = open(path +'/json/config.json')
config = json.load(fileconfig)

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

#initialising pi
pi = pigpio.pi()

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

#initialising Gen, check whether IN or OUT is being used
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



def activate_buzz_led(entrance) :
   if entrance == "E1":
      pi.write(E1_IN_Buzz,1)
      pi.write(E1_IN_Led,1)
      pi.write(E1_OUT_Buzz,1)
      pi.write(E1_OUT_Led,1)

   if entrance == "E2":
      pi.write(E2_IN_Buzz,1)
      pi.write(E2_IN_Led,1)
      pi.write(E2_OUT_Buzz,1)
      pi.write(E2_OUT_Led,1)

def deactivate_buzz_led(entrance) :
   if entrance == "E1":
      pi.write(E1_IN_Buzz,0)
      pi.write(E1_IN_Led,0)
      pi.write(E1_OUT_Buzz,0)
      pi.write(E1_OUT_Led,0)
   
   if entrance == "E2":
      pi.write(E2_IN_Buzz,0)
      pi.write(E2_IN_Led,0)
      pi.write(E2_OUT_Buzz,0)
      pi.write(E2_OUT_Led,0)


