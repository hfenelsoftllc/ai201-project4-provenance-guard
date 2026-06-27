# app/routes/log.py
# GET /log endpoint — return recent audit log entries.
# No implementation — skeleton only.
#
# TODO (Milestone 3): Implement log endpoint.
#   - Return the most recent audit log entries as JSON.
#   - At least 3 entries required for grading evidence.
#
# Response schema (200):
# {
#   "entries": [
#     {
#       "content_id": "<uuid>",
#       "creator_id": "<string>",
#       "timestamp": "<ISO 8601>",
#       "attribution": "likely_ai | likely_human | uncertain",
#       "confidence": 0.0,
#       "llm_score": 0.0,
#       "stylometric_score": 0.0,
#       "status": "classified | under_review",
#       "appeal_reasoning": null
#     }
#   ]
# }

from flask import Blueprint

log_bp = Blueprint("log", __name__)


@log_bp.route("/log", methods=["GET"])
def get_log():
    """Return recent audit log entries as JSON."""
    # TODO: implement
    pass
