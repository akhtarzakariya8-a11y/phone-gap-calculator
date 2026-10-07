"""Phone Gap Calculator: a prototype by Zak for Nesti.

Run locally:  streamlit run app.py
Needs ANTHROPIC_API_KEY in a .env file (local) or in the app's Secrets (Streamlit Cloud).
"""

import datetime as dt
import html
import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv

import content
from calc import (DEFAULTS, SCENARIOS, compute, inputs_from_profile, opener_line,
                  profile_flags, recovered, scenario_range)
from research import ResearchError, research_agency

load_dotenv()
st.set_page_config(page_title="Phone Gap Calculator", page_icon=":material/call:", layout="centered")
st.markdown(f"<style>{content.CSS}</style>", unsafe_allow_html=True)

DAILY_LOOKUP_LIMIT = 60          # protects the API key if the link is shared widely
CACHE_SECONDS = 24 * 60 * 60     # the same agency is only researched once a day
EXAMPLES_DIR = Path(__file__).parent / "examples"
COVER_TEXT = "Text-only AI (e.g. Alto Lead Flow)"
COVER_NESTI = "Calls and text (Nesti)"

# ---- Input fields: (group, key, label, widget settings, tag, source note) ----
FIELDS = [
    ("The agency", "branches", "Branches", dict(min_value=1, max_value=500, step=1), "assume",
     "The agency's own number."),
    (None, "calls", "Inbound calls per branch per month", dict(min_value=0, max_value=20000, step=10), "assume",
     "Ask the agent, or check their phone system's call log."),
    ("Out-of-hours calls", "ooh", "Share of calls out of hours (%)", dict(min_value=0, max_value=100, step=1), "data",
     'InStep AI client data: 27% of leads arrived outside office hours.<sup><a class="ref" href="#s1">1</a></sup> '
     'Supplier figures range from 26% to 65%.<sup><a class="ref" href="#s2">2</a></sup>'),
    (None, "unans", "Out-of-hours calls unanswered (%)", dict(min_value=0, max_value=100, step=1), "data",
     'InStep AI rang 3,047 UK agency numbers, 6pm–9pm weekdays, May–Jul 2026: 94.1% unanswered. '
     'InStep sells voice AI.<sup><a class="ref" href="#s1">1</a></sup>'),
    ("Turning calls into fees", "val", "Calls that are valuation enquiries (%)", dict(min_value=0, max_value=100, step=1),
     "assume", "Vendors and landlords wanting a sales or lettings valuation."),
    (None, "comp", "Missed vendors who go to a competitor (%)", dict(min_value=0, max_value=100, step=1), "assume",
     "Share who book another agent instead of calling back."),
    (None, "conv", "Valuation-to-instruction rate (%)", dict(min_value=0, max_value=100, step=1), "assume",
     "Share of valuations that become instructions."),
    (None, "fee", "Average fee per instruction (£)", dict(min_value=0, max_value=200000, step=50), "assume",
     "A blend of sales and lettings fees. Use the agency's own average."),
    ("AI cover", "rec", "Share of the phone loss Nesti recovers (%)", dict(min_value=0, max_value=100, step=1), "claim",
     'Nesti\'s own claim: "95%+ handled start to finish".<sup><a class="ref" href="#s7">7</a></sup> '
     'Used only when "Calls and text" is selected.'),
]
TAGS = {"data": ("tag-data", "Public data"), "assume": ("tag-assume", "Assumption"),
        "claim": ("tag-claim", "Nesti's claim"), "found": ("tag-found", "From lookup")}


# ---------------- helpers ----------------
def esc(x) -> str:
    return html.escape(str(x)) if x is not None else ""


def safe_url(u):
    return u if isinstance(u, str) and u.startswith(("https://", "http://")) else None


def link(url, text) -> str:
    u = safe_url(url)
    return f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(text)}</a>' if u else esc(text)


def gbp(n: float) -> str:
    return f"£{round(n):,}"


def gbp_k(n: float) -> str:
    return f"£{round(n / 1000):,}k" if n >= 1000 else gbp(n)


def num(n: float, dp: int = 1) -> str:
    s = f"{n:,.{dp}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def get_api_key():
    try:
        key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        key = None
    return key or os.getenv("ANTHROPIC_API_KEY")


@st.cache_resource
def lookup_store():
    """Shared across everyone using the app: a day's cache and a daily counter."""
    return {"cache": {}, "day": "", "count": 0}


@st.cache_data
def load_examples() -> dict:
    out = {}
    for f in sorted(EXAMPLES_DIR.glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        out[p.get("_label") or p.get("agency_name") or f.stem] = p
    return out


# ---------------- state ----------------
def apply_profile(profile):
    """Load an agency (or the generic defaults) into the inputs."""
    base = inputs_from_profile(profile)
    st.session_state.profile = profile
    st.session_state.base = base["values"]
    st.session_state.found = base["found"]
    for k, v in base["values"].items():
        st.session_state[f"in_{k}"] = v


if "base" not in st.session_state:
    apply_profile(None)


def set_scenario(name):
    for k, v in SCENARIOS[name].items():
        st.session_state[f"in_{k}"] = v


def reset_inputs():
    for k, v in st.session_state.base.items():
        st.session_state[f"in_{k}"] = v


def clear_agency():
    apply_profile(None)


def load_example(label):
    apply_profile(load_examples()[label])


# ---------------- header + search ----------------
st.markdown(content.HEADER, unsafe_allow_html=True)
st.write("")

with st.form("lookup", border=True):
    c1, c2 = st.columns([3, 2])
    agency = c1.text_input("Estate or letting agency", placeholder="e.g. Keatons")
    hint = c2.text_input("Town or website (optional)", placeholder="e.g. Bow, east London")
    submitted = st.form_submit_button("Estimate for this agency", type="primary")

examples = load_examples()
if examples:
    st.caption("Or load an example researched on 7 Oct 2026 (instant, no lookup needed):")
    cols = st.columns(len(examples))
    for col, label in zip(cols, examples):
        col.button(label, on_click=load_example, args=(label,), width="stretch")
    if st.session_state.profile:
        st.button("Clear agency", on_click=clear_agency)

if submitted:
    name, place = agency.strip(), hint.strip()
    if not name:
        st.warning("Type an agency name first.")
    else:
        store = lookup_store()
        key = f"{name.lower()}|{place.lower()}"
        cached = store["cache"].get(key)
        profile = None
        if cached and time.time() - cached["t"] < CACHE_SECONDS:
            profile = cached["profile"]
        else:
            today = dt.date.today().isoformat()
            if store["day"] != today:
                store["day"], store["count"] = today, 0
            api_key = get_api_key()
            if not api_key:
                st.error("No Anthropic API key is set up for this app, so it can't look agencies up. "
                         "The calculator below still works with your own numbers.")
            elif store["count"] >= DAILY_LOOKUP_LIMIT:
                st.error("Today's lookup limit has been reached. Try again tomorrow, or enter the numbers below by hand.")
            else:
                store["count"] += 1
                with st.status(f"Researching {name}… (usually 15–30 seconds)", expanded=True) as status:
                    try:
                        profile = research_agency(name, place, api_key=api_key, on_progress=status.write)
                        status.update(label=f"Researched {profile.get('agency_name') or name}",
                                      state="complete", expanded=False)
                    except ResearchError as exc:
                        status.update(label="The lookup didn't finish", state="error", expanded=False)
                        st.error(str(exc))
                if profile and profile.get("found"):
                    profile["_researched"] = dt.date.today().strftime("%-d %b %Y")
                    store["cache"][key] = {"t": time.time(), "profile": profile}
        if profile and profile.get("found"):
            apply_profile(profile)
        elif profile is not None:
            st.warning(f"Couldn't identify an agency called \"{name}\". Try adding the town or the website address.")


# ---------------- agency profile ----------------
profile = st.session_state.profile


def hours_text(h: dict) -> str:
    if not isinstance(h, dict):
        return "Not found"
    parts = [(lbl, h.get(k)) for lbl, k in (("Mon–Fri", "weekdays"), ("Sat", "saturday"), ("Sun", "sunday"))]
    shown = [f"{lbl} {esc(v)}" for lbl, v in parts if v]
    return " · ".join(shown) if shown else "Not found"


def yes_no(v) -> str:
    return {True: "Yes", False: "No"}.get(v, "Not checked")


if profile:
    services = {"sales": "Sales", "lettings": "Lettings", "both": "Sales and lettings"}.get(profile.get("services"), "Not found")
    branches = [b for b in (profile.get("branches") or []) if isinstance(b, str)]
    bcount = profile.get("branch_count") or (len(branches) if branches else None)
    branch_txt = (f"{esc(bcount)}" + (f": {esc(', '.join(branches[:8]))}" if branches else "")) if bcount else "Not found"
    cover = profile.get("out_of_hours_phone_cover") or {}
    cover_txt = {"yes": "Yes" + (f": {esc(cover.get('detail'))}" if cover.get("detail") else ""),
                 "maintenance_only": "Tenant emergencies only"}.get(cover.get("status"), "None found")
    if cover.get("source"):
        cover_txt += f" ({link(cover['source'], 'source')})"
    hrs = hours_text(profile.get("opening_hours"))
    if profile.get("opening_hours_source"):
        hrs += f" ({link(profile['opening_hours_source'], 'source')})"

    def price_txt(p, suffix=""):
        if not isinstance(p, dict) or not p.get("value"):
            return "Not found"
        try:
            v = f"£{float(p['value']):,.0f}{suffix}"
        except (TypeError, ValueError):
            return "Not found"
        detail = ", ".join(esc(x) for x in (p.get("measure"), p.get("area")) if x)
        src = link(p.get("source_url"), p.get("source_name") or "source")
        return f"{v} <span style='color:var(--muted)'>({detail}; {src})</span>"

    rows = [
        ("Website", link(profile.get("website"), urlparse(str(profile.get("website"))).netloc.removeprefix("www.")
                         or profile.get("website")) if safe_url(profile.get("website")) else "Not found"),
        ("Services", services),
        ("Branches", branch_txt),
        ("Opening hours", hrs),
        ("Out-of-hours phone cover", cover_txt),
        ("WhatsApp / live chat", f"WhatsApp: {yes_no(profile.get('whatsapp'))} · Live chat: {yes_no(profile.get('live_chat'))}"),
        ("Local average price", price_txt(profile.get("avg_property_price"))),
        ("Local average rent", price_txt(profile.get("avg_monthly_rent"), " a month")),
    ]
    if profile.get("crm"):
        rows.insert(5, ("CRM (if visible)", esc(profile["crm"])))
    facts = "".join(f"<dt>{lbl}</dt><dd>{val}</dd>" for lbl, val in rows)
    flags = "".join(f'<div class="pg-flag {f["kind"]}">{esc(f["text"])}</div>' for f in profile_flags(profile))
    reviews = [r for r in (profile.get("review_evidence") or []) if isinstance(r, dict) and r.get("quote")]
    review_html = ""
    if reviews:
        quotes = "".join(f'<div class="pg-quote">"{esc(r["quote"])}"<span>{link(r.get("url"), r.get("site") or "source")}</span></div>'
                         for r in reviews[:3])
        review_html = (f'<p class="pg-eyebrow" style="margin-top:16px">What reviewers say about getting through</p>{quotes}'
                       '<p class="pg-note" style="margin-top:4px">Found by AI search. Open each link to check the wording before quoting it.</p>')
    researched = esc(profile.get("_researched") or "")
    st.markdown(
        f'<div class="pg-card pg-agency"><p class="pg-eyebrow">Agency profile{" · researched " + researched if researched else ""}</p>'
        f'<h3>{esc(profile.get("agency_name"))}</h3>'
        f'<p class="match">{esc(profile.get("match_note") or "")}</p>'
        f'<dl class="pg-facts">{facts}</dl>{flags}{review_html}</div>',
        unsafe_allow_html=True,
    )
    srcs = [s for s in (profile.get("sources") or []) if isinstance(s, dict) and safe_url(s.get("url"))]
    if srcs:
        with st.expander(f"Sources for this agency ({len(srcs)})"):
            st.markdown("<ul class='pg-notes'>" + "".join(f"<li>{link(s['url'], s.get('label') or s['url'])}</li>" for s in srcs)
                        + "</ul>", unsafe_allow_html=True)

else:
    # Nothing below the search until an agency has been looked up or an example loaded.
    st.markdown(content.FOOTER, unsafe_allow_html=True)
    st.stop()

results = st.container()

# ---------------- inputs ----------------
st.markdown("### Every number is editable")
b1, b2, b3, _ = st.columns([1, 1, 1.2, 2])
b1.button("Central", on_click=set_scenario, args=("central",), width="stretch",
          help="27% of calls out of hours, 50% of missed vendors go elsewhere")
b2.button("Low", on_click=set_scenario, args=("low",), width="stretch",
          help="20% of calls out of hours, 30% of missed vendors go elsewhere")
b3.button("Reset inputs", on_click=reset_inputs, width="stretch")
st.caption("Central uses 27% of calls out of hours and 50% of missed vendors going elsewhere. Low uses 20% and 30%.")

found = st.session_state.found
v = {}
left, right = None, None
for i, (group, key, label, opts, tag, note) in enumerate(FIELDS):
    if group:
        st.markdown(f'<div class="pg-group">{group}</div>', unsafe_allow_html=True)
        left, right = st.columns(2)
        col_index = 0
    col = left if col_index % 2 == 0 else right
    col_index += 1
    with col:
        v[key] = st.number_input(label, key=f"in_{key}", **opts)
        if key in found:
            cls, txt = TAGS["found"]
            src = esc(found[key])
        else:
            cls, txt = TAGS[tag]
            src = note
        st.markdown(f'<p class="pg-src"><span class="tag {cls}">{txt}</span>{src}</p>', unsafe_allow_html=True)

# ---------------- results (rendered above the inputs) ----------------
r = compute(v)
lo, hi = scenario_range(v)
with results:
    label = f"Fee income at risk from unanswered out-of-hours calls for {esc(profile.get('agency_name'))}"
    inst_year = r["inst_lost"] * 12
    st.markdown(
        f'<div class="pg-card"><p class="pg-k">{label}</p>'
        f'<div class="pg-big">{gbp(r["year"])}<small>a year</small></div>'
        f'<p class="pg-sub"><b>{gbp(r["month"])}</b> a month · <b>{num(inst_year, 1 if inst_year < 10 else 0)}</b> instructions lost a year</p>'
        f'<div class="pg-range">Low to central range for this agency: <b>{gbp_k(lo)}–{gbp_k(hi)} a year</b></div>'
        f'<div class="pg-stats" style="margin-top:16px">'
        f'<div class="pg-stat"><p class="n">{num(r["missed"], 0)}</p><p class="k">calls missed a month</p></div>'
        f'<div class="pg-stat"><p class="n">{num(r["val_missed"], 1)}</p><p class="k">valuation enquiries missed a month</p></div>'
        f'<div class="pg-stat"><p class="n">{num(r["waiting"], 0)}</p><p class="k">buyers and tenants left waiting a month</p></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    cover_choice = st.segmented_control("What comes back with AI cover", [COVER_TEXT, COVER_NESTI],
                                        default=COVER_TEXT, key="cover")
    cover = "nesti" if cover_choice == COVER_NESTI else "text"
    rec = recovered(r["year"], cover, v["rec"])
    share = (rec / r["year"] * 100) if r["year"] else 0
    note = ('Alto lists portals, email, WhatsApp and web for Lead Flow, not phone calls.<sup><a class="ref" href="#s4">4</a></sup> '
            "A caller who rings at 7pm still gets no answer, so none of the phone loss comes back."
            if cover == "text" else
            "Nesti answers calls 24/7 as well as messages. Recovery uses Nesti's own \"95%+ handled start to finish\" "
            'figure, which you can change below.<sup><a class="ref" href="#s7">7</a></sup>')
    st.markdown(
        f'<div class="pg-card"><div class="pg-bar"><div class="rec" style="width:{share:.1f}%"></div></div>'
        f'<div class="pg-split"><div><p class="pg-k">Recovered a year</p><p class="pg-v win">{gbp(rec)}</p></div>'
        f'<div><p class="pg-k">Still lost a year</p><p class="pg-v loss">{gbp(r["year"] - rec)}</p></div></div>'
        f'<p class="pg-note">{note}</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<p class="pg-eyebrow" style="margin-top:6px">Opening line for a call or email</p>', unsafe_allow_html=True)
    st.code(opener_line(profile, r["year"], int(v["branches"])), language=None, wrap_lines=True)

# ---------------- workings ----------------
st.markdown("### The workings")
st.caption("Each line uses the one above it. Change any input and the sheet updates.")


def pc(x):
    return f"{num(x, 1)}%"


b = int(v["branches"])
sheet = [
    ("A", "Out-of-hours calls", f"{b} branch{'' if b == 1 else 'es'} × {num(v['calls'], 0)} calls × {pc(v['ooh'])}",
     num(r["ooh_calls"], 1), num(r["ooh_calls"] * 12, 0), ""),
    ("B", "Missed calls", f"A {num(r['ooh_calls'], 1)} × {pc(v['unans'])} unanswered",
     num(r["missed"], 1), num(r["missed"] * 12, 0), ""),
    ("C", "Missed valuation enquiries", f"B {num(r['missed'], 1)} × {pc(v['val'])}",
     num(r["val_missed"], 1), num(r["val_missed"] * 12, 0), ""),
    ("D", "Instructions lost", f"C {num(r['val_missed'], 1)} × {pc(v['comp'])} to a competitor × {pc(v['conv'])} instructed",
     num(r["inst_lost"], 2), num(r["inst_lost"] * 12, 1), ""),
    ("E", "Fee income at risk", f"D {num(r['inst_lost'], 2)} × {gbp(v['fee'])} fee", gbp(r["month"]), gbp(r["year"]), "money"),
    ("F", "Buyers and tenants left waiting", f"B {num(r['missed'], 1)} − C {num(r['val_missed'], 1)} (not counted in £)",
     num(r["waiting"], 1), num(r["waiting"] * 12, 0), "soft"),
    ("G", "Recovered with Nesti" if cover == "nesti" else "Recovered with text-only AI",
     f"E × {pc(v['rec'])} (Nesti's claim)" if cover == "nesti" else "E × 0% (no calls answered)",
     gbp(rec / 12), gbp(rec), "recov"),
]
rows_html = "".join(
    f'<tr class="{cls}"><td class="ref">{a}</td><td>{esc(item)}</td><td class="w">{esc(w)}</td>'
    f'<td class="r">{m}</td><td class="r">{y}</td></tr>' for a, item, w, m, y, cls in sheet)
st.markdown(
    '<div class="pg-scroll"><table class="sheet"><thead><tr><th class="ref">Ref</th><th>Item</th><th>Working</th>'
    f'<th class="r">Per month</th><th class="r">Per year</th></tr></thead><tbody>{rows_html}</tbody></table></div>'
    '<p class="pg-foot">Workings show rounded figures; results use unrounded values, so a line can differ from its '
    "working by a few pounds. Only phone calls are counted; WhatsApp, email and portal leads are left out.</p>",
    unsafe_allow_html=True,
)

# ---------------- how Nesti fits ----------------
st.markdown("### How Nesti fits alongside CRM AI")
st.markdown(content.FIT, unsafe_allow_html=True)
st.markdown(content.ANSWER, unsafe_allow_html=True)

# ---------------- sources ----------------
st.markdown("### Where the numbers come from")
st.markdown(content.NOTES, unsafe_allow_html=True)
st.markdown(content.SOURCES, unsafe_allow_html=True)
st.markdown(content.FOOTER, unsafe_allow_html=True)
