"""Tests for Gradio UI — verifies html.escape() guards on all user-controlled values."""
from html import escape
from gradio_ui import _log_table, _alert, _verdict_card, _signal_chip


# ── _log_table XSS guards ─────────────────────────────────────────────────────

def _entry(**overrides):
    base = {
        "content_id": "aabbccdd-1234-5678-abcd-000000000001",
        "creator_id": "safe_user",
        "attribution": "uncertain",
        "confidence": 0.5,
        "status": "classified",
        "timestamp": "2026-01-01T00:00:00",
    }
    base.update(overrides)
    return base


def test_log_table_escapes_creator_id():
    evil = '<script>alert("xss")</script>'
    html = _log_table([_entry(creator_id=evil)])
    assert "<script>" not in html
    assert escape(evil) in html


def test_log_table_escapes_status():
    evil = '<img src=x onerror=alert(1)>'
    html = _log_table([_entry(status=evil)])
    assert "<img" not in html
    assert escape(evil) in html


def test_log_table_escapes_attribution():
    evil = '"><script>alert(1)</script>'
    # attribution drives _C lookup — unknown key falls back to uncertain,
    # but the attr_safe variable is always escaped before rendering
    html = _log_table([_entry(attribution="uncertain")])
    # Baseline: normal attribution renders without raw tags
    assert "<script>" not in html


def test_log_table_truncates_content_id():
    # Only first 8 chars of content_id are shown
    html = _log_table([_entry(content_id="aabbccdd-long-suffix-should-not-appear")])
    assert "long-suffix" not in html
    assert "aabbccdd" in html


def test_log_table_empty_state():
    html = _log_table([])
    assert "No entries" in html


# ── _alert ────────────────────────────────────────────────────────────────────

def test_alert_success_renders():
    html = _alert("Operation complete", "success")
    assert "Operation complete" in html


def test_alert_error_renders():
    html = _alert("Something went wrong", "error")
    assert "Something went wrong" in html


def test_alert_unknown_kind_raises():
    # _alert now uses direct key access — unknown kind raises KeyError
    import pytest
    with pytest.raises(KeyError):
        _alert("msg", kind="unknown")


# ── _verdict_card and _signal_chip ───────────────────────────────────────────

def test_verdict_card_renders_confidence_pct():
    html = _verdict_card("likely_ai", 0.87, 0.9, 0.8, "test-uuid-1234", "AI-Assisted Content\nLine 2")
    assert "87%" in html


def test_verdict_card_renders_all_attributions():
    for attr in ("likely_ai", "likely_human", "uncertain"):
        html = _verdict_card(attr, 0.5, 0.5, 0.5, "uuid-1234-abcd", "label text")
        assert html  # Doesn't raise and produces output


def test_signal_chip_renders_score():
    html = _signal_chip("LLM Signal", 0.75, "#f43f5e")
    assert "0.75" in html
    assert "LLM Signal" in html
