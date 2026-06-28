# app/signals/stylometric_signal.py
# Signal 2: Stylometric heuristics (pure Python, no external libraries).
#
# Three sub-metrics averaged: Sentence Length Variance (SLV), Type-Token
# Ratio (TTR), Punctuation Density (PD). Each normalized 0.0–1.0 where
# 1.0 = AI-like.
#
# Blind spots: non-native English speakers with formal/restricted vocabulary,
# short texts (< 50 words), highly structured human writing (legal, academic).

import math
import re
import string

MIN_WORDS_FOR_STYLOMETRICS = 50

# Normalization reference ranges (recalibrate in Milestone 4 against sample texts)
SLV_AI_THRESHOLD = 6.0       # std dev ≤ 6 → AI-like (uniform sentences)
SLV_HUMAN_THRESHOLD = 15.0   # std dev ≥ 15 → human-like (variable sentences)

TTR_AI_THRESHOLD = 0.4       # ratio ≤ 0.4 → AI-like (low lexical diversity)
TTR_HUMAN_THRESHOLD = 0.7    # ratio ≥ 0.7 → human-like (high lexical diversity)

PD_AI_THRESHOLD = 3.0        # ≤ 3 non-period punct/100 words → AI-like (sparse)
PD_HUMAN_THRESHOLD = 8.0     # ≥ 8 non-period punct/100 words → human-like (expressive)


def classify_with_stylometrics(text: str) -> float:
    """
    Compute stylometric score for the given text.

    Returns 0.5 (neutral) if text is shorter than MIN_WORDS_FOR_STYLOMETRICS
    so the LLM signal dominates for short content.
    """
    words = text.split()
    if len(words) < MIN_WORDS_FOR_STYLOMETRICS:
        return 0.5

    sentences = _split_sentences(text)
    slv_raw = _compute_slv(sentences)
    ttr_raw = _compute_ttr(words)
    pd_raw = _compute_pd(text, len(words))

    slv_score = _normalize(slv_raw, SLV_AI_THRESHOLD, SLV_HUMAN_THRESHOLD)
    ttr_score = _normalize(ttr_raw, TTR_AI_THRESHOLD, TTR_HUMAN_THRESHOLD)
    pd_score = _normalize(pd_raw, PD_AI_THRESHOLD, PD_HUMAN_THRESHOLD)

    return round((slv_score + ttr_score + pd_score) / 3, 4)


def _split_sentences(text: str) -> list:
    """Split text into sentences on .!? boundaries."""
    parts = re.split(r"[.!?]+", text)
    return [p.strip() for p in parts if p.strip()]


def _compute_slv(sentences: list) -> float:
    """Std dev of sentence lengths in words. Low = uniform = AI-like."""
    if len(sentences) < 2:
        return 0.0
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    return math.sqrt(variance)


def _compute_ttr(words: list) -> float:
    """Type-token ratio on first 100 tokens. Low = low diversity = AI-like."""
    sample = [w.lower().strip(string.punctuation) for w in words[:100]]
    sample = [w for w in sample if w]
    if not sample:
        return 0.5
    return len(set(sample)) / len(sample)


def _compute_pd(text: str, word_count: int) -> float:
    """Non-period punctuation per 100 words. Low density = AI-like."""
    if word_count == 0:
        return 0.0
    non_period = sum(1 for ch in text if ch in ",;:!?—–-\"'()")
    return (non_period / word_count) * 100


def _normalize(value: float, ai_threshold: float, human_threshold: float) -> float:
    """
    Normalize a raw metric to 0.0–1.0.
    value ≤ ai_threshold    → 1.0 (most AI-like)
    value ≥ human_threshold → 0.0 (most human-like)
    """
    if value <= ai_threshold:
        return 1.0
    if value >= human_threshold:
        return 0.0
    return 1.0 - (value - ai_threshold) / (human_threshold - ai_threshold)
