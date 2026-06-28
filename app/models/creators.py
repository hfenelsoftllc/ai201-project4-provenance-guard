# app/models/creators.py
# Provenance certificate persistence — "verified human" creator registry.

import sqlite3
from datetime import datetime, timezone

from app.models.audit_log import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS creators (
    creator_id          TEXT PRIMARY KEY,
    attestation         TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending',
    verified_at         TEXT,
    verification_method TEXT NOT NULL DEFAULT 'self_attestation'
)
"""


def _init():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(_SCHEMA)
    conn.commit()
    conn.close()

_init()


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_verification_request(creator_id: str, attestation: str) -> dict:
    """Insert a new pending verification request. Raises on duplicate creator_id."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO creators (creator_id, attestation) VALUES (?, ?)",
            (creator_id, attestation),
        )
    return {"creator_id": creator_id, "status": "pending"}


def approve_verification(creator_id: str) -> bool:
    """Set a creator's status to verified. Returns False if creator_id not found."""
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        result = conn.execute(
            "UPDATE creators SET status = 'verified', verified_at = ? WHERE creator_id = ?",
            (now, creator_id),
        )
    return result.rowcount > 0


def get_creator_verified(creator_id: str) -> bool:
    """Return True if the creator has a verified provenance certificate."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT status FROM creators WHERE creator_id = ?", (creator_id,)
        ).fetchone()
    return row is not None and row["status"] == "verified"
