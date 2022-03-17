from GPIOconfig import *
from events import *
import threading
import pigpio 

'''
    1. main program that runs everything 
    2. when detects wiegand readings, imports verify.py
    3. when detects event, imports verify.py
    4. checks for API calls
'''


e1r1 = decoder(pi, E1_R1_D0, E1_R1_D1, bits_reader,"E1R1") 
e1r2 = decoder(pi, E1_R2_D0, E1_R2_D1, bits_reader,"E1R2")

# def inputnum():
#     while True:
#         value = str(input("Enter value: "))
#         bits = int(input("Enter bits: "))
#         bits_reader(bits,value)


def mag(cbmagrise,cbmagfall):
    cb1 = pi.callback(E1_Mag, pigpio.RISING_EDGE, cbmagrise)
    cb2 = pi.callback(E1_Mag, pigpio.FALLING_EDGE, cbmagfall)
    
    '''
    while True:
        
        if pi.read(6) == 1:
            print("Entrance opened at " + str(datetime.now()))
            
        
        pi.wait_for_edge(6, pigpio.RISING_EDGE)
        print("Entrance 1 is opened at " + str(datetime.now()))
        
        pi.wait_for_edge(6, pigpio.FALLING_EDGE)
        print("Entrance 1 is closed at " + str(datetime.now()))
    ''' 
   
def button(cbbutton):
    
    cb3 = pi.callback(E1_Button, pigpio.RISING_EDGE, cbbutton)
    
    '''
    while True: 
        if pi.read(5) == 0:
            print(pi.read(5))
            print("Pb 1 was pushed at " + str(datetime.now()))
            relay.trigger_relay_one()
            print("Here")
    '''

t1 = threading.Thread(target=button)
t2 = threading.Thread(target=mag)
t3= threading.Thread(target=check)

t1.start()
t2.start()
t3.start()