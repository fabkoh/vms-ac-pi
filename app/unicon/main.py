import threading
import time
from app.helpers.system import healthcheck

def t():
    print('here')
    while True:
        print("unicon")
        time.sleep(1)

def main():
    # healthcheck()
    t10 = threading.Thread(target=t)
    t10.start()