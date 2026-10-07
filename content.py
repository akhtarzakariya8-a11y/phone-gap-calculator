"""Look and feel: dashboard CSS, small HTML card helpers, and the static
sections (comparison grid, notes, sources). Kept apart from app.py so the
logic stays easy to read.

Design: navy sidebar, light grey page, white rounded cards (dashboard style).
"""

from html import escape

DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
    --navy: #24386f; --navy-dark: #17264c; --blue: #1f6fd5; --pink: #f23882;
    --green: #16b978; --orange: #e8753d; --page: #f4f6fa; --card: #ffffff;
    --line: #e7eaf0; --text: #172033; --muted: #7b8497; --radius: 16px;
    --shadow: 0 4px 18px rgba(23, 32, 51, .055);
}
html, body, [class*="css"], .stApp { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.stApp { background: var(--page); color: var(--text); }
[data-testid="stMainBlockContainer"], .block-container { max-width: 1400px; padding: 3.2rem 2.4rem 4rem 2.4rem; }
#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* Sidebar */
section[data-testid="stSidebar"] { background: var(--navy-dark); border-right: 0; }
section[data-testid="stSidebar"] * { color: #fff; }
.sidebar-brand { padding: 8px 10px 22px 10px; }
.sidebar-brand-name { font-size: 20px; font-weight: 800; letter-spacing: -0.4px; }
.sidebar-brand-sub { color: rgba(255,255,255,.56) !important; font-size: 11px; margin-top: 4px; text-transform: uppercase; letter-spacing: .09em; }
.sidebar-section { color: rgba(255,255,255,.45) !important; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .11em; margin: 17px 10px 7px; }
.sidebar-link { display: flex; align-items: center; gap: 11px; padding: 10px 12px; margin: 3px 0; border-radius: 8px; color: rgba(255,255,255,.78) !important; text-decoration: none !important; font-size: 14px; font-weight: 500; }
.sidebar-link:hover { background: rgba(255,255,255,.08); color: #fff !important; }
.sidebar-link.active { background: var(--blue); color: #fff !important; }
.sidebar-icon { width: 18px; text-align: center; opacity: .9; }
.sidebar-note { padding: 0 10px; color: rgba(255,255,255,.5) !important; font-size: 11px; line-height: 1.55; }

/* Header */
.eyebrow { color: var(--muted); font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: .11em; margin-bottom: 3px; }
.dashboard-title { color: var(--text); font-size: 30px; line-height: 1.15; font-weight: 800; letter-spacing: -.7px; margin: 0 0 4px; }
.dashboard-subtitle { color: var(--muted); font-size: 14px; margin-bottom: 14px; max-width: 70ch; }
.dashboard-subtitle b { color: var(--pink); }

/* Inputs and buttons */
div[data-baseweb="input"] > div { background: #f6f7fa !important; border: 1px solid #eef0f4 !important; border-radius: 8px !important; }
div[data-baseweb="input"] input { color: var(--text) !important; }
.stTextInput label, .stNumberInput label { color: #4c566b !important; font-size: 12px !important; font-weight: 600 !important; }
.stButton > button, .stFormSubmitButton > button { border-radius: 8px; min-height: 42px; font-weight: 700; }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primaryFormSubmit"], .stFormSubmitButton > button[kind="primary"] {
    background: var(--navy-dark); border-color: var(--navy-dark); color: white; }
[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] { background: #fff; border: 1px solid var(--line) !important; border-radius: 13px; box-shadow: var(--shadow); }

/* Cards */
.card { background: var(--card); border: 1px solid rgba(25,36,60,.055); border-radius: var(--radius); box-shadow: var(--shadow); padding: 18px 20px; margin-bottom: 16px; }
.card-title-row { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; margin-bottom: 14px; border-bottom: 1px solid #f0f1f4; }
.card-title { color: var(--text); font-size: 14px; font-weight: 750; }
.card-kicker { color: var(--muted); font-size: 12px; font-weight: 500; margin-top: 2px; }
.card-menu { color: #a2a9b7; font-size: 18px; letter-spacing: 2px; }
.card a { color: var(--navy); }

/* Headline money */
.money { font-size: 44px; line-height: 1; font-weight: 800; color: var(--text); letter-spacing: -1.4px; font-variant-numeric: tabular-nums; }
.money-period { color: var(--muted); font-size: 13px; margin-top: 8px; }
.money-period b { color: var(--text); }
.range-box { display: inline-block; margin-top: 16px; padding: 7px 10px; background: #f6f7fa; border-radius: 7px; color: #596277; font-size: 12px; }
.range-box b { color: var(--text); }
.metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 16px; }
.mini-metric { padding: 11px; background: #fafbfc; border: 1px solid #f0f1f4; border-radius: 9px; }
.mini-value { font-size: 18px; font-weight: 800; color: var(--text); font-variant-numeric: tabular-nums; }
.mini-label { color: var(--muted); font-size: 11px; margin-top: 3px; line-height: 1.3; }

/* Bars */
.bar-row { display: grid; grid-template-columns: 150px 1fr 70px; align-items: center; gap: 10px; margin: 16px 0; }
.bar-label { color: #596277; font-size: 12px; }
.bar-track { width: 100%; height: 9px; background: #eef1f5; border-radius: 100px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--blue); border-radius: 100px; }
.bar-value { text-align: right; color: var(--text); font-size: 12px; font-weight: 700; font-variant-numeric: tabular-nums; }

/* Reviews */
.review { display: grid; grid-template-columns: 34px 1fr auto; gap: 11px; align-items: start; padding: 12px 0; border-bottom: 1px solid #f0f1f4; }
.review:last-of-type { border-bottom: 0; }
.review-icon { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; background: #f5f6f9; border-radius: 8px; color: var(--navy); }
.review-text { font-size: 13px; line-height: 1.45; color: #30394c; }
.review-meta { color: var(--muted); font-size: 11px; margin-top: 3px; }
.review-meta a { color: var(--navy); text-decoration: none; }
.pill { white-space: nowrap; display: inline-flex; align-items: center; padding: 4px 8px; border-radius: 99px; font-size: 10px; font-weight: 750; }
.pill-pink { color: #d72d72; background: #fff0f6; }
.pill-orange { color: #c55d29; background: #fff4ed; }
.pill-blue { color: #1764bb; background: #edf5ff; }

/* Profile details */
.detail-row { display: flex; justify-content: space-between; gap: 18px; padding: 9px 0; border-bottom: 1px solid #f1f2f5; font-size: 12.5px; }
.detail-row:last-of-type { border-bottom: 0; }
.detail-label { color: var(--muted); flex-shrink: 0; }
.detail-value { color: var(--text); font-weight: 600; text-align: right; min-width: 0; overflow-wrap: anywhere; }
.detail-value small { display: block; color: var(--muted); font-weight: 400; font-size: 11px; }
.match-note { color: var(--muted); font-size: 12px; line-height: 1.45; margin: -4px 0 6px; }
.flag { border-radius: 8px; padding: 9px 11px; font-size: 12px; line-height: 1.45; margin-top: 10px; }
.flag-warn { background: #fff4ed; color: #a4491c; }
.flag-info { background: #edf5ff; color: #1764bb; }
.flag-note { background: #f6f7fa; color: #596277; }

/* Donut */
.donut-wrap { display: flex; align-items: center; justify-content: center; gap: 28px; padding: 7px 0; }
.donut { width: 145px; height: 145px; border-radius: 50%; position: relative; flex-shrink: 0; }
.donut::after { content: ""; position: absolute; inset: 25px; background: white; border-radius: 50%; }
.donut-centre { position: absolute; z-index: 2; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.donut-big { font-size: 24px; font-weight: 800; }
.donut-small { color: var(--muted); font-size: 10px; }
.legend-row { display: flex; align-items: center; gap: 7px; margin: 9px 0; font-size: 12.5px; }
.legend-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.dot-pink { background: var(--pink); } .dot-grey { background: #dfe4eb; }

/* Source tags on inputs */
.source-tag { display: inline-block; padding: 3px 7px; border-radius: 5px; background: #eef3fa; color: #50617c; font-size: 10px; font-weight: 700; white-space: nowrap; }
.tag-assumption { background: #fff4e8; color: #a45a18; }
.tag-lookup { background: #edf7f4; color: #217762; }
.tag-nesti { background: #fff0f6; color: #bd336c; }
.input-label { padding-top: 6px; font-size: 13px; font-weight: 650; color: var(--text); }
.input-note { font-size: 11.5px; color: var(--muted); line-height: 1.4; margin-top: 2px; }
.input-note a, .note a { color: var(--navy); }

/* Sales opener */
.sales-opener { border-left: 4px solid var(--pink); background: #fff7fa; border-radius: 0 10px 10px 0; padding: 13px 15px; color: #30394c; font-size: 13.5px; line-height: 1.55; }

/* Tables (workings + comparison grid) */
.table-scroll { overflow-x: auto; }
.table-scroll table { border-collapse: collapse; width: 100%; margin: 0; border: 0; }
.table-scroll th { text-align: left; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); padding: 9px 10px; border: 0; border-bottom: 1px solid var(--line); background: #fafbfc; vertical-align: bottom; }
.table-scroll td { padding: 10px; border: 0; border-bottom: 1px solid #f1f2f5; vertical-align: top; font-size: 13px; color: var(--text); }
.table-scroll tr:last-child td, .table-scroll tr:last-child th { border-bottom: 0; }
.sheet { min-width: 640px; }
.sheet .ref { font-weight: 700; color: var(--muted); width: 2.4em; }
.sheet td.w { color: var(--muted); font-size: 12.5px; }
.sheet .r { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
.sheet tr.money-row td { font-weight: 800; }
.sheet tr.recov td.r { color: #0f8a5a; font-weight: 700; }
.sheet tr.soft td { background: #fafbfc; }
.fit { min-width: 760px; }
.fit tbody th { font-size: 13px; font-weight: 650; letter-spacing: 0; text-transform: none; color: var(--text); background: #fff; width: 170px; vertical-align: top; position: sticky; left: 0; z-index: 1; }
.fit thead th:first-child { position: sticky; left: 0; z-index: 1; }
.fit th small { display: block; font-size: 11px; font-weight: 400; letter-spacing: 0; text-transform: none; margin-top: 3px; }
.fit .us { background: #fff7fa; }
.st { display: inline-block; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 999px; margin-bottom: 5px; white-space: nowrap; }
.st-yes { background: #e8f8f1; color: #0f8a5a; }
.st-part { background: #edf5ff; color: #1764bb; }
.st-ns { color: var(--muted); box-shadow: inset 0 0 0 1px var(--line); }
.st-no { background: #f4f5f8; color: var(--muted); }
.fit .d { display: block; color: var(--muted); font-size: 12px; line-height: 1.4; }
.ref { font-size: 10px; font-weight: 700; text-decoration: none; color: var(--blue) !important; }
.answer-quote { font-size: 19px; font-weight: 700; line-height: 1.35; color: var(--text); letter-spacing: -.3px; }
.answer-quote em { font-style: normal; color: var(--pink); }

/* Lists and misc */
.note { font-size: 13px; color: #30394c; line-height: 1.5; padding-left: 18px; margin: 0; }
.note li { margin-bottom: 7px; }
.src-list { padding-left: 24px; margin: 0; font-size: 13px; }
.src-list li { margin-bottom: 6px; color: var(--muted); }
.src-list a { color: var(--navy); font-weight: 600; text-decoration: none; }
.caveat { color: #8a92a1; font-size: 11px; line-height: 1.5; margin-top: 12px; }
.section-heading { margin: 10px 0 4px; color: var(--text); font-size: 18px; font-weight: 800; }
.empty-state { color: #7b8497; font-size: 12.5px; padding: 8px 0; }

@media (max-width: 900px) {
    [data-testid="stMainBlockContainer"], .block-container { padding-left: 1rem; padding-right: 1rem; }
    .metric-grid { grid-template-columns: 1fr; }
    .bar-row { grid-template-columns: 110px 1fr 55px; }
    .donut-wrap { flex-direction: column; }
    .money { font-size: 36px; }
}
</style>
"""


def safe_url(url):
    return url if isinstance(url, str) and url.startswith(("https://", "http://")) else None


def link(url, text):
    u = safe_url(url)
    return (f'<a href="{escape(u)}" target="_blank" rel="noopener noreferrer">{escape(str(text))}</a>'
            if u else escape(str(text)))


def card(title, body, kicker="", anchor=None):
    """A white dashboard card. `body` is HTML (escape any outside data before passing it in)."""
    anchor_html = f'<span id="{escape(str(anchor))}"></span>' if anchor else ""
    kicker_html = f'<div class="card-kicker">{escape(str(kicker))}</div>' if kicker else ""
    return (f'{anchor_html}<div class="card"><div class="card-title-row"><div>'
            f'<div class="card-title">{escape(str(title))}</div>{kicker_html}</div>'
            f'<div class="card-menu">···</div></div>{body}</div>')


def detail_row(label, value_html):
    """One label/value line. `value_html` must already be escaped."""
    return (f'<div class="detail-row"><span class="detail-label">{escape(str(label))}</span>'
            f'<span class="detail-value">{value_html}</span></div>')


TAG_CLASSES = {"Public data": "", "Assumption": "tag-assumption", "From lookup": "tag-lookup",
               "Nesti's claim": "tag-nesti"}


def source_tag(label):
    return f'<span class="source-tag {TAG_CLASSES.get(label, "")}">{escape(str(label))}</span>'


def review_pill(text):
    t = (text or "").lower()
    if any(w in t for w in ("call back", "callback", "call-back", "return", "respond", "promised")):
        return "No call-back", "pill-orange"
    if any(w in t for w in ("answer", "phone", "ring", "cut off", "cutoff", "voicemail")):
        return "Unanswered call", "pill-pink"
    return "Hard to reach", "pill-blue"


def review_row(text, source_name, source_url):
    label, cls = review_pill(text)
    return (f'<div class="review"><div class="review-icon">☎</div><div>'
            f'<div class="review-text">"{escape(str(text))}"</div>'
            f'<div class="review-meta">{link(source_url, source_name or "Source")}</div></div>'
            f'<span class="pill {cls}">{label}</span></div>')


def bar_row(label, value, width):
    width = max(0.0, min(float(width or 0), 100.0))
    return (f'<div class="bar-row"><div class="bar-label">{escape(str(label))}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{width:.1f}%"></div></div>'
            f'<div class="bar-value">{escape(str(value))}</div></div>')


def donut(recovered_pct, recovered_text, lost_text):
    pct = max(0.0, min(float(recovered_pct or 0), 100.0))
    shown = f"{pct:.0f}"
    return (f'<div class="donut-wrap"><div class="donut" style="background: conic-gradient(var(--pink) {pct:.1f}%, #e9edf3 0)">'
            f'<div class="donut-centre"><div class="donut-big">{shown}%</div><div class="donut-small">recovered</div></div></div>'
            f'<div><div class="legend-row"><span class="legend-dot dot-pink"></span><span>Recovered &nbsp;<b>{escape(recovered_text)}</b></span></div>'
            f'<div class="legend-row"><span class="legend-dot dot-grey"></span><span>Still lost &nbsp;<b>{escape(lost_text)}</b></span></div></div></div>')


SIDEBAR = """
<div class="sidebar-brand">
  <div class="sidebar-brand-name">☎ Phone Gap</div>
  <div class="sidebar-brand-sub">A prototype by Zak for Nesti</div>
</div>
<div class="sidebar-section">Dashboard</div>
<a class="sidebar-link active" href="#overview"><span class="sidebar-icon">◫</span>Overview</a>
<a class="sidebar-link" href="#agency-profile"><span class="sidebar-icon">⌂</span>Agency profile</a>
<a class="sidebar-link" href="#ai-cover"><span class="sidebar-icon">✦</span>AI cover</a>
<a class="sidebar-link" href="#inputs"><span class="sidebar-icon">☷</span>Inputs</a>
<a class="sidebar-link" href="#workings"><span class="sidebar-icon">≡</span>Workings</a>
<a class="sidebar-link" href="#how-nesti-fits"><span class="sidebar-icon">◎</span>How Nesti fits</a>
<a class="sidebar-link" href="#sources"><span class="sidebar-icon">↗</span>Sources</a>
<div style="height:30px"></div>
<div class="sidebar-section">Prototype</div>
<div class="sidebar-note">Built by Zak · October 2026<br>Figures are estimates for discussion.</div>
"""

HEADER = """
<div id="overview"></div>
<div class="eyebrow">A prototype by Zak for Nesti</div>
<div class="dashboard-title">Phone Gap Calculator</div>
<div class="dashboard-subtitle">Type in any UK estate or letting agency. The calculator researches it online and estimates the fee income it loses each year to calls nobody answers out of hours. InStep AI rang 3,047 UK agencies between 6pm and 9pm: <b>94% went unanswered.</b><sup><a class="ref" href="#s1">1</a></sup></div>
"""

FIT = """
<div class="table-scroll"><table class="fit">
<thead><tr>
  <th>Can it…</th>
  <th class="us">Nesti<small>AI workforce</small></th>
  <th>Alto Lead Flow<small>CRM AI, powered by BridgeAI</small></th>
  <th>EstateAgents.ai<small>Outbound AI voice</small></th>
  <th>Answerphone<small>Voicemail box</small></th>
</tr></thead>
<tbody>
<tr><th>Answer phone calls</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Every call picked up in under a second, 24/7.<sup><a class="ref" href="#s8">8</a></sup></span></td>
  <td><span class="st st-ns">Not listed</span><span class="d">Alto lists portals, email, WhatsApp and web.<sup><a class="ref" href="#s4">4</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span><span class="d">Reported as outbound calling.<sup><a class="ref" href="#s11">11</a></sup></span></td>
  <td><span class="st st-part">Takes a message</span></td></tr>
<tr><th>Handle WhatsApp and portal enquiries</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Calls, WhatsApp, SMS, email, portal enquiries and web chat.<sup><a class="ref" href="#s8">8</a></sup></span></td>
  <td><span class="st st-yes">Yes</span><span class="d">"Every enquiry from portals, email, WhatsApp or web is answered instantly."<sup><a class="ref" href="#s4">4</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-no">No</span></td></tr>
<tr><th>Book viewings and valuations</th>
  <td class="us"><span class="st st-yes">Yes, both</span><span class="d">Into the right negotiator's diary, allowing for travel time.<sup><a class="ref" href="#s9">9</a></sup></span></td>
  <td><span class="st st-part">Viewings</span><span class="d">Books viewings into the Alto diary. Valuations not stated.<sup><a class="ref" href="#s4">4</a></sup></span></td>
  <td><span class="st st-part">Passes leads on</span><span class="d">Qualified contacts go to branch teams as valuation leads.<sup><a class="ref" href="#s11">11</a></sup></span></td>
  <td><span class="st st-no">No</span></td></tr>
<tr><th>Call old leads</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Makes outbound calls and brings back valuations that never converted.<sup><a class="ref" href="#s9">9</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-yes">Yes</span><span class="d">Calls former applicants, historic enquiries and dormant contacts.<sup><a class="ref" href="#s11">11</a></sup></span></td>
  <td><span class="st st-no">No</span></td></tr>
<tr><th>Handle tenants and maintenance</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Answers tenants and landlords, logs maintenance, instructs contractors.<sup><a class="ref" href="#s7">7</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-no">No</span></td></tr>
<tr><th>Work across several CRMs</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Alto, Reapit, Street, Rex, SME Professional, Acquaint and more.<sup><a class="ref" href="#s10">10</a></sup></span></td>
  <td><span class="st st-part">Alto</span><span class="d">Alto's own product, writing to the Alto diary.<sup><a class="ref" href="#s4">4</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-no">No</span></td></tr>
</tbody></table></div>
<div class="caveat">Filled only from public pages; "Not stated" means the page doesn't say. Some CRMs now answer calls themselves: Street lists an AI Call Handler that answers inbound calls 24/7.<sup><a class="ref" href="#s12">12</a></sup> This grid uses Alto Lead Flow as the CRM example. Nesti is listed in Alto's own integration marketplace.<sup><a class="ref" href="#s6">6</a></sup></div>
"""

ANSWER = """
<div class="answer-quote">Great, keep it for text.<br><em>Nesti answers the phone</em>, works your old leads and handles tenants, and logs everything back into your CRM.</div>
"""

NOTES = """
<ul class="note">
  <li>The 94% and 27% figures come from InStep AI, which sells voice AI. Its mystery calls covered weekday evenings, 6pm to 9pm. This calculator applies that rate to all out-of-hours calls, weekends included.<sup><a class="ref" href="#s1">1</a></sup></li>
  <li>27% is the share of leads on all channels that arrived out of hours for InStep's clients. It is used here as the share of calls. Other suppliers publish figures from 26% to 65%, and none is independent.<sup><a class="ref" href="#s2">2</a></sup></li>
  <li>Calls per month, valuation share, competitor rate and conversion rate are assumptions. Swap in the agency's own figures.</li>
  <li>The fee comes from local prices: 1.2% of the average house price for sales (the low end of typical sole-agency fees, 1.2% to 1.8% inc VAT)<sup><a class="ref" href="#s13">13</a></sup> and 12% of a year's rent for lettings (10% + VAT, the low end of fully managed fees)<sup><a class="ref" href="#s14">14</a></sup>. Agencies doing both get the average of the two.</li>
  <li>Agency details come from an AI web search of public pages. Check the linked sources before quoting them to anyone.</li>
  <li>Recovery with Nesti uses Nesti's own claim that 95%+ of enquiries are handled start to finish.<sup><a class="ref" href="#s7">7</a></sup></li>
  <li>Sanity check: Alto's own Lead Flow calculator estimates £40,000–£50,000+ a year recovered for a typical single-branch agency, using different assumptions.<sup><a class="ref" href="#s5">5</a></sup></li>
</ul>
"""

SOURCES = """
<ol class="src-list">
  <li id="s1"><a href="https://propertyindustryeye.com/agents-miss-94-of-evening-calls-study-finds/" target="_blank">Agents miss 94% of evening calls, study finds</a> · Property Industry Eye, 5 Aug 2026 (InStep AI study)</li>
  <li id="s2"><a href="https://thenegotiator.co.uk/news/products-services-news/how-many-property-enquiries-really-arrive-after-hours/" target="_blank">How many property enquiries really arrive after hours?</a> · The Negotiator, 27 Jul 2026</li>
  <li id="s3"><a href="https://www.altosoftware.co.uk/lead-flow/" target="_blank">Alto Lead Flow</a> · Alto product page</li>
  <li id="s4"><a href="https://support.altosoftware.co.uk/hc/en-gb/articles/5048172508575-Alto-Lead-Flow-powered-by-Bridge-AI" target="_blank">Alto Lead Flow (powered by Bridge AI)</a> · Alto Help Centre</li>
  <li id="s5"><a href="https://www.altosoftware.co.uk/wp-content/themes/alto/embed/lead-flow.html" target="_blank">Alto Lead Flow calculator</a> · Alto</li>
  <li id="s6"><a href="https://www.altosoftware.co.uk/integrations/nesti/" target="_blank">Nesti integration</a> · Alto integrations marketplace</li>
  <li id="s7"><a href="https://www.nesti.io/" target="_blank">Nesti homepage</a> · nesti.io</li>
  <li id="s8"><a href="https://www.nesti.io/workforce/ai-receptionist" target="_blank">AI Receptionist</a> · nesti.io</li>
  <li id="s9"><a href="https://www.nesti.io/workforce/ai-negotiator" target="_blank">AI Negotiator</a> · nesti.io</li>
  <li id="s10"><a href="https://www.nesti.io/integrations" target="_blank">Integrations</a> · nesti.io</li>
  <li id="s11"><a href="https://propertyindustryeye.com/estate-agency-leads-to-be-contacted-by-ai-voice-system/" target="_blank">Estate agency leads to be contacted by AI voice system</a> · Property Industry Eye, 7 May 2026 (EstateAgents.ai)</li>
  <li id="s12"><a href="https://street.co.uk/product/index/ai-call-handler" target="_blank">AI Call Handler</a> · Street</li>
  <li id="s13"><a href="https://hoa.org.uk/advice/guides-for-homeowners/i-am-selling/how-do-i-lower-my-estate-agent-fees-use-online-agents/" target="_blank">Estate agent fees and how you can save in 2026</a> · HomeOwners Alliance</li>
  <li id="s14"><a href="https://www.landlordvision.co.uk/blog/buy-to-let-management-costs/" target="_blank">Buy-to-let management costs</a> · LandlordVision, May 2026</li>
</ol>
"""

FOOTER = """
<div class="caveat" style="margin-top:28px">Phone Gap Calculator · a prototype by Zak · October 2026<br>
Not affiliated with or endorsed by Nesti, Alto or any agency or company named. Figures are estimates for discussion.</div>
"""
