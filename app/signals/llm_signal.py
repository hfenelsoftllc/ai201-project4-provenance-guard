# app/signals/llm_signal.py
# Signal 1: LLM-based semantic classification using Groq.
# No implementation — skeleton only.
#
# TODO (Milestone 3): Implement LLM classification signal.
#
# Design spec (from planning.md):
#   - Model: llama-3.3-70b-versatile via Groq API
#   - Prompt: instructs model to return ONLY {"ai_probability": <float>}
#   - Output: float 0.0–1.0 where 1.0 = confident AI-generated
#   - Raises exception on API failure (caller handles gracefully)
#
# Blind spots:
#   - Adversarially humanized AI text
#   - Heavily edited AI output
#   - Unusually formal human writing (academic, legal)
#   - Writing styles underrepresented in training data


def classify_with_llm(text: str) -> float:
    """
    Call the Groq LLM to assess whether text is AI-generated.

    Args:
        text: The content to classify.

    Returns:
        Float 0.0–1.0 where 1.0 = highly likely AI-generated.

    Raises:
        ValueError: If the API response cannot be parsed.
        Exception: On API call failure.
    """
    # TODO: implement
    # 1. Load GROQ_API_KEY from environment
    # 2. Build prompt requesting JSON response: {"ai_probability": <float>}
    # 3. Call Groq API with model llama-3.3-70b-versatile
    # 4. Parse response and return ai_probability float
    raise NotImplementedError("LLM signal not yet implemented")
