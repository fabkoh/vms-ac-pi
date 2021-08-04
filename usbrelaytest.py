import usbrelay_py
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 


count = usbrelay_py.board_count()
print("Count: ",count)

boards = usbrelay_py.board_details()
print("Boards: ",boards)

for board in boards:
    print("Board: ",board)
    #relayport = 1
    #while(relayport < board[1]+1):
    result = usbrelay_py.board_control(board[0],1,1)
    
    print("Port: ",1, " is :", result, " state is: ")
    time.sleep(3)
    result = usbrelay_py.board_control(board[0],1,0)
    #print("Port: ",relayport, " is :", result)
    #get_relay_boards()
    print("Port: ",1, " is :", result, " state is: ")
    #relayport += 1
while True: # Run forever
    if GPIO.input(10) == GPIO.HIGH:
        print("Button was pushed!")
        result = usbrelay_py.board_control(board[0],1,1)
        time.sleep(3)
        result = usbrelay_py.board_control(board[0],1,0)
#    relay = 1
#    while(relay < board[1]+1):
#        result = usbrelay_py.board_control(board[0],relay,0)
#        print("Result: ",result)
#        relay += 1