# app/routes/submit.py
# POST /submit — content attribution submission endpoint.

import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from app.models import audit_log
from app.signals.llm_signal import classify_with_llm
from app.signals.repetition_signal import classify_with_repetition
from app.signals.stylometric_signal import classify_with_stylometrics
from app.utils.confidence import compute_confidence
from app.utils.labels import generate_label

submit_bp = Blueprint("submit", __name__)


@submit_bp.route("/submit", methods=["POST"])
def submit():
    """
    Submit content for AI attribution analysis.
    ---
    tags:
      - Attribution
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - text
            - creator_id
          properties:
            text:
              type: string
              description: Content to classify
            creator_id:
              type: string
              description: Identifier for the content creator
            content_type:
              type: string
              enum: [text, image_description]
              default: text
              description: Type of content being submitted
    responses:
      200:
        description: Attribution result
        schema:
          type: object
          properties:
            content_id:
              type: string
            attribution:
              type: string
              enum: [likely_ai, likely_human, uncertain]
            confidence:
              type: number
            label:
              type: string
            timestamp:
              type: string
            content_type:
              type: string
      400:
        description: Missing required fields
      503:
        description: LLM service unavailable
    """
    body = request.get_json(silent=True) or {}
    text = body.get("text", "").strip()
    creator_id = body.get("creator_id", "").strip()
    content_type = body.get("content_type", "text").strip()

    if not text or not creator_id:
        return jsonify({"error": "Both 'text' and 'creator_id' are required."}), 400

    try:
        llm_score = classify_with_llm(text, content_type=content_type)
    except Exception as exc:
        return jsonify({"error": f"LLM signal failed: {exc}"}), 503

    if content_type == "image_description":
        # Stylometric and repetition signals are unreliable on short image descriptions;
        # return neutral so only the LLM signal drives the result.
        stylometric_score = 0.5
        repetition_score = 0.5
    else:
        stylometric_score = classify_with_stylometrics(text)
        repetition_score = classify_with_repetition(text)

    confidence, attribution = compute_confidence(llm_score, stylometric_score, repetition_score)
    label = generate_label(attribution)

    content_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_log.write_entry({
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": timestamp,
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "stylometric_score": stylometric_score,
        "repetition_score": repetition_score,
        "content_type": content_type,
        "status": "classified",
        "appeal_reasoning": None,
        "appeal_timestamp": None,
    })

    return jsonify({
        "content_id": content_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": label,
        "timestamp": timestamp,
        "content_type": content_type,
    })
