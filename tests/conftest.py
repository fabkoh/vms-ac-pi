"""
conftest.py — runs before any test module is imported.

Responsibilities:
1. Mock pigpio and RPi.GPIO so the src/ modules load on non-Pi hardware (incl. CI).
2. Add src/ to sys.path so test files can do `import events`, `import api`, etc.
3. Disable the thread pool executor so hardware buzzer/LED tasks don't block pytest exit.

The actual src/json/config.json and src/json/credOccur.json files already exist in
the repo and are used when events.py initialises at import time.  Individual tests
that need different credential data should monkeypatch `events.credOccur` directly.
"""

import sys
import os
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# 1. Mock hardware modules BEFORE any src import occurs
# ---------------------------------------------------------------------------
pigpio_mock = MagicMock()
pigpio_mock.pi.return_value = MagicMock()
pigpio_mock.INPUT = 0
pigpio_mock.OUTPUT = 1
pigpio_mock.FALLING_EDGE = 0
pigpio_mock.TIMEOUT = 2
pigpio_mock.PUD_UP = 20

sys.modules["pigpio"] = pigpio_mock
sys.modules["RPi"] = MagicMock()
sys.modules["RPi.GPIO"] = MagicMock()

# var.py is a local-only config file (gitignored); stub it for tests
var_mock = MagicMock()
var_mock.server_url = "http://localhost:8082"
sys.modules["var"] = var_mock

# netifaces is a Pi OS package not available on CI/dev
sys.modules["netifaces"] = MagicMock()

# program.py starts infinite-loop threads at import time; mock it out entirely
sys.modules["program"] = MagicMock()

# api.py calls app.run() unconditionally at module level; prevent it from binding a port
import flask
flask.Flask.run = lambda *args, **kwargs: None

# ---------------------------------------------------------------------------
# 2. Add src/ to sys.path
# ---------------------------------------------------------------------------
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# ---------------------------------------------------------------------------
# 3. Disable the thread pool executor
#    led_and_buzzer_correct_cred / led_and_buzzer_wrong_cred submit tasks that
#    call time.sleep(2) in worker threads.  Python's ThreadPoolExecutor atexit
#    handler blocks on shutdown(wait=True), preventing pytest from exiting.
#    Replace submit() with a no-op so hardware tasks are silently skipped in tests.
# ---------------------------------------------------------------------------
import executor
executor.thread_pool_executor.executor.shutdown(wait=False)
executor.thread_pool_executor.submit = lambda func, *args, **kwargs: None
