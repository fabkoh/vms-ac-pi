import time

class TimerException(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            print("Timer is running. Use .stop() to stop it")
            return 
            raise TimerException(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            print("Timer is not running. Use .start() to start it")
            return 
            raise TimerException(f"Timer is not running. Use .start() to start it")
            
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
    
    def check(self,TIME):
        """return True if current_elapsed_time exceeds TIME"""
        if self._start_time is None:
            print("Timer is not running. Use .start() to start it")
            return 
            
        current_elapsed_time = time.perf_counter() - self._start_time
        if current_elapsed_time > TIME:
            return True
        
        return False

    def status(self):
        """return True if timing has started"""
        if self._start_time:
            return True 
        return False