import time

class TimerException(Exception):
    '''Exception to raise when timer has an error'''

class Timer:
    '''???'''
    def __init__(self):
        self._start_time = None

    def start(self):
        '''Starts a new timer'''
        if self._start_time is not None:
            print('Timer is running. Use timer.stop() before running timer.start()')
            raise TimerException('Timer is running. Use timer.stop() before running timer.start()')

        self._start_time = time.perf_counter()

    def stop(self):
        '''Stops the timer
        
        Returns:
        elasped_time (float): time in seconds since last self.start()
        '''
        if self._start_time is None:
            print('Timer is not running. Run timer.start() first')
            raise TimerException('Timer is not running. Run timer.start() first')
        
        elasped_time = time.perf_counter() - self._start_time
        self._start_time = None
        print(f'Elapsed time: {elasped_time:0.4f} seconds')
        return elasped_time

    def check(self, t):
        '''returns if elapsed_time exceeds time
        
        Args:
        t (float): time to check against
        
        Returns:
        elapsed (bool): if time > elapsed_time
        '''

        if self._start_time is None:
            print('Timer is not running. Run timer.start() first')
            raise TimerException('Timer is not running. Run timer.start() first')

        return (time.perf_counter() - self._start_time) > t

    def time_started(self):
        '''returns if time has started
        
        Returns:
        started (bool)
        '''
        return self._start_time is not None