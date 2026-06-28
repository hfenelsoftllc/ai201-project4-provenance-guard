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
    confidence = round((LLM_WEIGHT * llm_score) + (STYLO_WEIGHT * stylometric_score), 4)
    attribution = (
        ATTRIBUTION_LIKELY_AI if confidence >= LIKELY_AI_THRESHOLD
        else ATTRIBUTION_LIKELY_HUMAN if confidence <= LIKELY_HUMAN_THRESHOLD
        else ATTRIBUTION_UNCERTAIN
    )
    return confidence, attribution
