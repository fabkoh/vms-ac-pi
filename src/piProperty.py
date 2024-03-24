import subprocess
import re
import time
import logging
import threading

# Create a logger
logger = logging.getLogger(__name__)

# Set the level of logging. It can be DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.setLevel(logging.DEBUG)

# Create a file handler for outputting log messages to a file
file_handler = logging.FileHandler('/home/etlas/logfilePiProperty.log')

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)

def get_cpu_temperature():
    result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
    output = result.stdout.strip()
    temperature = re.findall(r'\d+\.\d+', output)[0]
    return float(temperature)

def get_system_stats():
    result = subprocess.run(['top', '-bn', '1'], capture_output=True, text=True)
    output = result.stdout.strip().split('\n')

    cpu_line = output[2]
    cpu_usage = re.findall(r'\d+\.\d+', cpu_line)[0]

    mem_line = output[3]
    mem_info = re.findall(r'\d+\.\d+', mem_line)
    total_mem = float(mem_info[0])
    free_mem = float(mem_info[1])
    used_mem = total_mem - free_mem
    ram_percentage = (used_mem / total_mem) * 100


    return {
        'cpu_temperature': get_cpu_temperature(),
        'ram_usage_percentage': ram_percentage,
        'cpu_usage_percentage': float(cpu_usage)
    }

def log_system_stats(interval, duration):
    start_time = time.time()
    end_time = start_time + duration

    while time.time() < end_time:
        stats = get_system_stats()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log = f'{timestamp} - CPU Temp: {stats["cpu_temperature"]}°C, RAM Usage: {stats["ram_usage_percentage"]:.2f}%, CPU Usage: {stats["cpu_usage_percentage"]:.2f}%'
        print(log)
        logger.info(log + str(threading.activeCount()))

        time.sleep(interval)

# Example usage: Log system stats every 5 seconds for 1 minute
# log_system_stats(5, 60)
