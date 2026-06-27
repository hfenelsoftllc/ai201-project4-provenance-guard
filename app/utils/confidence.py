# app/utils/confidence.py
# Confidence scoring: combines signal outputs into a single calibrated score.
# No implementation — skeleton only.
#
# TODO (Milestone 4): Implement confidence scoring logic.
#
# Design spec (from planning.md):
#
#   Combined score formula:
#     confidence = (LLM_WEIGHT * llm_score) + (STYLO_WEIGHT * stylometric_score)
#
#   Threshold map:
#     0.00 – 0.35  -> likely_human
#     0.36 – 0.64  -> uncertain
#     0.65 – 1.00  -> likely_ai
#
#   Asymmetric design: "likely_ai" requires >= 0.65 (not 0.51).
#   A false positive (human labeled as AI) is worse than a false negative.
#
#   Weights are explicit constants — not hardcoded magic numbers.
#   Adjust LLM_WEIGHT / STYLO_WEIGHT based on Milestone 4 calibration results.

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
        Tuple (confidence: float, attribution: str) where attribution is one of
        "likely_ai", "likely_human", or "uncertain".
    """
    # TODO: implement
    # confidence = (LLM_WEIGHT * llm_score) + (STYLO_WEIGHT * stylometric_score)
    # Apply threshold map to get attribution
    raise NotImplementedError("Confidence scoring not yet implemented")


def _map_to_attribution(confidence: float) -> str:
    """Map a confidence score to an attribution string using threshold map."""
    # TODO: implement
    raise NotImplementedError
