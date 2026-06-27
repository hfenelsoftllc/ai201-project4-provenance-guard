# app/models/audit_log.py
# Audit log persistence layer — SQLite or structured JSON.
# No implementation — skeleton only.
#
# TODO (Milestone 3): Implement audit log storage.
#
# Design spec (from planning.md):
#   Every attribution decision and appeal is written to a structured log.
#   Storage: SQLite (preferred) or JSON file. SQLite is built into Python.
#
# Log entry schema:
# {
#   "content_id": "<uuid>",      -- UUID v4
#   "creator_id": "<string>",    -- plain string identifier from submission
#   "timestamp": "<ISO 8601>",   -- UTC timestamp of classification
#   "attribution": "<string>",   -- likely_ai | likely_human | uncertain
#   "confidence": 0.0,           -- combined confidence score (0.0–1.0)
#   "llm_score": 0.0,            -- raw LLM signal output (0.0–1.0)
#   "stylometric_score": 0.0,    -- raw stylometric signal output (0.0–1.0)
#   "status": "<string>",        -- classified | under_review
#   "appeal_reasoning": null     -- string if appeal filed, else null
# }
#
# Required functions:
#   write_entry(entry: dict) -> None
#   get_entries(limit: int = 50) -> list[dict]
#   get_entry_by_id(content_id: str) -> dict | None
#   update_appeal(content_id: str, reasoning: str) -> bool


def write_entry(entry: dict) -> None:
    """Write a new audit log entry."""
    # TODO: implement
    raise NotImplementedError("Audit log write not yet implemented")


def get_entries(limit: int = 50) -> list:
    """Return the most recent audit log entries."""
    # TODO: implement
    raise NotImplementedError("Audit log read not yet implemented")


def get_entry_by_id(content_id: str) -> dict:
    """Look up a single audit log entry by content_id. Returns None if not found."""
    # TODO: implement
    raise NotImplementedError("Audit log lookup not yet implemented")


def update_appeal(content_id: str, reasoning: str) -> bool:
    """
    Update an existing entry with appeal information.

    Returns:
        True if entry found and updated.
        False if content_id not found.
        Raises ValueError if status already 'under_review'.
    """
    # TODO: implement
    raise NotImplementedError("Appeal update not yet implemented")
