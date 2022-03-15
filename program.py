from GPIOconfig import *
from verify import callback_e1,Timer
import threading





timeout_cred = Timer()
timeout_mag = Timer()
e1r1 = decoder(pi, E1_R1_D0, E1_R1_D1, callback_e1)
e1r2 = decoder(pi, E1_R2_D0, E1_R2_D1, callback_e1)

def inputnum():
    while True:
        value = str(input("Enter value: "))
        bits = int(input("Enter bits: "))
        callback_e1(bits,value)

def check():
    while True:
        if timeout_cred.status(): 
            if timeout_cred.check(CRED_TIMEOUT):
                timeout_cred.stop()
                del credentials [:]

        if timeout_mag.status():
            if timeout_mag.check(MAG_TIMEOUT):
                print("BUZZZZZZZZZZZZZZZZZZ")

        time.sleep(0.1)



t1 = threading.Thread(target=button)
t2 = threading.Thread(target=mag)
t3=threading.Thread(target=check,)

t1.start()
t2.start()
t3.start()