---
name: sketch-findings-provenance-guard
description: Design decisions from UI sketches for Provenance Guard — split-panel sidebar layout and verdict card result display. Load when building or modifying the Gradio UI.
applies_to:
  - gradio_ui.py
  - any future frontend work for this project
---

# Sketch Findings — Provenance Guard UI

Design decisions from two UI sketches, frozen at wrap-up. These reference files are the source of truth for UI patterns in `gradio_ui.py`.

## Reference Files

| File | Covers |
|------|--------|
| `references/layout-and-navigation.md` | Split-panel sidebar, nav buttons, section labels, badge, footer |
| `references/attribution-result-display.md` | Verdict card, color tokens, signal chips, label text placement, XSS guards |

## Source Files

Raw HTML sketches — read these when you need the full interactive prototype:

| File | Sketch |
|------|--------|
| `sources/001-app-layout/index.html` | Three layout variants (A: tabs, B★: split panel, C: centered card) |
| `sources/002-result-display/index.html` | Three result variants (A: gauge, B★: verdict card, C: banner) |
| `sources/themes/default.css` | Design token system (colors, spacing, typography, shadows) |

## Winners

- **001 App Layout → Variant B** — Split Panel sidebar (persistent 240px left nav, toggled panels in main area)
- **002 Result Display → Variant B** — Verdict Card (gradient header by attribution, always-visible signal chips and label text)

## Key Invariants

These must hold in any future UI work:

1. **Color tokens** — `--color-ai: #f43f5e`, `--color-human: #10b981`, `--color-uncertain: #f59e0b`. Change in `_C` dict only.
2. **XSS prevention** — `html.escape()` on every user-controlled value before HTML interpolation (creator_id, content_id, attr, label text, status).
3. **Signal chips always visible** — never collapse LLM / Stylometric scores behind a toggle.
4. **Label text always shown** — the label is part of the API contract; do not hide it.
5. **Sidebar nav** — use `gr.Column` + CSS + `gr.Group` visibility toggling; do not switch to `gr.Tab` as primary structure.

## How to Use

When asked to modify or extend the Gradio UI, read the relevant reference file first:

- Layout / navigation changes → `references/layout-and-navigation.md`
- Result display / verdict card changes → `references/attribution-result-display.md`
- Adding a new attribution state → update `_C` dict in `gradio_ui.py` and the color token table in `references/attribution-result-display.md`
