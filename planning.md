# Provenance Guard — Planning Document

> **AI201 Project 4 | Due: June 29, 2026**  
> Written before any implementation code. Updated before any stretch features are begun.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Goal Boundary](#goal-boundary)
3. [Recommended Stack](#recommended-stack)
4. [Features](#features)
5. [Detection Signals](#detection-signals)
6. [Uncertainty Representation](#uncertainty-representation)
7. [Transparency Label Design](#transparency-label-design)
8. [Appeals Workflow](#appeals-workflow)
9. [Anticipated Edge Cases](#anticipated-edge-cases)
10. [Architecture](#architecture)
11. [API Surface](#api-surface)
12. [AI Tool Plan](#ai-tool-plan)

---

## Project Overview

Provenance Guard is a backend attribution service that any creative-sharing platform (writing, poetry, music lyrics, short fiction) can integrate to:

- Classify whether submitted text-based content is likely AI-generated or human-written.
- Return a calibrated confidence score that reflects genuine uncertainty.
- Surface a plain-language transparency label to end users.
- Allow creators to file an appeal if they believe they have been misclassified.
- Log every decision in a structured audit trail.
- Protect the system from abuse via rate limiting.

The service is built as a standalone Flask REST API with no frontend. Every feature is observable through the API and documented in the README.

---

## Goal Boundary

**In scope:**
- Text-based content only (poems, short story excerpts, blog posts, song lyric snippets).
- Synchronous classification: POST /submit returns a result immediately.
- Single-reviewer appeals: the system queues appeals for human review; it does NOT auto-reclassify.
- SQLite or structured JSON for persistence (no cloud database required).
- Rate limiting at the submission endpoint only.
- Audit log readable via GET /log.

**Out of scope:**
- Image, audio, or video content (unless stretch feature multi-modal is attempted).
- Automated re-classification on appeal.
- User authentication / JWT (creator_id is a plain string identifier).
- Frontend UI or dashboard (unless stretch analytics dashboard is attempted).
- Deployment to production cloud infrastructure.
- Storing or analyzing raw submitted text beyond what is needed for the audit log entry.

---

## Recommended Stack

| Component | Tool | Version / Notes |
|---|---|---|
| API framework | Flask | >= 3.0.0 |
| LLM signal | Groq (llama-3.3-70b-versatile) | Free tier, same account as Projects 1–3 |
| Stylometric signal | Pure Python heuristics | No external libraries |
| Rate limiting | Flask-Limiter | >= 3.5.0; requires `storage_uri` param |
| Audit log | SQLite (built-in) or structured JSON file | No additional setup |
| Environment secrets | python-dotenv | 1.0.1 |

**requirements.txt:**
```
flask>=3.0.0
flask-limiter>=3.5.0
groq==0.15.0
python-dotenv==1.0.1
```

---

## Features

### Required Features

#### 1. Content Submission Endpoint — POST /submit

Accepts `text` and `creator_id`. Returns:
- `content_id` — UUID assigned to this submission (required for appeals).
- `attribution` — one of `likely_ai`, `likely_human`, `uncertain`.
- `confidence` — float 0.0–1.0.
- `label` — exact transparency label text shown to end users.
- `timestamp` — ISO 8601 UTC.

Every call writes to the audit log and is subject to rate limiting.

#### 2. Multi-Signal Detection Pipeline

Runs **two independent signals** on every submission. Single-signal detection is not acceptable. See [Detection Signals](#detection-signals).

#### 3. Confidence Scoring with Uncertainty

Returns a calibrated float, not a binary flag. A 0.51 score produces a meaningfully different label than a 0.95. See [Uncertainty Representation](#uncertainty-representation).

#### 4. Transparency Label

Three distinct variants returned based on confidence score. All three variant texts are committed to the README and to this document. See [Transparency Label Design](#transparency-label-design).

#### 5. Appeals Workflow — POST /appeal

Accepts `content_id` and `creator_reasoning`. Updates submission status to `under_review`, logs the appeal, returns confirmation. No automated re-classification. See [Appeals Workflow](#appeals-workflow).

#### 6. Rate Limiting

Flask-Limiter on POST /submit. Limits and reasoning documented in README. See [API Surface](#api-surface).

#### 7. Audit Log — GET /log

Every attribution decision and appeal written to structured log (SQLite or JSON). At least 3 entries visible for grading. Schema:

```json
{
  "content_id": "<uuid>",
  "creator_id": "<string>",
  "timestamp": "<ISO 8601>",
  "attribution": "likely_ai | likely_human | uncertain",
  "confidence": 0.0,
  "llm_score": 0.0,
  "stylometric_score": 0.0,
  "status": "classified | under_review",
  "appeal_reasoning": null
}
```

### Stretch Features

Attempted only after all required features pass. This document updated before each stretch feature begins.

- **S1. Ensemble Detection** — third signal with documented weighting/voting.
- **S2. Provenance Certificate** — "verified human" credential with display logic.
- **S3. Analytics Dashboard** — GET /dashboard with detection patterns, appeal rate, and one additional metric.
- **S4. Multi-Modal Support** — extend pipeline to a second content type.

---

## Detection Signals

### Signal 1 — LLM Semantic Classification (Groq)

**Measures:** Holistic semantic and stylistic coherence. The LLM is prompted to assess whether text reads as human-authored or AI-generated.

**Output:** Float 0.0–1.0 where 1.0 = confident AI-generated, 0.0 = confident human-written. Prompt instructs model to return only `{"ai_probability": <float>}` for deterministic parsing.

**Why it differs:** LLMs have learned patterns distinguishing AI output (uniform sentence rhythm, excessive hedging, formulaic transitions) from human writing (idiosyncratic vocabulary, emotional variance, autobiographical specificity).

**Blind spots:** Can be fooled by adversarially humanized AI text, heavily edited AI output, or unusually formal human writing. May over-flag writing styles underrepresented in its training data.

---

### Signal 2 — Stylometric Heuristics (Pure Python)

**Measures:** Three statistical sub-metrics averaged into a single stylometric score:

1. **Sentence Length Variance (SLV):** Std dev of sentence lengths in words. AI text → more uniform (low SLV); human writing → more variable (high SLV). Low SLV normalized toward 1.0 (AI-like).

2. **Type-Token Ratio (TTR):** `unique_words / total_words` on first 100 tokens. AI text → lower lexical diversity; human creative writing → higher TTR. Low TTR normalized toward 1.0 (AI-like).

3. **Punctuation Density (PD):** Non-period punctuation per 100 words. AI text → comma-heavy, uniform; human creative text → idiosyncratic punctuation. Extreme uniformity normalized toward 1.0 (AI-like).

**Output:** Float 0.0–1.0 where 1.0 = strongly AI-like structurally.

**Why it differs from Signal 1:** Signal 1 is semantic; Signal 2 is structural. Genuinely independent — a text can have human-sounding semantics but AI-uniform structure, or vice versa.

**Blind spots:** Non-native English speakers may produce low-SLV, low-TTR text that scores as AI-like. Short texts (< 50 words) produce unreliable statistics. Highly structured human writing (legal, academic) may also score falsely high.

### Signal Combination

```
confidence = (0.60 * llm_score) + (0.40 * stylometric_score)
```

LLM signal receives higher weight (captures semantic coherence holistically); stylometric signal provides corroborating structural check. Weights are explicit constants, not hardcoded magic numbers.

---

## Uncertainty Representation

### Threshold Map

| Score Range | Attribution | Label Variant |
|---|---|---|
| 0.00 – 0.35 | `likely_human` | High-Confidence Human |
| 0.36 – 0.64 | `uncertain` | Uncertain |
| 0.65 – 1.00 | `likely_ai` | High-Confidence AI |

### What a score of 0.6 means

A confidence of 0.6 means the combined signals lean toward AI-generated but with meaningful uncertainty. The system is not confident enough for a high-confidence AI label. Score 0.6 → "Uncertain" label.

### Asymmetric design rationale

Thresholds are intentionally asymmetric. "Likely AI" requires score ≥ 0.65 (not 0.51). A false positive (labeling a human's work as AI) is worse than a false negative on a creative platform. The uncertain band (0.36–0.64) is deliberately wide.

### Calibration approach

During Milestone 4 testing, at least 4 sample texts run and scores inspected. If clearly AI text scores below 0.65 or clearly human text scores above 0.35, stylometric normalization functions will be recalibrated before proceeding.

---

## Transparency Label Design

All three label variants written here verbatim. Same texts appear in the README. The `label` field in every /submit response contains one of these exact strings.

### Variant 1 — High-Confidence AI (score ≥ 0.65)

```
AI-Assisted Content
Our systems detected patterns consistent with AI-generated text (confidence: HIGH).
This label does not prevent you from reading or engaging with this work.
If you are the creator and believe this is incorrect, you can submit an appeal.
```

### Variant 2 — High-Confidence Human (score ≤ 0.35)

```
Human-Authored Content
Our systems found strong indicators that this work was written by a person (confidence: HIGH).
Enjoy the work knowing it reflects a human creative voice.
```

### Variant 3 — Uncertain (score 0.36–0.64)

```
Attribution Unclear
Our systems were unable to determine with confidence whether this content was written by a person or generated by AI (confidence: LOW).
We encourage you to consider the context. If you are the creator and believe this classification is wrong, you can submit an appeal.
```

---

## Appeals Workflow

**Who can appeal:** Any creator with a valid `content_id` from a prior /submit call.

**Information required:**
- `content_id` (required) — UUID from original submission.
- `creator_reasoning` (required) — plain-text explanation.

**System actions on appeal:**
1. Look up audit log entry for `content_id`. If not found → 404.
2. If status already `under_review` → 409 Conflict.
3. Update status: `classified` → `under_review`.
4. Append `appeal_reasoning` and `appeal_timestamp` to log entry.
5. Return HTTP 200:
```json
{
  "content_id": "<uuid>",
  "status": "under_review",
  "message": "Your appeal has been received and will be reviewed by a human moderator."
}
```

**Human reviewer view:** GET /log filtered by `status: under_review`. Each entry shows original attribution, confidence, both signal scores, and creator's stated reasoning.

---

## Anticipated Edge Cases

### Edge Case 1 — Non-native English speaker with formal register

A non-native writer may produce restricted vocabulary (low TTR) and uniform sentence lengths (low SLV) due to careful deliberate writing, not AI generation. Stylometric signal will over-score as AI-like. **Mitigation:** Wide uncertain band and 0.65 threshold reduce false positives reaching "Likely AI" label. Appeals workflow provides correction path.

### Edge Case 2 — Heavily edited AI output

Semantically humanized but structurally uniform text will have LLM signal scoring human-like but stylometric signal scoring AI-like. Combined score lands in uncertain band. **This is the correct outcome** — the system should not confidently classify either way.

### Edge Case 3 — Very short texts (< 50 words)

Poems, haiku, or one-liners provide too few tokens for reliable stylometric statistics. **Mitigation:** Add minimum-length check in stylometric function; if text < 50 words, set stylometric score to 0.5 (neutral) and note in audit log. Rely primarily on LLM signal for short texts.

### Edge Case 4 — Rate-limit abuse via distributed IPs

Distributed submission across multiple IPs bypasses per-IP rate limits. **Known limitation** of project-scope implementation; in production, token-bucket strategy keyed on creator_id (after authentication) would be more robust.

---

## Architecture

### Submission Flow

```
POST /submit
    |
    v
[Input Validation]
    | text, creator_id
    v
[Signal 1: Groq LLM]          [Signal 2: Stylometric Heuristics]
    | llm_score (0-1)              | stylometric_score (0-1)
    +--------------+---------------+
                   |
                   v
        [Confidence Scoring]
        confidence = 0.60*llm + 0.40*stylo
                   |
                   v
        [Threshold Mapping]
        attribution: likely_ai | uncertain | likely_human
                   |
                   v
        [Label Generator]
        label: <variant text>
                   |
                   v
        [Audit Logger]
        writes structured entry to SQLite/JSON
                   |
                   v
        [JSON Response]
        content_id, attribution, confidence, label, timestamp
```

### Appeal Flow

```
POST /appeal
    |
    v
[Input Validation]
    | content_id, creator_reasoning
    v
[Log Lookup]
    | find entry by content_id
    v
[Status Check]
    | if already under_review  -> 409
    | if not found             -> 404
    v
[Status Update]
    | status: classified -> under_review
    | append appeal_reasoning, appeal_timestamp
    v
[Audit Logger]
    | update existing entry
    v
[JSON Response]
    | content_id, status: under_review, message
```

### Architecture Narrative

A submitted piece of text enters the system via `POST /submit`, is validated for required fields, and passed to two independent detection signals: a Groq LLM call and a pure-Python stylometric analysis. Their outputs are combined via a weighted average into a single confidence score, mapped through a threshold table to produce an attribution and the exact transparency label text. The complete decision — including both raw signal scores — is written to the audit log before the response is returned.

When a creator submits `POST /appeal`, the system looks up the original log entry by content_id, validates that the submission is not already under review, updates its status, records the creator's reasoning, and returns confirmation. No re-classification occurs; the appeal surfaces in GET /log for human review.

---

## API Surface

### Endpoints

| Method | Path | Description | Rate Limited |
|---|---|---|---|
| POST | /submit | Submit content for attribution analysis | Yes |
| POST | /appeal | File an appeal for a prior classification | No |
| GET | /log | Return recent audit log entries as JSON | No |

### Rate Limiting Rationale

**Chosen limits:** `10 per minute; 100 per day` (per IP address).

**Reasoning:** A typical human creator submitting their own work might upload 2–5 pieces in a session several times a day — 100/day provides generous room. 10/minute prevents scripted flooding without blocking a human submitting several pieces in succession. In production, limits would be keyed on creator_id rather than IP for greater accuracy.

---

## AI Tool Plan

### Milestone 3 — Submission Endpoint + Signal 1 (Groq LLM)

**Spec sections to provide:** Detection Signals (Signal 1), API Surface (POST /submit contract), Architecture diagram (submission flow).

**Ask AI tool to generate:**
1. Flask app skeleton with `POST /submit` route stub accepting `text` and `creator_id`, returning hardcoded response.
2. Standalone `classify_with_llm(text: str) -> float` function calling Groq, parsing `{"ai_probability": <float>}`.

**Verification:** Call function directly with 3 test inputs; confirm returns 0.0–1.0 float; test endpoint with curl; confirm response includes `content_id`, `attribution`, `confidence`, `label` fields.

---

### Milestone 4 — Signal 2 + Confidence Scoring

**Spec sections to provide:** Detection Signals (Signal 2, all three sub-metrics), Uncertainty Representation (threshold map, weighting formula), Architecture diagram (both signals).

**Ask AI tool to generate:**
1. Standalone `classify_with_stylometrics(text: str) -> float` implementing SLV, TTR, PD with normalization.
2. `compute_confidence(llm_score, stylometric_score) -> tuple[float, str]` applying weighted average and threshold map.

**Verification:** Run both signals on 4 test inputs (clearly AI, clearly human, two borderline). Confirm clearly AI ≥ 0.65 combined, clearly human ≤ 0.35. Print sub-metric scores individually if calibration is off.

---

### Milestone 5 — Production Layer

**Spec sections to provide:** Transparency Label Design (all three variant texts + threshold map), Appeals Workflow (full state machine), Architecture diagram (both flows), Rate Limiting Rationale.

**Ask AI tool to generate:**
1. `generate_label(attribution: str, confidence: float) -> str` mapping to exact variant texts.
2. `POST /appeal` endpoint with lookup, status update, log append, response logic.
3. Flask-Limiter setup with `storage_uri="memory://"` on `POST /submit`.
4. `GET /log` returning most recent entries as JSON.

**Verification:** Submit inputs hitting all three confidence ranges — confirm all three label variants returned. Submit valid appeal and check GET /log for `status: under_review` and `appeal_reasoning` populated. Run 12-request rate-limit test; confirm 429 after 10th request.

---

*Document version: 1.0 — pre-implementation. Update version and date whenever this document is revised.*
