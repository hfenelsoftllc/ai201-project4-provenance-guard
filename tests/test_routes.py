"""Integration tests for Flask routes via test client."""
import pytest
from unittest.mock import patch
from app.main import create_app
from app.models import audit_log
from app.models import creators as creators_model


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_log, "DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setattr(creators_model, "DB_PATH", str(tmp_path / "test.db"))
    audit_log._init()
    creators_model._init()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _submit(client, text="hello world", creator_id="u1", llm=0.9, stylo=0.9, rep=0.9,
            content_type="text"):
    with patch("app.routes.submit.classify_with_llm", return_value=llm), \
         patch("app.routes.submit.classify_with_stylometrics", return_value=stylo), \
         patch("app.routes.submit.classify_with_repetition", return_value=rep):
        return client.post("/submit", json={
            "text": text, "creator_id": creator_id, "content_type": content_type
        })


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


# ── POST /verify ──────────────────────────────────────────────────────────────

def test_verify_missing_fields_400(client):
    r = client.post("/verify", json={})
    assert r.status_code == 400


def test_verify_creates_pending(client):
    r = client.post("/verify", json={"creator_id": "creator1", "attestation": "I am human."})
    assert r.status_code == 201
    assert r.get_json()["status"] == "pending"


def test_verify_duplicate_409(client):
    client.post("/verify", json={"creator_id": "creator1", "attestation": "first"})
    r = client.post("/verify", json={"creator_id": "creator1", "attestation": "second"})
    assert r.status_code == 409


def test_verify_approve_success(client):
    client.post("/verify", json={"creator_id": "creator1", "attestation": "I am human."})
    r = client.post("/verify/creator1/approve")
    assert r.status_code == 200
    assert r.get_json()["status"] == "verified"


def test_verify_approve_not_found_404(client):
    r = client.post("/verify/nobody/approve")
    assert r.status_code == 404


# ── GET /dashboard ────────────────────────────────────────────────────────────

def test_dashboard_returns_200(client):
    r = client.get("/dashboard")
    assert r.status_code == 200


def test_dashboard_shape(client):
    r = client.get("/dashboard")
    data = r.get_json()
    assert "total_submissions" in data
    assert "attribution_distribution" in data
    assert "appeal_rate" in data
    assert "signal_agreement_rate" in data


def test_dashboard_reflects_submissions(client):
    _submit(client, llm=1.0, stylo=1.0, rep=1.0)
    _submit(client, llm=0.0, stylo=0.0, rep=0.0)
    r = client.get("/dashboard")
    data = r.get_json()
    assert data["total_submissions"] == 2


# ── S4: content_type ──────────────────────────────────────────────────────────

def test_submit_image_description_accepted(client):
    r = _submit(client, content_type="image_description")
    assert r.status_code == 200
    assert r.get_json()["content_type"] == "image_description"


def test_submit_default_content_type_is_text(client):
    r = _submit(client)
    assert r.get_json()["content_type"] == "text"
