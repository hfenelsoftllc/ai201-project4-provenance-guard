# app/routes/dashboard.py
# GET /dashboard — read-only analytics derived from the audit log.

from flask import Blueprint, jsonify

from app.models.audit_log import get_analytics

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Return aggregate detection analytics from the audit log.
    ---
    tags:
      - Analytics
    responses:
      200:
        description: Analytics summary
        schema:
          type: object
          properties:
            total_submissions:
              type: integer
            attribution_distribution:
              type: object
              properties:
                likely_ai:
                  type: integer
                likely_human:
                  type: integer
                uncertain:
                  type: integer
            appeal_rate:
              type: number
            signal_agreement_rate:
              type: number
    """
    return jsonify(get_analytics())
