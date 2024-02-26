import threading

# Create a lock for each file
pending_logs_lock = threading.Lock()
archived_logs_lock = threading.Lock()
config_lock = threading.Lock()
