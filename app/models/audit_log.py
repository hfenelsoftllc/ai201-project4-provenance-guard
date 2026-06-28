# app/models/audit_log.py
# Audit log persistence — SQLite via Python's built-in sqlite3.

import sqlite3
from datetime import datetime, timezone

DB_PATH = "provenance_guard.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    content_id        TEXT PRIMARY KEY,
    creator_id        TEXT NOT NULL,
    timestamp         TEXT NOT NULL,
    attribution       TEXT NOT NULL,
    confidence        REAL NOT NULL,
    llm_score         REAL NOT NULL,
    stylometric_score REAL NOT NULL,
    status            TEXT NOT NULL DEFAULT 'classified',
    appeal_reasoning  TEXT,
    appeal_timestamp  TEXT
)
"""


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    conn.commit()
    return conn


def write_entry(entry: dict) -> None:
    """Write a new audit log entry."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO audit_log
                (content_id, creator_id, timestamp, attribution, confidence,
                 llm_score, stylometric_score, status, appeal_reasoning, appeal_timestamp)
            VALUES
                (:content_id, :creator_id, :timestamp, :attribution, :confidence,
                 :llm_score, :stylometric_score, :status, :appeal_reasoning, :appeal_timestamp)
            """,
            {
                "content_id": entry["content_id"],
                "creator_id": entry["creator_id"],
                "timestamp": entry["timestamp"],
                "attribution": entry["attribution"],
                "confidence": entry["confidence"],
                "llm_score": entry["llm_score"],
                "stylometric_score": entry["stylometric_score"],
                "status": entry.get("status", "classified"),
                "appeal_reasoning": entry.get("appeal_reasoning"),
                "appeal_timestamp": entry.get("appeal_timestamp"),
            },
        )


def get_entries(limit: int = 50) -> list:
    """Return the most recent audit log entries, newest first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_entry_by_id(content_id: str) -> dict:
    """Look up a single audit log entry by content_id. Returns None if not found."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM audit_log WHERE content_id = ?", (content_id,)
        ).fetchone()
    return dict(row) if row else None


def update_appeal(content_id: str, reasoning: str) -> bool:
    """
    Update an existing entry with appeal information.

    Returns:
        True if entry found and updated.
        False if content_id not found.

    Raises:
        ValueError: If status is already 'under_review'.
    """
    entry = get_entry_by_id(content_id)
    if entry is None:
        return False
    if entry["status"] == "under_review":
        raise ValueError("Appeal already filed for this content_id")
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE audit_log
               SET status = 'under_review',
                   appeal_reasoning = ?,
                   appeal_timestamp = ?
             WHERE content_id = ?
            """,
            (reasoning, now, content_id),
        )
    return True
