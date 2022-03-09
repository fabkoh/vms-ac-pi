import pigpio
import time
import RPi.GPIO as GPIO
from datetime import datetime
import relay
import transactionsMod

class decoder:

   def __init__(self, pi, gpio_0, gpio_1, callback, bit_timeout=5):


      self.pi = pi
      self.gpio_0 = gpio_0
      self.gpio_1 = gpio_1

      self.callback = callback

      self.bit_timeout = bit_timeout

      self.in_code = False

      self.pi.set_mode(gpio_0, pigpio.INPUT)
      self.pi.set_mode(gpio_1, pigpio.INPUT)

      self.pi.set_pull_up_down(gpio_0, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpio_1, pigpio.PUD_UP)

      self.cb_0 = self.pi.callback(gpio_0, pigpio.FALLING_EDGE, self._cb)
      self.cb_1 = self.pi.callback(gpio_1, pigpio.FALLING_EDGE, self._cb)

   def _cb(self, gpio, level, tick):

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
               self.callback(self.bits, self.num)

   def cancel(self):

      """
      Cancel the Wiegand decoder.
      """

      self.cb_0.cancel()
      self.cb_1.cancel()

def callback_e1(bits, value):
    print("bits={} value={}".format(bits, value))
    # if value in list of credid 
    if value == 36443419 or value == 36443438:
        print("Authenticated")
        relay.trigger_relay_one()
        transactionsMod.record(value,reader,exit)

def callback_e2(bits, value):
    print("bits={} value={}".format(bits, value))
    # if value in list of credid 
    if value == 36443419 or value == 36443438:
        print("Authenticated")
        relay.trigger_relay_two()
        transactionsMod.record()

#initialising pi
pi = pigpio.pi()

#initialising E1_Button for pushbutton1
pi.set_mode(E1_Button, pigpio.INPUT)
pi.set_pull_up_down(E1_Button, pigpio.PUD_UP)

#E1_Mag for mag contact
pi.set_mode(E1_Mag, pigpio.INPUT) 
pi.set_pull_up_down(E1_Mag, pigpio.PUD_UP)

#E1_R1_Buzz for Buzz
pi.set_mode(E1_R1_Buzz, pigpio.INPUT) 
pi.set_pull_up_down(E1_R1_Buzz, pigpio.PUD_UP)

#E1_R1_Led for Led
pi.set_mode(E1_R1_Led, pigpio.INPUT) 
pi.set_pull_up_down(E1_R1_Led, pigpio.PUD_UP)

#E1_R2_Buzz for Buzz
pi.set_mode(E1_R2_Buzz, pigpio.INPUT) 
pi.set_pull_up_down(E1_R2_Buzz, pigpio.PUD_UP)

#E1_R2_Led for Led
pi.set_mode(E1_R2_Led, pigpio.INPUT) 
pi.set_pull_up_down(E1_R2_Led, pigpio.PUD_UP)

#initialising E2_Button for pushbutton2
pi.set_mode(E2_Button, pigpio.INPUT)
pi.set_pull_up_down(E2_Button, pigpio.PUD_UP)

#E2_Mag for mag contact
pi.set_mode(E2_Mag, pigpio.INPUT) 
pi.set_pull_up_down(E2_Mag, pigpio.PUD_UP)

#E2_R1_Buzz for Buzz
pi.set_mode(E2_R1_Buzz, pigpio.INPUT) 
pi.set_pull_up_down(E2_R1_Buzz, pigpio.PUD_UP)

#E2_R1_Led for Led
pi.set_mode(E2_R1_Led, pigpio.INPUT) 
pi.set_pull_up_down(E2_R1_Led, pigpio.PUD_UP)

#E2_R1_Buzz for Buzz
pi.set_mode(E2_R2_Buzz, pigpio.INPUT) 
pi.set_pull_up_down(E2_R2_Buzz, pigpio.PUD_UP)

#E2_R1_Led for Led
pi.set_mode(E2_R2_Led, pigpio.INPUT) 
pi.set_pull_up_down(E2_R2_Led, pigpio.PUD_UP)

#wiegand
e1r1 = decoder(pi, E1_R1_D0, E1_R1_D1, callback_e1)
e1r2 = decoder(pi, E1_R2_D0, E1_R2_D1, callback_e1)

e2r1 = decoder(pi, E2_R1_D0, E2_R1_D1, callback_e2)
e2r2 = decoder(pi, E2_R2_D0, E2_R2_D1, callback_e2)



def button_callback_e1(channel):
    if E1_Button:
        print("Pb 1 was pushed at " + str(datetime.now()))
    else:
        print("Pb 1 was released at " + str(datetime.now()))

def button_callback_e2(channel):
    if E2_Button:
        print("Pb 2 was pushed at " + str(datetime.now()))
    else:
        print("Pb 2 was released at " + str(datetime.now()))

def mag_callback_e1(channel):
    if E1_Mag:
        print("Entrance 1 is closed at " + str(datetime.now()))
    else:
        print("Entrance 1 is opened at " + str(datetime.now()))

def mag_callback_e2(channel):
    if E2_Mag:
        print("Entrance 2 is closed at " + str(datetime.now()))
    else:
        print("Entrance 2 is opened at " + str(datetime.now()))


GPIO.add_event_detect(E1_Button,GPIO.BOTH,callback=button_callback_e1)
GPIO.add_event_detect(E2_Button,GPIO.BOTH,callback=button_callback_e2)

E1_opened = False
E2_opened = False

GPIO.add_event_detect(E1_Mag,GPIO.BOTH,callback=mag_callback_e1)
GPIO.add_event_detect(E2_Mag,GPIO.BOTH,callback=mag_callback_e2)










message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up

e1r1.cancel()
e1r2.cancel()
e2r1.cancel()
e2r2.cancel()

pi.stop()

