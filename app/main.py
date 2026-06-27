# app/main.py
# Entry point for the Provenance Guard Flask application.
# No implementation — skeleton only.
#
# TODO (Milestone 3): Initialize Flask app, register blueprints,
#   configure Flask-Limiter, load environment variables.

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# TODO: import and register route blueprints
# from app.routes.submit import submit_bp
# from app.routes.appeal import appeal_bp
# from app.routes.log import log_bp


def create_app():
    """Application factory. Returns a configured Flask app instance."""
    app = Flask(__name__)

    # TODO: Configure Flask-Limiter
    # limiter = Limiter(
    #     get_remote_address,
    #     app=app,
    #     default_limits=[],
    #     storage_uri="memory://",
    # )

    # TODO: Register blueprints
    # app.register_blueprint(submit_bp)
    # app.register_blueprint(appeal_bp)
    # app.register_blueprint(log_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
