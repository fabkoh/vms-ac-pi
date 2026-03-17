# vms-ac-pi

Raspberry Pi controller for the **VMS-AC Access Control** system.

Runs a Flask API (`src/api.py`) and a main event loop (`src/program.py`) that read
Wiegand card/PIN readers, control relays, and sync credentials with the backend server.

---

## Prerequisites

- Python 3
- Install dependencies: `python3 -m pip install -r requirements.txt`
- Also install test tools: `pip install pytest freezegun`

---

## Running (on the Pi)

Start via systemd:
```bash
sudo systemctl start api.service
sudo systemctl start maincontroller.service
```

---

## Running Tests

Tests run on **any machine** — no Raspberry Pi hardware needed. All GPIO and hardware
modules (`pigpio`, `RPi.GPIO`) are mocked automatically by `tests/conftest.py`.

**Run all tests:**
```bash
cd vms-ac-pi
python -m pytest tests/ -v
```

**Run a single test file:**
```bash
python -m pytest tests/test_reader_detects_bits.py -v
```

Test files are in `tests/`. Source code under test is in `src/`.
