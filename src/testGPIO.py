import pigpio

pi = pigpio.pi()

Gen_1 = 27
Gen_2 = 13
Gen_3 = 21


pi.set_mode(Gen_1, pigpio.OUTPUT)    
pi.set_mode(Gen_2, pigpio.OUTPUT)
pi.set_mode(Gen_3, pigpio.INPUT)

def listen():
    w = input("Enter Command : ")
    if w == "1":
        pi.write(Gen_1,1)
    if w == "0":
        pi.write(Gen_1,0)

def activate_relay(gpio, level, tick):
    pi.write(Gen_2,1)
    print(pi.read(Gen_2),"activate")
    

def deactivate_relay(gpio, level, tick):
    pi.write(Gen_2,0)
    print(pi.read(Gen_2),"deactivate")



cb = pi.callback(Gen_3, pigpio.FALLING_EDGE, activate_relay)
cb1 = pi.callback(Gen_3, pigpio.RISING_EDGE, deactivate_relay)
   
while True:
    listen()


#pi.write(Gen_2,0)
