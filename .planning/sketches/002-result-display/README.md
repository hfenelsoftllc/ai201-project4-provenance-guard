---
sketch: "002"
name: result-display
question: "How should the attribution result be displayed after a submission?"
winner: "B"
tags: [result, attribution, confidence, label]
---

# Sketch 002: Attribution Result Display

## Design Question
How should the attribution result (confidence score + attribution + label text) be presented after POST /submit returns?

## How to View
Open `.planning/sketches/002-result-display/index.html` in a browser.
Use the state buttons to cycle between all three attribution outcomes (AI / Human / Uncertain).

## Variants
- **A: Score Gauge** — SVG half-donut gauge showing confidence %, attribution label below, two signal breakdowns, transparency label text in a bordered box. Visually dramatic.
- **B: Verdict Card** — Color-coded card header (gradient + border) carrying the verdict + score, body with signal bars + full label text. Information-dense, professional.
- **C: Minimal Banner** — Thin color strip (verdict + %) + expandable body with progress bar, detail grid, and collapsible transparency label. Cleanest at rest, full detail on demand.

## What to Look For
- Click all three state buttons in each variant — which handles the **uncertain** state most gracefully?
- Which conveys the **two-signal breakdown** (LLM vs Stylometric) most clearly?
- Is the **full transparency label text** (multi-line) readable and appropriately weighted?
- Variant C's expandable label — does lazy disclosure feel right, or should it always be visible?
- Which design would feel at home in a Gradio `gr.Blocks` layout?
