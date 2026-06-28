
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project State

**Implementation is complete** (Milestones 3–5). All `app/` modules are fully implemented; `raise NotImplementedError` stubs have been replaced. The authoritative spec lives in `planning.md`; design decisions there are binding, not advisory.

## Commands

```powershell
# Setup (one-time)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env   # then edit .env to add GROQ_API_KEY

# Run the dev server (Flask app factory in app/main.py)
python -m app.main

# Run the Gradio UI (port 7860)
python gradio_ui.py

# Run the test suite (no GROQ_API_KEY required — LLM calls are mocked)
pytest tests/ -v
```

## Test Suite

70 tests across 6 files in `tests/`. No network calls — the Groq client is injectable via `classify_with_llm(text, client=mock)` so tests run offline.

| File | Covers |
|------|--------|
| `tests/test_confidence.py` | Threshold boundaries (0.65 → likely_ai, 0.64 → uncertain), weights |
| `tests/test_labels.py` | Label dispatch, public contract strings, appeal copy |
| `tests/test_stylometric_signal.py` | Short-text guard (< 50 words), normalize boundaries, SLV/TTR |
| `tests/test_llm_signal.py` | Mock client injection, score clamping, parse errors |
| `tests/test_audit_log.py` | Write/read, appeal status transition, duplicate 409, limit/ordering |
| `tests/test_routes.py` | Flask test client: all HTTP status codes, log write-through |
| `tests/test_gradio_ui.py` | `html.escape()` on all user-controlled HTML values |

When adding new features: patch at the import site (`app.routes.submit.classify_with_llm`), not the source module (`app.signals.llm_signal.classify_with_llm`).

## Architecture

### Request flow (the one diagram that matters)

`POST /submit` runs **two independent signals in sequence**, combines them with explicit weights, maps the combined score through a threshold table, generates a label, writes one audit entry, and returns. The audit write happens **before** the response is returned.

```
text + creator_id
   ├─► classify_with_llm (Groq, semantic)        → llm_score
   └─► classify_with_stylometrics (pure Python)  → stylometric_score
            │
            ▼
   compute_confidence(llm_score, stylometric_score)
       = 0.60 * llm_score + 0.40 * stylometric_score   → (confidence, attribution)
            │
            ▼
   generate_label(attribution, confidence)             → label text (one of 3 verbatim variants)
            │
            ▼
   audit_log.write_entry({...})                        → SQLite or JSON
            │
            ▼
   { content_id, attribution, confidence, label, timestamp }
```

`POST /appeal` does **not** re-classify. It looks up by `content_id`, transitions status `classified → under_review`, appends `appeal_reasoning` + `appeal_timestamp` to the existing log entry, and returns 200. 404 if not found, 409 if already under review.

`GET /log` returns recent entries — appeals are surfaced here for human reviewers (no separate moderator endpoint).

### Module boundaries

- `app/main.py` — Flask app factory + Flask-Limiter setup. Limiter uses `storage_uri="memory://"` (required param; omitting it triggers a runtime warning) and is attached to `POST /submit` only.
- `app/routes/` — blueprints, one per endpoint (`submit_bp`, `appeal_bp`, `log_bp`). Routes orchestrate; they do not contain detection logic.
- `app/signals/` — the two detection signals. They are **deliberately independent**: Signal 1 is semantic (Groq LLM), Signal 2 is structural (pure Python stylometrics). Do not collapse them or share state — the design depends on them being able to disagree.
- `app/utils/confidence.py` — owns the weights (`LLM_WEIGHT=0.60`, `STYLO_WEIGHT=0.40`) and thresholds (`LIKELY_AI_THRESHOLD=0.65`, `LIKELY_HUMAN_THRESHOLD=0.35`). These are module-level constants, not magic numbers — change them here, not at call sites.
- `app/utils/labels.py` — holds the three label strings as `LABEL_LIKELY_AI`, `LABEL_LIKELY_HUMAN`, `LABEL_UNCERTAIN`. **The label text is part of the public contract** — same strings appear verbatim in `README.md` and `planning.md`. If you must change a label, update all three places in the same commit.
- `app/models/audit_log.py` — persistence. Four functions: `write_entry`, `get_entries`, `get_entry_by_id`, `update_appeal`. The schema (9 fields) is documented in the module docstring. `update_appeal` raises `ValueError` if status is already `under_review` — the appeal route maps that to HTTP 409.

### Calibration constants

`app/signals/stylometric_signal.py` exposes `MIN_WORDS_FOR_STYLOMETRICS = 50` and normalization thresholds (`SLV_*`, `TTR_*`, `PD_*`). Texts under 50 words return `0.5` (neutral) so the LLM signal dominates — this is intentional, not a fallback. The thresholds are placeholders to recalibrate in Milestone 4 against 4 sample texts (two clearly AI, two clearly human, two borderline). If calibration shifts, update the constants — do not introduce per-call overrides.

### Asymmetric thresholds (load-bearing design)

The "uncertain" band (0.36–0.64) is deliberately wide and the AI threshold is 0.65 rather than 0.51. The premise: on a creative platform, falsely labeling a human as AI is worse than the reverse. Don't narrow this band without revisiting `planning.md` § Uncertainty Representation.

## Spec ↔ code coupling

When changing any of the following, update **both** the code and the matching section of `planning.md` in the same commit (and `README.md` when label text or API surface changes):

- Label variant text → `app/utils/labels.py` + README "Transparency Labels" + planning.md § Transparency Label Design
- Confidence weights or thresholds → `app/utils/confidence.py` + planning.md § Uncertainty Representation
- Rate-limit values (`10/min; 100/day`) → `app/main.py` limiter config + README + planning.md § Rate Limiting Rationale
- Audit log schema → `app/models/audit_log.py` + planning.md § Audit Log + `GET /log` response example in `app/routes/log.py`

## UI Skill

When working on `gradio_ui.py` or any frontend work, load the sketch findings skill first:
`.claude/skills/sketch-findings-provenance-guard/SKILL.md`

It captures the winning design decisions from the two UI sketches (Split Panel layout, Verdict Card result display) and the invariants that must hold in all future UI work (color tokens, XSS guards, signal chip visibility).

## Security note

`.env.example` currently contains a real-format `GROQ_API_KEY` value (committed in `2646bc1`-era history). If that key is live, rotate it and replace the example with a placeholder before doing further commits. Never commit `.env`.
