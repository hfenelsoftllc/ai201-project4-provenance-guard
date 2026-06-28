# app/routes/verify.py
# POST /verify — submit a provenance attestation
# POST /verify/<creator_id>/approve — moderator approval

from flask import Blueprint, jsonify, request

from app.models import creators as creators_model

verify_bp = Blueprint("verify", __name__)


@verify_bp.route("/verify", methods=["POST"])
def verify():
    """
    Submit a provenance attestation for a creator.
    ---
    tags:
      - Provenance
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - creator_id
            - attestation
          properties:
            creator_id:
              type: string
              description: Unique creator identifier
            attestation:
              type: string
              description: Plain-text statement attesting human authorship
    responses:
      201:
        description: Verification request created (status pending)
      400:
        description: Missing required fields
      409:
        description: creator_id already has a pending or verified request
    """
    body = request.get_json(silent=True) or {}
    creator_id = body.get("creator_id", "").strip()
    attestation = body.get("attestation", "").strip()
    if not creator_id or not attestation:
        return jsonify({"error": "Both 'creator_id' and 'attestation' are required."}), 400
    try:
        result = creators_model.create_verification_request(creator_id, attestation)
    except Exception:
        return jsonify({"error": "A verification request already exists for this creator_id."}), 409
    return jsonify(result), 201


@verify_bp.route("/verify/<creator_id>/approve", methods=["POST"])
def approve(creator_id: str):
    """
    Approve a pending provenance certificate.
    ---
    tags:
      - Provenance
    parameters:
      - in: path
        name: creator_id
        type: string
        required: true
        description: The creator to approve
    responses:
      200:
        description: Verification approved
      404:
        description: creator_id not found
    """
    updated = creators_model.approve_verification(creator_id)
    if not updated:
        return jsonify({"error": "creator_id not found"}), 404
    return jsonify({"creator_id": creator_id, "status": "verified"}), 200
