# app/routes/appeal.py
# POST /appeal endpoint — creator appeal for a prior classification.
# No implementation — skeleton only.
#
# TODO (Milestone 5): Implement appeals endpoint.
#   - Accept JSON body: { "content_id": str, "creator_reasoning": str }
#   - Validate required fields; return 400 if missing.
#   - Look up original log entry by content_id; return 404 if not found.
#   - If status already "under_review", return 409 Conflict.
#   - Update status: "classified" -> "under_review".
#   - Append appeal_reasoning and appeal_timestamp to log entry.
#   - Return confirmation JSON.
#
# Response schema (200):
# {
#   "content_id": "<uuid>",
#   "status": "under_review",
#   "message": "Your appeal has been received and will be reviewed by a human moderator."
# }

from flask import Blueprint

appeal_bp = Blueprint("appeal", __name__)


@appeal_bp.route("/appeal", methods=["POST"])
def appeal():
    """File an appeal for a prior content classification."""
    # TODO: implement
    pass
