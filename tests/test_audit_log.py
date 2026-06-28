"""Tests for audit log persistence — uses temp DB via monkeypatch."""
import pytest
from app.models import audit_log


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_log, "DB_PATH", str(tmp_path / "test.db"))
    audit_log._init()


def _entry(**overrides):
    base = {
        "content_id": "aaaaaaaa-0000-0000-0000-000000000001",
        "creator_id": "creator1",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "attribution": "likely_ai",
        "confidence": 0.8,
        "llm_score": 0.9,
        "stylometric_score": 0.6,
        "repetition_score": 0.7,
        "content_type": "text",
        "status": "classified",
        "appeal_reasoning": None,
        "appeal_timestamp": None,
    }
    base.update(overrides)
    return base


def test_write_and_read_back():
    audit_log.write_entry(_entry())
    entries = audit_log.get_entries()
    assert len(entries) == 1
    assert entries[0]["content_id"] == "aaaaaaaa-0000-0000-0000-000000000001"
    assert entries[0]["attribution"] == "likely_ai"


def test_get_entries_empty():
    assert audit_log.get_entries() == []


def test_get_entry_by_id_found():
    audit_log.write_entry(_entry())
    found = audit_log.get_entry_by_id("aaaaaaaa-0000-0000-0000-000000000001")
    assert found is not None
    assert found["confidence"] == pytest.approx(0.8)


def test_get_entry_by_id_missing():
    assert audit_log.get_entry_by_id("nonexistent") is None


def test_update_appeal_transitions_status():
    audit_log.write_entry(_entry())
    result = audit_log.update_appeal(
        "aaaaaaaa-0000-0000-0000-000000000001", "I wrote this myself."
    )
    assert result is True
    row = audit_log.get_entry_by_id("aaaaaaaa-0000-0000-0000-000000000001")
    assert row["status"] == "under_review"
    assert row["appeal_reasoning"] == "I wrote this myself."
    assert row["appeal_timestamp"] is not None


def test_update_appeal_duplicate_raises():
    audit_log.write_entry(_entry())
    audit_log.update_appeal("aaaaaaaa-0000-0000-0000-000000000001", "first")
    with pytest.raises(ValueError):
        audit_log.update_appeal("aaaaaaaa-0000-0000-0000-000000000001", "second")


def test_update_appeal_not_found_returns_false():
    result = audit_log.update_appeal("nonexistent", "reasoning")
    assert result is False


def test_get_entries_limit():
    for i in range(5):
        audit_log.write_entry(_entry(content_id=f"id-{i:04d}"))
    assert len(audit_log.get_entries(limit=3)) == 3


def test_get_entries_newest_first():
    for i in range(3):
        audit_log.write_entry(_entry(
            content_id=f"id-{i:04d}",
            timestamp=f"2026-01-0{i+1}T00:00:00+00:00"
        ))
    entries = audit_log.get_entries()
    timestamps = [e["timestamp"] for e in entries]
    assert timestamps == sorted(timestamps, reverse=True)


# ── get_analytics ─────────────────────────────────────────────────────────────

def test_analytics_empty_db():
    result = audit_log.get_analytics()
    assert result["total_submissions"] == 0
    assert result["appeal_rate"] == 0.0
    assert result["signal_agreement_rate"] == 0.0


def test_analytics_counts_attributions():
    audit_log.write_entry(_entry(content_id="a1", attribution="likely_ai", llm_score=0.9, stylometric_score=0.8))
    audit_log.write_entry(_entry(content_id="a2", attribution="likely_human", llm_score=0.2, stylometric_score=0.1))
    audit_log.write_entry(_entry(content_id="a3", attribution="uncertain", llm_score=0.6, stylometric_score=0.3))
    result = audit_log.get_analytics()
    assert result["total_submissions"] == 3
    assert result["attribution_distribution"]["likely_ai"] == 1
    assert result["attribution_distribution"]["likely_human"] == 1
    assert result["attribution_distribution"]["uncertain"] == 1


def test_analytics_appeal_rate():
    audit_log.write_entry(_entry(content_id="b1"))
    audit_log.write_entry(_entry(content_id="b2"))
    audit_log.update_appeal("b1", "reason")
    result = audit_log.get_analytics()
    assert result["appeal_rate"] == 0.5


def test_analytics_signal_agreement():
    # Both high → agree
    audit_log.write_entry(_entry(content_id="c1", llm_score=0.8, stylometric_score=0.7))
    # Both low → agree
    audit_log.write_entry(_entry(content_id="c2", llm_score=0.2, stylometric_score=0.3))
    # Disagree
    audit_log.write_entry(_entry(content_id="c3", llm_score=0.8, stylometric_score=0.2))
    result = audit_log.get_analytics()
    assert result["signal_agreement_rate"] == pytest.approx(2 / 3, abs=0.001)
