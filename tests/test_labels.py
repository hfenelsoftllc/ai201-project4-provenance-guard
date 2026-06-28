"""Tests for label dispatch — label text is part of the public API contract."""
import pytest
from app.utils.labels import generate_label, LABEL_LIKELY_AI, LABEL_LIKELY_HUMAN, LABEL_UNCERTAIN


def test_likely_ai_label():
    assert generate_label("likely_ai") == LABEL_LIKELY_AI


def test_likely_human_label():
    assert generate_label("likely_human") == LABEL_LIKELY_HUMAN


def test_uncertain_label():
    assert generate_label("uncertain") == LABEL_UNCERTAIN


def test_unknown_attribution_raises():
    with pytest.raises(ValueError, match="Unknown attribution value"):
        generate_label("maybe_ai")


def test_labels_contain_key_phrases():
    assert "AI-Assisted Content" in LABEL_LIKELY_AI
    assert "Human-Authored Content" in LABEL_LIKELY_HUMAN
    assert "Attribution Unclear" in LABEL_UNCERTAIN


def test_ai_label_mentions_appeal():
    # Appeals call-to-action must be present for AI label
    assert "appeal" in LABEL_LIKELY_AI.lower()


def test_uncertain_label_mentions_appeal():
    assert "appeal" in LABEL_UNCERTAIN.lower()
