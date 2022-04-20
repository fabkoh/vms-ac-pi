import time
import threading

def start():
    print("test")

def t():
    while True:
        print("etet")
        time.sleep(1)

t10 = threading.Thread(target=t)