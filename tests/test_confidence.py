"""Tests for confidence scoring — thresholds and weights are load-bearing design decisions."""
import pytest
from app.utils.confidence import (
    compute_confidence,
    LIKELY_AI_THRESHOLD,
    LIKELY_HUMAN_THRESHOLD,
    ATTRIBUTION_LIKELY_AI,
    ATTRIBUTION_LIKELY_HUMAN,
    ATTRIBUTION_UNCERTAIN,
)


def test_weights():
    # 0.60 * 1.0 + 0.40 * 0.0 = 0.60
    confidence, _ = compute_confidence(1.0, 0.0)
    assert confidence == 0.60


def test_both_max():
    confidence, attr = compute_confidence(1.0, 1.0)
    assert confidence == 1.0
    assert attr == ATTRIBUTION_LIKELY_AI


def test_both_min():
    confidence, attr = compute_confidence(0.0, 0.0)
    assert confidence == 0.0
    assert attr == ATTRIBUTION_LIKELY_HUMAN


# ── Threshold boundary tests (the ones the feedback called out explicitly) ──

def test_ai_boundary_exact():
    # 0.60 * 1.0 + 0.40 * 0.125 = 0.65 exactly → likely_ai
    confidence, attr = compute_confidence(1.0, 0.125)
    assert confidence == LIKELY_AI_THRESHOLD
    assert attr == ATTRIBUTION_LIKELY_AI


def test_just_below_ai_boundary():
    # 0.60 * 1.0 + 0.40 * 0.1 = 0.64 → uncertain
    confidence, attr = compute_confidence(1.0, 0.1)
    assert confidence == 0.64
    assert attr == ATTRIBUTION_UNCERTAIN


def test_human_boundary_exact():
    # 0.60 * 0.0 + 0.40 * 0.875 = 0.35 exactly → likely_human
    confidence, attr = compute_confidence(0.0, 0.875)
    assert confidence == LIKELY_HUMAN_THRESHOLD
    assert attr == ATTRIBUTION_LIKELY_HUMAN


def test_just_above_human_boundary():
    # 0.60 * 0.0 + 0.40 * 0.9 = 0.36 → uncertain
    confidence, attr = compute_confidence(0.0, 0.9)
    assert confidence == 0.36
    assert attr == ATTRIBUTION_UNCERTAIN


def test_mid_uncertain_band():
    # 0.60 * 0.5 + 0.40 * 0.5 = 0.50 → uncertain
    _, attr = compute_confidence(0.5, 0.5)
    assert attr == ATTRIBUTION_UNCERTAIN


def test_confidence_rounded_to_4dp():
    # Verify rounding — weights produce a repeating decimal without rounding
    confidence, _ = compute_confidence(0.3, 0.7)
    assert len(str(confidence).split(".")[-1]) <= 4
