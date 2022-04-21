import pigpio

class Decoder:
    '''???'''

    #callback refers to the function that is being called when the wiegand reader reads an input 
    #entrance refers to the particular entrance and reader e.g. E1R1
    def __init__(self, pi, gpio_0, gpio_1, callback, entrance, bit_timeout=5):
        '''initialises decoder
        
        Args:
            pi (gpio pi)
            gpio_0 (int): the pin number
            gpio_1 (int): the pin number
            callback (func): function to execute when reader detects an input
                calls the function with inputs bits, value, entrance ???
            entrance (string): the entrance name ( 'E1_IN' | 'E1_OUT' | 'E2_IN' | 'E2_OUT' )

        Returns:
            Decoder object
        '''
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
            
    def _cb(self, gpio, level, tick):
        '''accumulates bits until d0 and d1 timeout

        Args:
            gpio (int): the gpio pin ( self.gpio_0 | self.gpio_1 )
            level (enum): type of peak to detect ( pigio.RISING_EDGE | pigpio.FALLING_EDGE | pigpio.EITHER_EDGE )
            tick: ??

        Does not return anything, but calls self.callback(bits, num, entrance)
        '''
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
        '''Cancel the Wiegand decoder.'''
        self.cb_0.cancel()
        self.cb_1.cancel()
