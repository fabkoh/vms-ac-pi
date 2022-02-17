#import usbrelay_py
import time
import RPi.GPIO as GPIO
import relay_module_test
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(0, GPIO.IN, GPIO.PUD_UP)

#count = usbrelay_py.board_count()
#print("Count: ",count)

#boards = usbrelay_py.board_details()
#print("Boards: ",boards)

#for board in boards:
    #print("Board: ",board)
    #relayport = 1
    #while(relayport < board[1]+1):
    #result = usbrelay_py.board_control(board[0],1,1)
    
    #print("Port: ",1, " is :", result, " state is: ")
    #time.sleep(3)
    #result = usbrelay_py.board_control(board[0],1,0)
    #print("Port: ",relayport, " is :", result)
    #get_relay_boards()
    #print("Port: ",1, " is :", result, " state is: ")
    #relayport += 1
def pushbutton(): 
    while True: # Run forever
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(5, GPIO.IN, GPIO.PUD_UP)
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(0, GPIO.IN, GPIO.PUD_UP) #GPIO 0 is ID_SD
        if GPIO.input(5) == GPIO.LOW:
            print("Button was pushed!")
            relay_module_test.main()

        if GPIO.input(0) == GPIO.HIGH:
            print("Door is open!")
    return
        #result = usbrelay_py.board_control(board[0],1,1)
        #time.sleep(3)
        #result = usbrelay_py.board_control(board[0],1,0)
#    relay = 1
#    while(relay < board[1]+1):
#        result = usbrelay_py.board_control(board[0],relay,0)
#        print("Result: ",result)
#        relay += 1