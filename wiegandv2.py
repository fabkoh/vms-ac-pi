#!/usr/bin/env python
# This version uses 2 sets of  EMLOCK, Wiegand reader and pushbutton.
# 1 set is nearby, the other set is at 50m away.

import pigpio
import relay_one
import relay_two
import threading
#import usbrelaytest

class decoder:

   """
   A class to read Wiegand codes of an arbitrary length.

   The code length and value are returned.

   EXAMPLE

   #!/usr/bin/env python

   import time

   import pigpio

   import wiegand

   def callback(bits, code):
      print("bits={} code={}".format(bits, code))

   pi = pigpio.pi()

   w = wiegand.decoder(pi, 14, 15, callback)

   time.sleep(300)

   w.cancel()

   pi.stop()
   """

   def __init__(self, pi, gpio_0, gpio_1, callback, bit_timeout=5):

      """
      Instantiate with the pi, gpio for 0 (green wire), the gpio for 1
      (white wire), the callback function, and the bit timeout in
      milliseconds which indicates the end of a code.

      The callback is passed the code length in bits and the value.
      """

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

if __name__ == "__main__":

    import time

    import pigpio

    import wiegandEntOne
    
    from datetime import datetime
    
    
    def callback(bits, value):
      print("bits={} value={}".format(bits, value))
      
      #check for auth method, if requires fingerprint and card
          #check if value is in fingerprint of Credentials
              # check if the other value is in card of the same Credentials
          #check if value is in card of Credentials
              # check if the other value is in fingerprint of the same Credentials
      
      if value == 36443419 or value == 36443438:
          print("Authenticated")
          relay_one.trigger_relay()
    

    
      

    
    
    pi = pigpio.pi()
    #initialising pin5 for pushbutton1
    pi.set_mode(5, pigpio.INPUT)
    #print(pi.read(5))
    pi.set_pull_up_down(5, pigpio.PUD_UP)
    #print(pi.read(5))
    #initialising pin19 for pushbutton2
    pi.set_mode(19, pigpio.INPUT)
    #print(pi.read(19))
    pi.set_pull_up_down(19, pigpio.PUD_UP)
    #print(pi.read(19))
    
    pi.set_mode(6, pigpio.INPUT) #pin 6 for mag contact
    pi.set_pull_up_down(6, pigpio.PUD_UP)
    
    w1 = wiegandEntOne.decoder(pi, 22, 10, callback)
    w2 = wiegandEntOne.decoder(pi, 24, 25, callback)
    
    
    
    
    while True: 
        if pi.read(5) == 0:
            print(pi.read(5))
            print("Pb 1 was pushed at " + str(datetime.now()))
            relay_one.trigger_relay()
            
        #if pi.read(19) == 0:
            #print(pi.read(19))
            #print("Pb 2 was pushed at " + str(datetime.now()))
            #relay_two.trigger_relay()
        
        pi.set_pull_up_down(6, pigpio.PUD_UP)
        if pi.read(6) == 1:
            print("Entrance 1 is opened at " + str(datetime.now()))
        pi.set_pull_up_down(6, pigpio.PUD_UP)
        
        #if pi.read(26) == 1:
            #print("Entrance 2 is open!")
        #pi.set_pull_up_down(26, pigpio.PUD_UP)
    #usbrelaytest.magcontact()
    time.sleep(3)
    #while True: 
        #relay_module_test.main()
    

    
    w.cancel()
    
    pi.stop()
    
    


