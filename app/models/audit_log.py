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
    appeal_timestamp  TEXT,
    repetition_score  REAL DEFAULT 0.5,
    content_type      TEXT NOT NULL DEFAULT 'text'
)
"""

# Migrations for existing databases that predate the new columns.
_MIGRATIONS = [
    "ALTER TABLE audit_log ADD COLUMN repetition_score REAL DEFAULT 0.5",
    "ALTER TABLE audit_log ADD COLUMN content_type TEXT NOT NULL DEFAULT 'text'",
]


def _init():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(_SCHEMA)
    for migration in _MIGRATIONS:
        try:
            conn.execute(migration)
        except sqlite3.OperationalError:
            pass  # column already exists
    conn.commit()
    conn.close()

_init()


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def write_entry(entry: dict) -> None:
    """Write a new audit log entry."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO audit_log
                (content_id, creator_id, timestamp, attribution, confidence,
                 llm_score, stylometric_score, status, appeal_reasoning, appeal_timestamp,
                 repetition_score, content_type)
            VALUES
                (:content_id, :creator_id, :timestamp, :attribution, :confidence,
                 :llm_score, :stylometric_score, :status, :appeal_reasoning, :appeal_timestamp,
                 :repetition_score, :content_type)
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
                "repetition_score": entry.get("repetition_score", 0.5),
                "content_type": entry.get("content_type", "text"),
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


def get_analytics() -> dict:
    """Return aggregate analytics derived from the audit log."""
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        dist_rows = conn.execute(
            "SELECT attribution, COUNT(*) as cnt FROM audit_log GROUP BY attribution"
        ).fetchall()
        appeals = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE status = 'under_review'"
        ).fetchone()[0]
        agree = conn.execute(
            """SELECT COUNT(*) FROM audit_log
               WHERE (llm_score > 0.5 AND stylometric_score > 0.5)
                  OR (llm_score < 0.5 AND stylometric_score < 0.5)"""
        ).fetchone()[0]

    distribution = {"likely_ai": 0, "likely_human": 0, "uncertain": 0}
    for row in dist_rows:
        distribution[row["attribution"]] = row["cnt"]

    appeal_rate = round(appeals / total, 4) if total > 0 else 0.0
    agreement_rate = round(agree / total, 4) if total > 0 else 0.0

    return {
        "total_submissions": total,
        "attribution_distribution": distribution,
        "appeal_rate": appeal_rate,
        "signal_agreement_rate": agreement_rate,
    }
