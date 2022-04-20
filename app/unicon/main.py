import threading
import time


def t():
    print('here')
    while True:
        print("unicon")
        time.sleep(1)

def main():
    t10 = threading.Thread(target=t)
    t10.start()