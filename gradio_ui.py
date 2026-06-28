"""
Provenance Guard — Gradio UI
Design: Split panel sidebar (Sketch 001-B) + Verdict card (Sketch 002-B)

Run: python gradio_ui.py
     Calls app/ functions directly — no Flask server required.
"""

import uuid
from datetime import datetime, timezone

import gradio as gr
from html import escape
from dotenv import load_dotenv

load_dotenv()

from app.models import audit_log
from app.signals.llm_signal import classify_with_llm
from app.signals.stylometric_signal import classify_with_stylometrics
from app.utils.confidence import compute_confidence
from app.utils.labels import generate_label

# ── Design tokens (mirrors sketch theme) ───────────────────────────────────
_C = {
    "likely_ai":    {"hex": "#f43f5e", "bg": "rgba(244,63,94,.12)",  "border": "rgba(244,63,94,.28)",  "icon": "🤖", "title": "AI-Assisted Content"},
    "likely_human": {"hex": "#10b981", "bg": "rgba(16,185,129,.12)", "border": "rgba(16,185,129,.28)", "icon": "✍️", "title": "Human-Authored Content"},
    "uncertain":    {"hex": "#f59e0b", "bg": "rgba(245,158,11,.12)", "border": "rgba(245,158,11,.28)", "icon": "❓", "title": "Attribution Unclear"},
}

# ── HTML builders ───────────────────────────────────────────────────────────

def _verdict_card(attribution, confidence, llm_score, stylo_score, content_id, label_text):
    c = _C[attribution]
    pct = round(confidence * 100)
    label_html = label_text.replace("\n", "<br>")
    short_id = content_id[:8] + "…"
    return f"""
<div style="border-radius:14px;overflow:hidden;font-family:'Inter',system-ui,sans-serif">
  <div style="background:linear-gradient(135deg,{c['bg']} 0%,transparent 100%);
              border:1px solid {c['border']};border-bottom:none;
              border-radius:14px 14px 0 0;padding:20px 22px 16px">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px">
      <div>
        <div style="font-size:18px;font-weight:700;color:{c['hex']};margin-bottom:3px">
          {c['icon']} {c['title']}
        </div>
        <div style="font-size:11px;color:{c['hex']};opacity:.6">
          ID: <span style="font-family:'JetBrains Mono',monospace">{short_id}</span>
        </div>
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:30px;font-weight:700;
                  color:{c['hex']};line-height:1">{pct}%</div>
    </div>
    <div style="height:7px;background:rgba(255,255,255,.08);border-radius:4px;overflow:hidden">
      <div style="width:{pct}%;height:100%;background:{c['hex']};border-radius:4px"></div>
    </div>
  </div>
  <div style="background:#151826;border:1px solid {c['border']};border-top:none;
              border-radius:0 0 14px 14px;padding:18px 22px">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
      {_signal_chip("LLM Signal", llm_score, c['hex'])}
      {_signal_chip("Stylometric", stylo_score, c['hex'])}
    </div>
    <div style="background:#1e2235;border-radius:8px;padding:14px 16px;
                font-size:13px;line-height:1.7;color:#7c86a1;
                border-left:3px solid {c['hex']}40">
      {label_html}
    </div>
  </div>
</div>"""


def _signal_chip(name, score, color):
    pct = round(score * 100)
    return f"""
<div style="background:#1e2235;border-radius:8px;padding:12px 14px">
  <div style="font-size:10px;font-weight:700;text-transform:uppercase;
              letter-spacing:.06em;color:#4a5270;margin-bottom:4px">{name}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:18px;
              font-weight:700;color:{color};margin-bottom:6px">{score:.2f}</div>
  <div style="height:3px;background:#272b42;border-radius:2px;overflow:hidden">
    <div style="width:{pct}%;height:100%;background:{color}"></div>
  </div>
</div>"""


def _log_table(entries):
    if not entries:
        return "<div style='text-align:center;padding:48px;color:#4a5270;font-family:system-ui;font-size:14px'>No entries yet — submit some content first.</div>"
    rows = ""
    for e in entries:
        attr = e.get("attribution", "uncertain")
        c = _C.get(attr, _C["uncertain"])
        conf = e.get("confidence", 0)
        pct = round(conf * 100)
        status = e.get("status", "classified")
        status_color = "#f59e0b" if status == "under_review" else "#10b981"
        short_id   = escape((e.get("content_id") or "")[:8]) + "…"
        creator    = escape(str(e.get("creator_id", "")))
        attr_safe  = escape(attr)
        status_safe = escape(status)
        ts         = escape((e.get("timestamp") or "")[:16].replace("T", " "))
        rows += f"""
<tr style="border-bottom:1px solid #1a1d2e">
  <td style="padding:11px 14px;font-family:monospace;font-size:11px;color:#4a5270">{short_id}</td>
  <td style="padding:11px 14px;font-size:13px;color:#e2e8f0">{creator}</td>
  <td style="padding:11px 14px">
    <span style="background:{c['bg']};color:{c['hex']};border:1px solid {c['border']};
                 padding:2px 10px;border-radius:999px;font-size:11px;font-weight:700">{attr_safe}</span>
  </td>
  <td style="padding:11px 14px">
    <div style="display:flex;align-items:center;gap:8px">
      <div style="width:52px;height:4px;background:#272b42;border-radius:2px;overflow:hidden">
        <div style="width:{pct}%;height:100%;background:{c['hex']};border-radius:2px"></div>
      </div>
      <span style="font-family:monospace;font-size:12px;color:#7c86a1">{conf:.2f}</span>
    </div>
  </td>
  <td style="padding:11px 14px">
    <span style="color:{status_color};font-size:12px;font-weight:600">{status_safe}</span>
  </td>
  <td style="padding:11px 14px;font-family:monospace;font-size:11px;color:#4a5270">{ts}</td>
</tr>"""
    return f"""
<div style="overflow:auto;font-family:'Inter',system-ui,sans-serif">
  <table style="width:100%;border-collapse:collapse">
    <thead>
      <tr style="border-bottom:1px solid #272b42">
        {''.join(f'<th style="padding:8px 14px;text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:#4a5270;font-weight:700;white-space:nowrap">{h}</th>' for h in ['ID','Creator','Attribution','Confidence','Status','Time'])}
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""


def _page_header(title, sub):
    return f"""
<div style="margin-bottom:24px">
  <h2 style="font-size:22px;font-weight:700;color:#e2e8f0;letter-spacing:-.01em;margin:0 0 4px">{title}</h2>
  <p style="font-size:13px;color:#7c86a1;margin:0">{sub}</p>
</div>"""


def _empty_state(icon, msg):
    return f"""
<div style="background:#151826;border:1px dashed #272b42;border-radius:14px;
            display:flex;flex-direction:column;align-items:center;justify-content:center;
            min-height:260px;gap:12px;font-family:system-ui">
  <span style="font-size:32px;opacity:.25">{icon}</span>
  <span style="font-size:13px;color:#4a5270">{msg}</span>
</div>"""


def _alert(msg, kind="success"):
    colors = {"success": ("#10b981", "rgba(16,185,129,.1)", "rgba(16,185,129,.25)"),
              "error":   ("#f43f5e", "rgba(244,63,94,.1)",  "rgba(244,63,94,.25)")}
    c, bg, border = colors[kind]
    return f'<div style="padding:12px 16px;background:{bg};border:1px solid {border};border-radius:8px;font-size:13px;color:{c};font-family:system-ui;line-height:1.5">{msg}</div>'


# ── Core functions ──────────────────────────────────────────────────────────

def analyze_content(text, creator_id):
    text, creator_id = text.strip(), creator_id.strip()
    if not text or not creator_id:
        return _alert("Both <strong>Text Content</strong> and <strong>Creator ID</strong> are required.", "error")

    try:
        llm_score = classify_with_llm(text)
    except Exception as exc:
        return _alert(f"LLM signal failed: {exc}", "error")

    stylo_score = classify_with_stylometrics(text)
    confidence, attribution = compute_confidence(llm_score, stylo_score)
    label = generate_label(attribution)
    content_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_log.write_entry({
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": timestamp,
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "stylometric_score": stylo_score,
        "status": "classified",
        "appeal_reasoning": None,
        "appeal_timestamp": None,
    })

    return _verdict_card(attribution, confidence, llm_score, stylo_score, content_id, label)


def file_appeal(content_id, reasoning):
    content_id, reasoning = content_id.strip(), reasoning.strip()
    if not content_id or not reasoning:
        return _alert("Both <strong>Content ID</strong> and <strong>Reasoning</strong> are required.", "error")

    try:
        found = audit_log.update_appeal(content_id, reasoning)
    except ValueError:
        return _alert("An appeal has already been filed for this content.", "error")

    if not found:
        return _alert(f"Content ID not found: <code>{escape(content_id)}</code>", "error")

    return _alert("✓ Appeal submitted. A human moderator will review your case.")


def refresh_log():
    entries = audit_log.get_entries(limit=50)
    return _log_table(entries)


def show_panel(target):
    """Return visibility tuple: (analyze, appeal, log)."""
    return (
        gr.update(visible=target == "analyze"),
        gr.update(visible=target == "appeal"),
        gr.update(visible=target == "log"),
    )


def show_log_panel():
    return (*show_panel("log"), _log_table(audit_log.get_entries(limit=50)))


# ── CSS ─────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Reset Gradio container */
.gradio-container {
    background: #0d0f1a !important;
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}
footer { display: none !important; }

/* App row — full height, no gap */
#app-row {
    min-height: 100vh;
    gap: 0 !important;
    align-items: stretch !important;
}
#app-row > .wrap { align-items: stretch !important; }

/* Sidebar column */
#sidebar-col {
    background: #151826 !important;
    border-right: 1px solid #272b42 !important;
    min-height: 100vh !important;
    padding: 0 !important;
}
#sidebar-col > .wrap, #sidebar-col .block { background: transparent !important; border: none !important; padding: 0 !important; }

/* Nav buttons */
#nav-analyze, #nav-appeal, #nav-log {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #7c86a1 !important;
    justify-content: flex-start !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    width: 100% !important;
    margin: 2px 0 !important;
    transition: all 0.12s ease !important;
}
#nav-analyze:hover, #nav-appeal:hover, #nav-log:hover {
    background: #252840 !important;
    color: #e2e8f0 !important;
}

/* Main content column */
#main-col {
    background: #0d0f1a !important;
    padding: 36px 40px !important;
}
#main-col > .wrap, #main-col .block { background: transparent !important; border: none !important; }

/* Panels */
#panel-analyze > .wrap, #panel-appeal > .wrap, #panel-log > .wrap {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* Inputs */
#main-col textarea, #main-col input[type=text] {
    background: #151826 !important;
    border: 1px solid #272b42 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    font-size: 14px !important;
    padding: 12px 14px !important;
    transition: border-color 0.15s ease !important;
}
#main-col textarea:focus, #main-col input[type=text]:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.12) !important;
    outline: none !important;
}
#main-col label span {
    color: #7c86a1 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* Primary action button */
#submit-btn button, #appeal-btn button {
    background: #6366f1 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 11px 20px !important;
    width: 100% !important;
    transition: all 0.12s ease !important;
    box-shadow: none !important;
}
#submit-btn button:hover, #appeal-btn button:hover {
    background: #818cf8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 0 20px rgba(99,102,241,.25) !important;
}

/* Refresh / secondary button */
#refresh-btn button {
    background: transparent !important;
    border: 1px solid #272b42 !important;
    color: #7c86a1 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    transition: all 0.12s ease !important;
    box-shadow: none !important;
}
#refresh-btn button:hover {
    border-color: #6366f1 !important;
    color: #e2e8f0 !important;
}

/* Row gap */
#main-col .gap { gap: 20px !important; }
"""

# ── Layout ──────────────────────────────────────────────────────────────────
LOGO_HTML = """
<div style="padding:20px 16px 16px;border-bottom:1px solid #272b42;margin-bottom:12px">
  <div style="display:flex;align-items:center;gap:10px">
    <div style="width:30px;height:30px;background:linear-gradient(135deg,#6366f1,#a78bfa);
                border-radius:8px;display:flex;align-items:center;justify-content:center;
                font-size:16px;flex-shrink:0">🛡</div>
    <div>
      <div style="font-size:14px;font-weight:700;color:#e2e8f0;letter-spacing:-.01em;
                  font-family:'Inter',system-ui">Provenance Guard</div>
      <div style="font-size:10px;color:#4a5270;font-family:'Inter',system-ui">
        AI Content Attribution
      </div>
    </div>
  </div>
</div>"""

SIDEBAR_FOOTER_HTML = """
<div style="padding:16px;border-top:1px solid #272b42;position:absolute;bottom:0;left:0;right:0;background:#151826">
  <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#4a5270;font-family:system-ui">
    <span style="width:6px;height:6px;border-radius:50%;background:#22c55e;display:inline-block"></span>
    API · localhost:5000
  </div>
  <div style="margin-top:6px">
    <a href="http://localhost:5000/apidocs" target="_blank"
       style="font-size:11px;color:#6366f1;text-decoration:none;font-family:system-ui">
      Swagger Docs ↗
    </a>
  </div>
</div>"""

with gr.Blocks(title="Provenance Guard") as demo:

    with gr.Row(elem_id="app-row"):

        # ── Sidebar ────────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=240, elem_id="sidebar-col"):
            gr.HTML(LOGO_HTML)
            gr.HTML('<div style="padding:8px 16px 4px;font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#4a5270;font-weight:700;font-family:\'Inter\',system-ui">Detection</div>')
            nav_analyze = gr.Button("🔍  Analyze Content", elem_id="nav-analyze")
            nav_appeal  = gr.Button("📝  File Appeal",     elem_id="nav-appeal")
            gr.HTML('<div style="padding:12px 16px 4px;font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#4a5270;font-weight:700;font-family:\'Inter\',system-ui">History</div>')
            nav_log = gr.Button("📋  Audit Log", elem_id="nav-log")
            gr.HTML(SIDEBAR_FOOTER_HTML)

        # ── Main content ───────────────────────────────────────────────────
        with gr.Column(scale=4, elem_id="main-col"):

            # Analyze panel
            with gr.Group(visible=True, elem_id="panel-analyze") as panel_analyze:
                gr.HTML(_page_header("Analyze Content",
                    "Submit text for dual-signal AI attribution — LLM semantic + stylometric structural"))
                with gr.Row():
                    with gr.Column(scale=1):
                        text_input    = gr.Textbox(label="Text Content",
                                                   placeholder="Paste the content to analyze — poem, story excerpt, blog post, song lyrics…",
                                                   lines=9)
                        creator_input = gr.Textbox(label="Creator ID",
                                                   placeholder="e.g. poet_alice or user_12345")
                        submit_btn    = gr.Button("Analyze Content →", elem_id="submit-btn")
                    with gr.Column(scale=1):
                        result_out = gr.HTML(_empty_state("🔍", "Results will appear here"))

            # Appeal panel
            with gr.Group(visible=False, elem_id="panel-appeal") as panel_appeal:
                gr.HTML(_page_header("File Appeal",
                    "Contest a prior classification — a human moderator will review your case"))
                with gr.Row():
                    with gr.Column(scale=1, min_width=480):
                        appeal_id_input     = gr.Textbox(label="Content ID",
                                                         placeholder="UUID from your /submit response")
                        appeal_reason_input = gr.Textbox(label="Your Reasoning",
                                                         placeholder="Explain why you believe the classification is incorrect…",
                                                         lines=5)
                        appeal_btn          = gr.Button("Submit Appeal →", elem_id="appeal-btn")
                        appeal_out          = gr.HTML()
                    with gr.Column(scale=1):
                        gr.HTML("""
<div style="background:#151826;border:1px solid #272b42;border-radius:12px;padding:20px 22px;
            font-family:'Inter',system-ui;font-size:13px;line-height:1.7;color:#7c86a1">
  <div style="font-weight:600;color:#e2e8f0;margin-bottom:10px">How appeals work</div>
  <ul style="padding-left:18px;margin:0;display:flex;flex-direction:column;gap:8px">
    <li>Find your <strong style="color:#e2e8f0">Content ID</strong> in the Audit Log or your original submission response.</li>
    <li>Describe why the classification is wrong. Be specific — include context about your writing process.</li>
    <li>Status changes to <strong style="color:#f59e0b">under_review</strong> immediately.</li>
    <li>A human moderator reviews flagged entries via <strong style="color:#e2e8f0">GET /log</strong>.</li>
    <li>One appeal per submission — make it count.</li>
  </ul>
</div>""")

            # Log panel
            with gr.Group(visible=False, elem_id="panel-log") as panel_log:
                with gr.Row():
                    gr.HTML(_page_header("Audit Log",
                        "All attribution decisions — appeal entries surface here for human review"))
                    refresh_btn = gr.Button("↻ Refresh", elem_id="refresh-btn", scale=0)
                log_out = gr.HTML(_log_table([]))

    # ── Event wiring ───────────────────────────────────────────────────────

    # Nav → panel visibility
    nav_analyze.click(
        fn=lambda: show_panel("analyze"),
        outputs=[panel_analyze, panel_appeal, panel_log],
    )
    nav_appeal.click(
        fn=lambda: show_panel("appeal"),
        outputs=[panel_analyze, panel_appeal, panel_log],
    )
    nav_log.click(
        fn=show_log_panel,
        outputs=[panel_analyze, panel_appeal, panel_log, log_out],
    )

    # Analyze submit
    submit_btn.click(
        fn=analyze_content,
        inputs=[text_input, creator_input],
        outputs=[result_out],
    )

    # Appeal submit
    appeal_btn.click(
        fn=file_appeal,
        inputs=[appeal_id_input, appeal_reason_input],
        outputs=[appeal_out],
    )

    # Log refresh
    refresh_btn.click(fn=refresh_log, outputs=[log_out])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, css=CSS)
