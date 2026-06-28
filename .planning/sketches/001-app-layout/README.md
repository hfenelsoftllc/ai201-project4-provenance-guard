---
sketch: "001"
name: app-layout
question: "How should the three API surfaces (Submit / Appeal / Log) be organized?"
winner: "B"
tags: [layout, navigation, gradio]
---

# Sketch 001: App Layout

## Design Question
How should the three API surfaces (Submit / Appeal / Log) be organized into a single Gradio UI?

## How to View
Open `.planning/sketches/001-app-layout/index.html` in a browser.

## Variants
- **A: Tab Navigation** — header + segmented tab bar + two-column content area. Most natural Gradio pattern (`gr.Tab`). Familiar, scannable, low friction.
- **B: Split Panel** — persistent sidebar nav + main content area. Command-center feel. Better for power users who switch contexts often.
- **C: Centered Card** — minimalist hero landing + single card with inner tabs. Clean, focused, works best for single-task users.

## What to Look For
- Which layout feels most natural for a **technical API demo tool**?
- Does the sidebar (B) feel necessary or over-engineered for 3 endpoints?
- Does the centered card (C) feel too sparse for a developer tool?
- The inline result card renders in each variant after clicking submit — does the two-column (A/B) or inline (C) result placement feel better?
