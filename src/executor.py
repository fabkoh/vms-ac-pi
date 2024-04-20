import gc
import time
# from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import logging

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/home/etlas/ThreadPool.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class ThreadTaskManager:
    def _init_(self, max_workers):
        self.max_workers = max_workers
        self.lock = threading.Lock()
        self.task_id_counter = 0
        self.active_tasks = {}
        self.threads = []
        self.monitoring_thread = threading.Thread(target=self._monitor_queue_length)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def submit(self, func, *args, **kwargs):
        with self.lock:
            if len(self.threads) >= self.max_workers:
                logger.warning("Max workers limit reached. Waiting for an available slot.")
                while len(self.threads) >= self.max_workers:
                    time.sleep(1)  # Wait for a slot to become available
                
            task_id = self.task_id_counter
            self.task_id_counter += 1
            thread = threading.Thread(target=self._run, args=(task_id, func) + args, kwargs=kwargs)
            thread.daemon = True
            self.threads.append(thread)
            self.active_tasks[task_id] = func._name_  # Track task by name
            logger.info(f"Task {task_id} submitted: {func._name_}. Total submitted: {len(self.active_tasks)}")
            thread.start()

    def _run(self, task_id, func, *args, **kwargs):
        logger.info(f"Thread started running task {task_id}: {func._name_}")
        result = func(*args, **kwargs)
        logger.info(f"Thread completed task {task_id}: {func._name_}")
        self._task_complete(task_id)
        return result

    def _task_complete(self, task_id):
        with self.lock:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
                self.threads = [t for t in self.threads if t.is_alive()]
        logger.info(f"Task {task_id} completed. Total remaining: {len(self.active_tasks)}")

    def get_queue_length(self):
        with self.lock:
            return len(self.active_tasks)

    def _monitor_queue_length(self):
        while True:
            queue_length = self.get_queue_length()
            logger.info(f"Current queue length: {queue_length}")
            time.sleep(60 * 30)  # Every 30 minutes
            gc.collect()

    def shutdown(self, wait=True):
        logger.info("Shutting down all active threads.")
        for thread in self.threads:
            if thread.is_alive():
                if wait:
                    thread.join()
                else:
                    thread._stop()
        self.monitoring_thread.join()

# Usage
max_workers = 16
thread_pool_executor = ThreadTaskManager(max_workers=max_workers)
