# app/utils/confidence.py
# Confidence scoring: combines signal outputs into a single calibrated score.

# Signal weights (must sum to 1.0)
LLM_WEIGHT = 0.60
STYLO_WEIGHT = 0.40

# Attribution thresholds
LIKELY_AI_THRESHOLD = 0.65
LIKELY_HUMAN_THRESHOLD = 0.35

ATTRIBUTION_LIKELY_AI = "likely_ai"
ATTRIBUTION_LIKELY_HUMAN = "likely_human"
ATTRIBUTION_UNCERTAIN = "uncertain"


def compute_confidence(llm_score: float, stylometric_score: float) -> tuple:
    """
    Combine signal scores into a final confidence score and attribution.

    Args:
        llm_score: Float 0.0–1.0 from LLM signal (1.0 = AI-like).
        stylometric_score: Float 0.0–1.0 from stylometric signal (1.0 = AI-like).

    Returns:
        Tuple (confidence: float, attribution: str).
    """
    confidence = round((LLM_WEIGHT * llm_score) + (STYLO_WEIGHT * stylometric_score), 4)
    return confidence, _map_to_attribution(confidence)


def _map_to_attribution(confidence: float) -> str:
    """Map confidence score to attribution string using asymmetric threshold map."""
    if confidence >= LIKELY_AI_THRESHOLD:
        return ATTRIBUTION_LIKELY_AI
    if confidence <= LIKELY_HUMAN_THRESHOLD:
        return ATTRIBUTION_LIKELY_HUMAN
    return ATTRIBUTION_UNCERTAIN
