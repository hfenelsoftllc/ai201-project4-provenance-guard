"""Tests for stylometric signal — normalization boundaries and short-text guard."""
from app.signals.stylometric_signal import (
    classify_with_stylometrics,
    _normalize,
    _compute_ttr,
    _compute_slv,
    MIN_WORDS_FOR_STYLOMETRICS,
)


def test_short_text_returns_neutral():
    assert classify_with_stylometrics("Too short.") == 0.5


def test_exactly_at_min_words_does_not_return_neutral():
    # 50 words — should run the full pipeline, not return 0.5
    text = " ".join(["word"] * MIN_WORDS_FOR_STYLOMETRICS)
    result = classify_with_stylometrics(text)
    # "word word word..." has low TTR and minimal SLV → AI-like (high score)
    assert result != 0.5


def test_normalize_at_ai_threshold():
    # value <= ai_threshold → 1.0
    assert _normalize(5.0, 6.0, 15.0) == 1.0


def test_normalize_at_human_threshold():
    # value >= human_threshold → 0.0
    assert _normalize(15.0, 6.0, 15.0) == 0.0


def test_normalize_midpoint():
    # halfway between 6.0 and 15.0 → 0.5
    assert _normalize(10.5, 6.0, 15.0) == 0.5


def test_normalize_below_ai_threshold():
    assert _normalize(0.0, 6.0, 15.0) == 1.0


def test_normalize_above_human_threshold():
    assert _normalize(20.0, 6.0, 15.0) == 0.0


def test_ttr_all_unique():
    words = "the quick brown fox jumps over lazy dog runs fast".split()
    assert _compute_ttr(words) == 1.0


def test_ttr_all_same():
    words = ["word"] * 50
    assert _compute_ttr(words) == pytest.approx(1 / 50)


def test_slv_uniform_sentences():
    # All sentences same length → std dev ≈ 0
    sentences = ["one two three four five"] * 5
    assert _compute_slv(sentences) == pytest.approx(0.0)


import pytest
