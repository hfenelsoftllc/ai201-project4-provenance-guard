# Sketch Manifest — Provenance Guard UI

## Design Direction
Sleek dark-mode tool UI targeting Gradio (`gr.Blocks`). Dark slate background (#0d0f1a) with indigo primary accent and three semantic signal colors: rose for AI-detected, emerald for human, amber for uncertain. Typography: Inter for UI copy, JetBrains Mono for scores and IDs. The aesthetic is a professional developer tool, not a consumer app — information-dense but uncluttered.

## Reference Points
- Gradio Blocks dark theme (native implementation target)
- OpenAI Playground (clean monochrome + accent)
- Vercel dashboard (dark, tight typography, status indicators)

## Sketches

| # | Name | Design Question | Winner | Tags |
|---|------|----------------|--------|------|
| 001 | app-layout | How should Submit / Appeal / Log be organized? | B: Split Panel | layout, navigation, gradio |
| 002 | result-display | How should the attribution result be displayed? | B: Verdict Card | result, attribution, confidence |
