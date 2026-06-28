"""Integration tests for Flask routes via test client."""
import pytest
from unittest.mock import patch
from app.main import create_app
from app.models import audit_log


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_log, "DB_PATH", str(tmp_path / "test.db"))
    audit_log._init()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _submit(client, text="hello world", creator_id="u1", llm=0.9, stylo=0.9):
    with patch("app.routes.submit.classify_with_llm", return_value=llm), \
         patch("app.routes.submit.classify_with_stylometrics", return_value=stylo):
        return client.post("/submit", json={"text": text, "creator_id": creator_id})


# ── POST /submit ─────────────────────────────────────────────────────────────

def test_submit_missing_fields_400(client):
    r = client.post("/submit", json={})
    assert r.status_code == 400


def test_submit_missing_text_400(client):
    r = client.post("/submit", json={"creator_id": "u1"})
    assert r.status_code == 400


def test_submit_missing_creator_400(client):
    r = client.post("/submit", json={"text": "hello"})
    assert r.status_code == 400


def test_submit_returns_required_fields(client):
    r = _submit(client)
    assert r.status_code == 200
    data = r.get_json()
    for key in ("content_id", "attribution", "confidence", "label", "timestamp"):
        assert key in data


def test_submit_high_scores_give_likely_ai(client):
    r = _submit(client, llm=1.0, stylo=1.0)
    assert r.get_json()["attribution"] == "likely_ai"


def test_submit_low_scores_give_likely_human(client):
    r = _submit(client, llm=0.0, stylo=0.0)
    assert r.get_json()["attribution"] == "likely_human"


def test_submit_mid_scores_give_uncertain(client):
    r = _submit(client, llm=0.5, stylo=0.5)
    assert r.get_json()["attribution"] == "uncertain"


def test_submit_llm_failure_503(client):
    with patch("app.routes.submit.classify_with_llm", side_effect=Exception("timeout")):
        r = client.post("/submit", json={"text": "hello", "creator_id": "u1"})
    assert r.status_code == 503


def test_submit_writes_to_audit_log(client):
    _submit(client)
    r = client.get("/log")
    assert len(r.get_json()["entries"]) == 1


# ── POST /appeal ─────────────────────────────────────────────────────────────

def test_appeal_missing_fields_400(client):
    r = client.post("/appeal", json={})
    assert r.status_code == 400


def test_appeal_not_found_404(client):
    r = client.post("/appeal", json={"content_id": "nope", "creator_reasoning": "reason"})
    assert r.status_code == 404


def test_appeal_success_200(client):
    content_id = _submit(client).get_json()["content_id"]
    r = client.post("/appeal", json={"content_id": content_id, "creator_reasoning": "I wrote this"})
    assert r.status_code == 200
    assert r.get_json()["status"] == "under_review"


def test_appeal_duplicate_409(client):
    content_id = _submit(client).get_json()["content_id"]
    client.post("/appeal", json={"content_id": content_id, "creator_reasoning": "once"})
    r = client.post("/appeal", json={"content_id": content_id, "creator_reasoning": "twice"})
    assert r.status_code == 409


def test_appeal_updates_log_entry(client):
    content_id = _submit(client).get_json()["content_id"]
    client.post("/appeal", json={"content_id": content_id, "creator_reasoning": "my reason"})
    entries = client.get("/log").get_json()["entries"]
    entry = next(e for e in entries if e["content_id"] == content_id)
    assert entry["status"] == "under_review"
    assert entry["appeal_reasoning"] == "my reason"


# ── GET /log ─────────────────────────────────────────────────────────────────

def test_log_returns_200(client):
    r = client.get("/log")
    assert r.status_code == 200
    assert "entries" in r.get_json()


def test_log_limit_param(client):
    for _ in range(5):
        _submit(client)
    r = client.get("/log?limit=2")
    assert len(r.get_json()["entries"]) == 2
