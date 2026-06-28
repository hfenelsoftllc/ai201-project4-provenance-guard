# app/routes/log.py
# GET /log — return recent audit log entries.

from flask import Blueprint, jsonify, request

from app.models import audit_log

log_bp = Blueprint("log", __name__)


@log_bp.route("/log", methods=["GET"])
def get_log():
    """
    Return recent audit log entries.
    ---
    tags:
      - Audit Log
    parameters:
      - in: query
        name: limit
        type: integer
        default: 50
        description: Maximum number of entries to return
    responses:
      200:
        description: List of audit log entries
        schema:
          type: object
          properties:
            entries:
              type: array
              items:
                type: object
                properties:
                  content_id:
                    type: string
                  creator_id:
                    type: string
                  timestamp:
                    type: string
                  attribution:
                    type: string
                  confidence:
                    type: number
                  llm_score:
                    type: number
                  stylometric_score:
                    type: number
                  status:
                    type: string
                  appeal_reasoning:
                    type: string
                  appeal_timestamp:
                    type: string
    """
    limit = request.args.get("limit", 50, type=int)
    entries = audit_log.get_entries(limit=limit)
    return jsonify({"entries": entries})
