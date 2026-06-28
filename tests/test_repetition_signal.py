"""Tests for repetition density signal — Signal 3."""
from app.signals.repetition_signal import classify_with_repetition, MIN_WORDS_FOR_REPETITION


def test_short_text_returns_neutral():
    assert classify_with_repetition("hello world") == 0.5


def test_short_text_just_under_threshold():
    words = ["word"] * (MIN_WORDS_FOR_REPETITION - 1)
    assert classify_with_repetition(" ".join(words)) == 0.5


def test_high_repetition_returns_one():
    # All same bigram — maximum repetition → AI-like = 1.0
    words = ["the"] * 60
    score = classify_with_repetition(" ".join(words))
    assert score == 1.0


def test_low_repetition_returns_zero():
    # 60 unique consecutive words — no repeated bigrams → human-like = 0.0
    words = [f"word{i}" for i in range(60)]
    score = classify_with_repetition(" ".join(words))
    assert score == 0.0


def test_score_in_range():
    # Mixed text — should be between 0 and 1
    text = " ".join(["the cat sat on the mat the cat looked around"] * 8)
    score = classify_with_repetition(text)
    assert 0.0 <= score <= 1.0


def test_empty_string_returns_neutral():
    assert classify_with_repetition("") == 0.5


def test_score_is_float():
    words = ["hello world this is a test " * 12]
    score = classify_with_repetition(" ".join(words))
    assert isinstance(score, float)
