# Layout & Navigation

## Design Decisions

**Split-panel sidebar layout** won over tab-nav and centered-card.

- 240px fixed sidebar, dark surface (`#151826`), `border-right: 1px solid #272b42`
- Main content area (`background: #0d0f1a`) toggled via panel visibility
- Three nav items: Analyze Content / File Appeal / Audit Log
- Section labels above nav groups (Detection / History) in 10px uppercase dimmed text
- Sidebar footer: API status dot + Swagger link, pinned to bottom
- Log nav item carries an entry-count badge

**Why it won:** Persistent sidebar keeps navigation visible at all times; better than tabs when users need to switch between submitting content and reviewing appeals. Badge on Log provides passive awareness.

**Rejected:** Tab navigation (A) — natural Gradio pattern but hides nav behind click; Centered card (C) — too minimal for a tool with three distinct workflows.

## CSS Patterns

```css
/* Sidebar column */
#sidebar-col {
  background: #151826;
  border-right: 1px solid #272b42;
  min-height: 100vh;
  padding: 0;
  width: 240px;
  position: relative;
}

/* Nav buttons — unstyled, left-aligned */
.nav-btn {
  width: 100%;
  justify-content: flex-start;
  background: transparent;
  border: none;
  color: #7c86a1;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.12s ease;
}
.nav-btn:hover {
  background: #252840;
  color: #e2e8f0;
}
.nav-btn.active {
  background: rgba(99,102,241,.15);
  color: #818cf8;
}

/* Section label */
.nav-section {
  padding: 8px 16px 4px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: #4a5270;
  font-weight: 700;
}

/* Badge */
.nav-badge {
  margin-left: auto;
  background: #6366f1;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 9999px;
}

/* Sidebar footer */
.sidebar-footer {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 16px;
  border-top: 1px solid #272b42;
  background: #151826;
}

/* Main content */
#main-col {
  background: #0d0f1a;
  padding: 36px 40px;
  flex: 1;
}

/* Page header pattern */
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: -.01em;
  margin: 0 0 4px;
}
.page-sub {
  font-size: 13px;
  color: #7c86a1;
  margin: 0 0 24px;
}
```

## HTML Structures

```html
<!-- App shell -->
<div class="app-layout" style="display:grid;grid-template-columns:240px 1fr;min-height:100vh">

  <!-- Sidebar -->
  <aside id="sidebar-col">
    <div class="sidebar-head"><!-- logo --></div>
    <div class="nav-section">Detection</div>
    <button class="nav-btn active">🔍  Analyze Content</button>
    <button class="nav-btn">📝  File Appeal</button>
    <div class="nav-section">History</div>
    <button class="nav-btn">
      📋  Audit Log
      <span class="nav-badge">3</span>
    </button>
    <div class="sidebar-footer">
      <span class="status-dot"></span> API · localhost:5000
    </div>
  </aside>

  <!-- Main content — panels toggled by nav -->
  <main id="main-col">
    <div id="panel-analyze" class="panel active">...</div>
    <div id="panel-appeal"  class="panel">...</div>
    <div id="panel-log"     class="panel">...</div>
  </main>

</div>
```

## What to Avoid

- **Tab nav** (`gr.Tab`) as primary structure — tabs hide the navigation; sidebar keeps context visible
- **Centered card** — too minimal, collapses three distinct workflows into one cramped card
- Nav items without section labels — the Detection/History grouping clarifies what each panel does

## Origin
Synthesized from sketch 001.
Source file: `sources/001-app-layout/index.html`
