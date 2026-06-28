# Attribution Result Display

## Design Decisions

**Verdict Card** won over Score Gauge and Banner.

- Color-coded gradient header: `--color-ai` (rose `#f43f5e`), `--color-human` (emerald `#10b981`), `--color-uncertain` (amber `#f59e0b`)
- Three zones: header (verdict + confidence %), body (signal chips + confidence bar), footer (label text + appeal button)
- Signal chips are always shown side-by-side (LLM | Stylometric) with individual scores and mini bars — never collapsed
- Label text displayed inline in the card; not hidden behind a toggle or tooltip
- Appeal button appears only in footer, ghost style, right-aligned

**Why it won:** Verdict Card front-loads the decision (header is unmistakable at a glance) while preserving explainability (signal breakdown is always visible). Score Gauge (A) was visually impressive but buried the label text; Banner (C) lacked signal breakdown.

**Rejected:** Gauge — SVG arc animation is clever but the signal cards below it duplicated vertical space; Banner — one-line format collapses too much info.

## Color Tokens

```css
/* Semantic signal colors — defined in default.css */
--color-ai:        #f43f5e;   /* rose-500 */
--color-human:     #10b981;   /* emerald-500 */
--color-uncertain: #f59e0b;   /* amber-500 */

/* Gradient headers per attribution */
/* likely_ai    */ background: linear-gradient(135deg, #2d0a14, #4a0e20);
/* likely_human */ background: linear-gradient(135deg, #052e1c, #064e32);
/* uncertain    */ background: linear-gradient(135deg, #2d1b00, #4a2e00);
```

## CSS Patterns

```css
/* Verdict card shell */
.verdict-card {
  border-radius: var(--radius-xl);
  overflow: hidden;
  animation: fadeUp .3s ease;
  box-shadow: var(--shadow-md);
}

/* Header — color varies by attribution */
.verdict-header {
  padding: var(--space-6) var(--space-6) var(--space-5);
  /* background set inline from _C dict */
}

/* Icon ring */
.verdict-icon-ring {
  width: 48px; height: 48px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  /* background: rgba(<signal-color>, .15) */
}

/* Confidence % — mono, large */
.verdict-pct {
  font-family: var(--font-mono);
  font-size: var(--text-4xl);
  font-weight: 700;
  line-height: 1;
}

/* Confidence progress bar */
.confidence-bar {
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
  margin-top: var(--space-3);
}
.confidence-fill {
  height: 100%;
  border-radius: 3px;
  /* background: <signal-color> */
  /* width: <confidence * 100>% — animated */
  animation: fillBar .6s ease forwards;
}

/* Signal chip pair */
.signal-chips { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.signal-chip {
  background: var(--color-surface-raised);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}
.signal-chip-name {
  font-size: var(--text-xs); font-weight: 600;
  text-transform: uppercase; letter-spacing: .06em;
  color: var(--color-text-dim); margin-bottom: var(--space-2);
}
.signal-chip-score {
  font-family: var(--font-mono);
  font-size: var(--text-2xl); font-weight: 700;
  margin-bottom: var(--space-2);
}
.signal-chip-bar { height: 4px; background: var(--color-border); border-radius: 2px; overflow: hidden; }
.signal-chip-fill { height: 100%; border-radius: 2px; }

/* Label text box */
.label-box {
  background: var(--color-surface-raised);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-5);
  font-size: var(--text-sm); line-height: 1.65;
  color: var(--color-text-muted);
  margin-top: var(--space-5);
  position: relative;
}
.label-box::before {
  content: 'Label';
  position: absolute; top: -8px; left: 12px;
  background: var(--color-surface-raised);
  padding: 0 6px; font-size: 10px;
  text-transform: uppercase; letter-spacing: .06em;
  color: var(--color-text-dim);
}

/* Appeal row */
.appeal-row { margin-top: var(--space-5); display: flex; justify-content: flex-end; }

/* Fade-up entrance animation */
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
@keyframes fillBar { from{width:0} to{width:var(--target-w)} }
```

## HTML Structure

```html
<div class="verdict-card">
  <!-- Header: colored gradient by attribution -->
  <div class="verdict-header" style="background: linear-gradient(...)">
    <div class="verdict-header-row">
      <div class="verdict-icon-ring">🤖 / 👤 / ❓</div>
      <div>
        <div class="verdict-title">AI-Assisted / Human-Authored / Attribution Unclear</div>
        <div class="verdict-sub">Short descriptor</div>
      </div>
      <div class="verdict-pct">87%</div>
    </div>
    <!-- Confidence bar -->
    <div class="confidence-bar">
      <div class="confidence-fill" style="--target-w: 87%; background: #f43f5e;"></div>
    </div>
  </div>

  <!-- Body: signal chips -->
  <div class="verdict-body" style="background: var(--color-surface); padding: var(--space-5);">
    <div class="signal-chips">
      <div class="signal-chip">
        <div class="signal-chip-name">LLM Signal</div>
        <div class="signal-chip-score" style="color: #f43f5e;">0.91</div>
        <div class="signal-chip-bar"><div class="signal-chip-fill" style="width:91%;background:#f43f5e;"></div></div>
      </div>
      <div class="signal-chip">
        <div class="signal-chip-name">Stylometric</div>
        <div class="signal-chip-score" style="color: #f43f5e;">0.80</div>
        <div class="signal-chip-bar"><div class="signal-chip-fill" style="width:80%;background:#f43f5e;"></div></div>
      </div>
    </div>

    <!-- Label text — always visible -->
    <div class="label-box">AI-Assisted Content\nThis content shows strong indicators of AI generation...</div>

    <!-- Appeal -->
    <div class="appeal-row">
      <button class="btn btn-ghost btn-sm">📝 File Appeal</button>
    </div>
  </div>
</div>
```

## Python Implementation Notes

In `gradio_ui.py`, the `_C` dict maps attribution to color tokens:
```python
_C = {
    "likely_ai":    {"color": "#f43f5e", "bg": "linear-gradient(135deg,#2d0a14,#4a0e20)", "icon": "🤖", "title": "AI-Assisted Content"},
    "likely_human": {"color": "#10b981", "bg": "linear-gradient(135deg,#052e1c,#064e32)", "icon": "👤", "title": "Human-Authored Content"},
    "uncertain":    {"color": "#f59e0b", "bg": "linear-gradient(135deg,#2d1b00,#4a2e00)", "icon": "❓", "title": "Attribution Unclear"},
}
```
`_verdict_card()` builds the card HTML. `_signal_chip()` builds each chip. All user-controlled values (`creator_id`, `content_id`, `attr`, label text) are passed through `html.escape()` before f-string interpolation to prevent XSS.

## What to Avoid

- **Hiding the signal breakdown** — gauge-style cards that show only a final number lose the explainability that makes users trust the result
- **Collapsible label text** — the label is part of the public API contract; always show it
- **Per-call color overrides** — colors are defined in `_C`; add attributions there, not at call sites
- **Raw string interpolation** — any user-controlled value in HTML must go through `html.escape()`

## Origin
Synthesized from sketch 002.
Source file: `sources/002-result-display/index.html`
