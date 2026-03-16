"""
Tests for the Flask routes in src/api.py using the Flask test client.

Two critical routes:
  POST /api/credOccur  — receives credOccur JSON, writes file, reloads in-memory state
  GET  /api/unlock/entrance/<id>  — remote unlock (admin click → Pi relay)
"""

import json
import pytest

import events
import api as flask_api


# ---------------------------------------------------------------------------
# Test client fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    flask_api.app.config["TESTING"] = True
    with flask_api.app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# POST /api/credOccur
# ---------------------------------------------------------------------------

@pytest.fixture
def cred_occur_setup(tmp_path, monkeypatch):
    """Set up the path, json directory, and default no-op callbacks."""
    monkeypatch.setattr(flask_api, "path", str(tmp_path))
    (tmp_path / "json").mkdir(exist_ok=True)
    monkeypatch.setattr(events, "update_credOccur", lambda: None)
    monkeypatch.setattr(events, "check_entrance_status", lambda: None)
    return tmp_path


class TestCredOccurRoute:

    def test_returns_200(self, client, cred_occur_setup):
        data = {"Entrances": [], "CredentialLookup": {}}
        resp = client.post(
            "/api/credOccur",
            data=json.dumps(data),
            content_type="application/json",
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/unlock/entrance/<id>
# ---------------------------------------------------------------------------

class TestUnlockEntranceRoute:

    def test_returns_200(self, client, monkeypatch):
        monkeypatch.setattr(events, "open_door_using_entrance_id", lambda eid: None)
        resp = client.get("/api/unlock/entrance/1")
        assert resp.status_code == 200

    def test_calls_open_door_with_entrance_id(self, client, monkeypatch):
        called_with = []
        monkeypatch.setattr(
            events, "open_door_using_entrance_id",
            lambda eid: called_with.append(eid)
        )
        client.get("/api/unlock/entrance/3")
        # The route calls int(entrance_id), so the value is an integer
        assert called_with == [3]

    def test_different_entrance_ids(self, client, monkeypatch):
        called_with = []
        monkeypatch.setattr(
            events, "open_door_using_entrance_id",
            lambda eid: called_with.append(eid)
        )
        client.get("/api/unlock/entrance/1")
        client.get("/api/unlock/entrance/2")
        assert called_with == [1, 2]


# ---------------------------------------------------------------------------
# POST /api/entrance-name — input validation (400 paths)
# ---------------------------------------------------------------------------

class TestEntranceNameRoute:

    def test_missing_key_returns_400(self, client):
        """Request without the required 'E2' key must be rejected before any file I/O."""
        resp = client.post(
            "/api/entrance-name",
            data=json.dumps({"E1": "MainDoor", "controllerSerialNo": "SERIAL"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_wrong_serial_returns_400(self, client):
        """A serial number that doesn't match the Pi's config must be rejected with 400.

        Uses the real src/json/config.json (serial: 100000005f34ee9d).
        The route reads the file before the serial check, so no monkeypatching
        of api.path is needed — the real file is always present.
        """
        resp = client.post(
            "/api/entrance-name",
            data=json.dumps({
                "E1": "MainDoor",
                "E2": "SideDoor",
                "controllerSerialNo": "WRONG_SERIAL",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/config — serial validation (was a bare assert, now a proper 400)
# ---------------------------------------------------------------------------

class TestConfigRoute:

    def test_missing_required_fields_returns_400(self, client):
        """Request missing one of the three required fields must be rejected with 400."""
        resp = client.post(
            "/api/config",
            data=json.dumps({"controllerIPStatic": False, "controllerIP": "192.168.1.1"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_wrong_serial_returns_400(self, client, tmp_path, monkeypatch):
        """A serial number that doesn't match the stored config must return 400.

        The original code used bare ``assert`` here, which raised AssertionError
        (→ 500) instead of returning 400.  The fix replaces the assert with an
        explicit ``flask.abort(400)`` so the route behaves consistently with
        every other validation check in api.py.
        """
        monkeypatch.setattr(flask_api, "path", str(tmp_path))
        (tmp_path / "json").mkdir()
        config_data = {"controllerConfig": {"controllerSerialNo": "REAL_SERIAL"}}
        (tmp_path / "json" / "config.json").write_text(json.dumps(config_data))

        resp = client.post(
            "/api/config",
            data=json.dumps({
                "controllerIPStatic": False,
                "controllerIP": "192.168.1.1",
                "controllerSerialNo": "WRONG_SERIAL",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400
