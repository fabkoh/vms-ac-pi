'''contains the controller code'''
import threading
import time
from json_readers import TestJsonContainer

def run():
    while True:
        print(TestJsonContainer[0])
        time.sleep(1)

def main():
    t1 = threading.Thread(target=run)
    t1.start()
