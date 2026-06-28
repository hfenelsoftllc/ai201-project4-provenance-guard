# app/main.py
# Flask app factory for Provenance Guard.

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

_SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs",
}

_SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Provenance Guard API",
        "description": (
            "Backend attribution service for AI content detection on creative platforms. "
            "Classifies text as likely_ai, likely_human, or uncertain using a three-signal "
            "pipeline (Groq LLM + stylometric heuristics + repetition density). "
            "Includes provenance certificates (S2), analytics dashboard (S3), and "
            "multi-modal support for image descriptions (S4)."
        ),
        "version": "1.0.0",
        "contact": {"email": "fhyac001@fiu.edu"},
    },
    "basePath": "/",
    "schemes": ["http"],
}


def create_app():
    """Application factory. Returns a configured Flask app instance."""
    app = Flask(__name__)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[],
        storage_uri="memory://",
    )

    from app.routes.submit import submit_bp
    from app.routes.appeal import appeal_bp
    from app.routes.log import log_bp
    from app.routes.verify import verify_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(submit_bp)
    app.register_blueprint(appeal_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(verify_bp)
    app.register_blueprint(dashboard_bp)

    # Rate limiting: POST /submit only — 10/min and 100/day per IP
    limiter.limit("10 per minute; 100 per day")(submit_bp)

    Swagger(app, config=_SWAGGER_CONFIG, template=_SWAGGER_TEMPLATE)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
