import time
import tracemalloc

from flask import Blueprint

from src.app.utils.helpers import display_top
from src.executor import thread_pool_executor

memory_bp = Blueprint("memory", __name__)


def log_memory_usage_every_hour():
    tracemalloc.start(25)  # Adjust stack depth as needed
    try:
        while True:
            snapshot = tracemalloc.take_snapshot()
            display_top(snapshot)
            time.sleep(3600)  # Adjust time as needed
    finally:
        tracemalloc.stop()


thread_pool_executor.submit(log_memory_usage_every_hour)
