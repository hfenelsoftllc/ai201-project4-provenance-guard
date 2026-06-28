# app/signals/repetition_signal.py
# Signal 3: Repetition Density — measures bigram repetition ratio.
# AI text over-samples high-probability token sequences and repeats itself;
# human writing varies more. Pure Python, no dependencies.
#
# Blind spots: intentionally repetitive human writing (song lyrics, poetry with
# refrains, legal boilerplate), very short texts (<50 words).

MIN_WORDS_FOR_REPETITION = 50

# Normalization thresholds
RD_AI_THRESHOLD = 0.15     # repetition ratio >= 0.15 → AI-like (high repetition)
RD_HUMAN_THRESHOLD = 0.04  # repetition ratio <= 0.04 → human-like (low repetition)


def classify_with_repetition(text: str) -> float:
    """
    Compute repetition density score for the given text.

    Returns 0.5 (neutral) if text is shorter than MIN_WORDS_FOR_REPETITION
    so the LLM signal dominates for short content.
    """
    words = [w.lower() for w in text.split()]
    if len(words) < MIN_WORDS_FOR_REPETITION:
        return 0.5

    bigrams = [(words[i], words[i + 1]) for i in range(len(words) - 1)]
    if not bigrams:
        return 0.5

    total = len(bigrams)
    unique = len(set(bigrams))
    repeated = total - unique
    ratio = repeated / total

    return round(_normalize(ratio, RD_AI_THRESHOLD, RD_HUMAN_THRESHOLD), 4)


def _normalize(value: float, ai_threshold: float, human_threshold: float) -> float:
    """
    Normalize repetition ratio to 0.0–1.0.
    value >= ai_threshold    → 1.0 (most AI-like, high repetition)
    value <= human_threshold → 0.0 (most human-like, low repetition)
    """
    if value >= ai_threshold:
        return 1.0
    if value <= human_threshold:
        return 0.0
    return (value - human_threshold) / (ai_threshold - human_threshold)
