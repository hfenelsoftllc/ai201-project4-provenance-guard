# app/routes/appeal.py
# POST /appeal — creator appeal for a prior classification.

from flask import Blueprint, jsonify, request

from app.models import audit_log

appeal_bp = Blueprint("appeal", __name__)


@appeal_bp.route("/appeal", methods=["POST"])
def appeal():
    """
    File an appeal for a prior content classification.
    ---
    tags:
      - Appeals
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - content_id
            - creator_reasoning
          properties:
            content_id:
              type: string
              description: UUID from original /submit response
            creator_reasoning:
              type: string
              description: Creator's explanation for the appeal
    responses:
      200:
        description: Appeal received
        schema:
          type: object
          properties:
            content_id:
              type: string
            status:
              type: string
              example: under_review
            message:
              type: string
      400:
        description: Missing required fields
      404:
        description: content_id not found
      409:
        description: Appeal already filed
    """
    body = request.get_json(silent=True) or {}
    content_id = body.get("content_id", "").strip()
    creator_reasoning = body.get("creator_reasoning", "").strip()

    if not content_id or not creator_reasoning:
        return jsonify({"error": "Both 'content_id' and 'creator_reasoning' are required."}), 400

    try:
        found = audit_log.update_appeal(content_id, creator_reasoning)
    except ValueError:
        return jsonify({"error": "An appeal has already been filed for this content."}), 409

    if not found:
        return jsonify({"error": "content_id not found."}), 404

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Your appeal has been received and will be reviewed by a human moderator.",
    })
