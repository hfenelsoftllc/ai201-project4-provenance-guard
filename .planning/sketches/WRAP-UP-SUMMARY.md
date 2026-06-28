# Sketch Wrap-Up Summary — Provenance Guard UI

## Sketches Processed

| # | Name | Winner | Design Question |
|---|------|--------|----------------|
| 001 | app-layout | B: Split Panel | How should Submit / Appeal / Log be organized? |
| 002 | result-display | B: Verdict Card | How should the attribution result be displayed? |

## Skill Package

Created at: `.claude/skills/sketch-findings-provenance-guard/`

```
SKILL.md                                  ← load instructions + invariants
references/
  layout-and-navigation.md               ← CSS patterns, HTML structure, anti-patterns
  attribution-result-display.md          ← color tokens, card structure, XSS guards
sources/
  themes/default.css                     ← design token system
  001-app-layout/index.html              ← 3-variant layout sketch
  002-result-display/index.html          ← 3-variant result sketch
```

## Key Decisions Captured

**Layout (001-B):**
- 240px fixed sidebar, dark surface, toggled main panels
- Section labels (Detection / History) above nav groups
- Log nav item carries entry-count badge
- Sidebar footer: API status + Swagger link

**Result Display (002-B):**
- Gradient header color-coded by attribution (rose/emerald/amber)
- Confidence % in mono font, large, in header
- Signal chips always visible (LLM + Stylometric side-by-side)
- Label text inline in card, never behind toggle
- Appeal button in card footer, ghost style

**Design Tokens (from `default.css`):**
- Bg: `#0d0f1a` / Surface: `#151826` / Primary: `#6366f1`
- AI: `#f43f5e` / Human: `#10b981` / Uncertain: `#f59e0b`
- Fonts: Inter (UI) + JetBrains Mono (scores/IDs)

## Invariants for Future Builds

1. Color tokens live in `_C` dict — never override at call sites
2. `html.escape()` on all user-controlled values before HTML interpolation
3. Signal chips always visible — no collapsing
4. Label text always shown inline
5. Sidebar via `gr.Column` + CSS — not `gr.Tab`

## Implementation Reference

`gradio_ui.py` at project root implements all winning patterns:
- `_verdict_card()` — Variant B result display
- `_signal_chip()` — individual signal score chip
- `_log_table()` — audit log with escaped values
- `show_panel()` — sidebar navigation toggling
- CSS string with all design tokens and `.nav-btn`, `.nav-badge`, `.sidebar-footer` classes
