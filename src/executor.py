from datetime import datetime
import gc
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import heapq
import logging

def setup_logger(log_filename="ThreadPool.log"):
    # Determine the home directory dynamically
    home_dir = os.path.expanduser("~")
    
    # Define the log file path
    log_dir = os.path.join(home_dir, "logs")
    log_file = os.path.join(log_dir, log_filename)
    
    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    
    # Create formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger('ThreadPool.log')

class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0
        self._lock = threading.Lock()
    
    def put(self, priority, task):
        with self._lock:
            heapq.heappush(self._queue, (priority, self._index, task))
            self._index += 1
    
    def get(self):
        with self._lock:
            if self._queue:
                return heapq.heappop(self._queue)[2]
            else:
                return None
    
    def is_empty(self):
        with self._lock:
            return not self._queue

class ThreadPoolMonitor:
    def __init__(self, max_workers):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()
        self.task_id_counter = 0
        self.active_tasks = {}
        self.queue = PriorityQueue()
        self.monitoring_thread = threading.Thread(target=self._monitor_queue_length)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

        # Start a thread to handle high-priority tasks
        self.priority_thread = threading.Thread(target=self._process_priority_tasks)
        self.priority_thread.daemon = True
        self.priority_thread.start()

    def submit(self, func, *args, priority=0, **kwargs):
        with self.lock:
            task_id = self.task_id_counter
            self.task_id_counter += 1
            self.active_tasks[task_id] = func.__name__  # Track task by name
        print(task_id, " task created: ", datetime.now())
        logger.info(f"Task {task_id} submitted: {func.__name__}. Total submitted: {len(self.active_tasks)}")
        self.queue.put(priority, (task_id, func, args, kwargs))

    def _process_priority_tasks(self):
        while True:
            task = self.queue.get()
            if task:
                task_id, func, args, kwargs = task
                print(task_id, " executing task: ", datetime.now())
                future = self.executor.submit(self._run, task_id, func, *args, **kwargs)
                future.add_done_callback(lambda f: self._task_complete(task_id, f))
            time.sleep(0.1)  # Poll every 0.1 seconds to check for new tasks

    def _run(self, task_id, func, *args, **kwargs):
        print(task_id, " thread running: ", datetime.now())
        logger.info(f"Thread started running task {task_id}: {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"Thread completed task {task_id}: {func.__name__}")
        return result

    def _task_complete(self, task_id, future):
        print(task_id, " thread completed: ", datetime.now())
        with self.lock:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
        logger.info(f"Task {task_id} completed. Total remaining: {len(self.active_tasks)}")

    def get_queue_length(self):
        with self.lock:
            return len(self.active_tasks)

    def _monitor_queue_length(self):
        while True:
            queue_length = self.get_queue_length()
            logger.info(f"Current queue length: {queue_length}")
            time.sleep(60*30)  # Every 30 minutes
            gc.collect()

    def shutdown(self, wait=True):
        logger.info("Shutting down thread pool.")
        self.executor.shutdown(wait=wait)

# Usage
max_workers = 16
thread_pool_executor = ThreadPoolMonitor(max_workers=max_workers)
