"""Tests for confidence scoring — thresholds and weights are load-bearing design decisions."""
from app.utils.confidence import (
    compute_confidence,
    LIKELY_AI_THRESHOLD,
    LIKELY_HUMAN_THRESHOLD,
    ATTRIBUTION_LIKELY_AI,
    ATTRIBUTION_LIKELY_HUMAN,
    ATTRIBUTION_UNCERTAIN,
)


def test_weights():
    # 0.50 * 1.0 + 0.30 * 0.0 + 0.20 * 0.0 = 0.50
    confidence, _ = compute_confidence(1.0, 0.0, 0.0)
    assert confidence == 0.50


def test_both_max():
    confidence, attr = compute_confidence(1.0, 1.0, 1.0)
    assert confidence == 1.0
    assert attr == ATTRIBUTION_LIKELY_AI


def test_both_min():
    confidence, attr = compute_confidence(0.0, 0.0, 0.0)
    assert confidence == 0.0
    assert attr == ATTRIBUTION_LIKELY_HUMAN


# ── Threshold boundary tests (the ones the feedback called out explicitly) ──

def test_ai_boundary_exact():
    # 0.50 * 1.0 + 0.30 * 0.0 + 0.20 * 0.75 = 0.65 exactly → likely_ai
    confidence, attr = compute_confidence(1.0, 0.0, 0.75)
    assert confidence == LIKELY_AI_THRESHOLD
    assert attr == ATTRIBUTION_LIKELY_AI


def test_just_below_ai_boundary():
    # 0.50 * 1.0 + 0.30 * 0.0 + 0.20 * 0.70 = 0.64 → uncertain
    confidence, attr = compute_confidence(1.0, 0.0, 0.70)
    assert confidence == 0.64
    assert attr == ATTRIBUTION_UNCERTAIN


def test_human_boundary_exact():
    # 0.50 * 0.0 + 0.30 * 1.0 + 0.20 * 0.25 = 0.35 exactly → likely_human
    confidence, attr = compute_confidence(0.0, 1.0, 0.25)
    assert confidence == LIKELY_HUMAN_THRESHOLD
    assert attr == ATTRIBUTION_LIKELY_HUMAN


def test_just_above_human_boundary():
    # 0.50 * 0.0 + 0.30 * 1.0 + 0.20 * 0.30 = 0.36 → uncertain
    confidence, attr = compute_confidence(0.0, 1.0, 0.30)
    assert confidence == 0.36
    assert attr == ATTRIBUTION_UNCERTAIN


def test_mid_uncertain_band():
    # 0.50 * 0.5 + 0.30 * 0.5 + 0.20 * 0.5 = 0.50 → uncertain
    _, attr = compute_confidence(0.5, 0.5, 0.5)
    assert attr == ATTRIBUTION_UNCERTAIN


def test_confidence_rounded_to_4dp():
    # Verify rounding — weights produce a repeating decimal without rounding
    confidence, _ = compute_confidence(0.3, 0.7, 0.3)
    assert len(str(confidence).split(".")[-1]) <= 4


def test_repetition_score_default_is_neutral():
    # Default repetition_score=0.5 contributes 0.20 * 0.5 = 0.10
    # So compute_confidence(0.6, 0.4) == 0.50 * 0.6 + 0.30 * 0.4 + 0.20 * 0.5 = 0.30 + 0.12 + 0.10 = 0.52
    confidence, _ = compute_confidence(0.6, 0.4)
    assert confidence == 0.52
