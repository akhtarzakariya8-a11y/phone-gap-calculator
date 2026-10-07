"""Phone Gap Calculator: a prototype by Zak for Nesti.

Run locally:  streamlit run app.py
Needs ANTHROPIC_API_KEY in a .env file (local) or in the app's Secrets (Streamlit Cloud).

How the file is laid out:
  1. setup and helpers
  2. sidebar, header, search box and example buttons
  3. the lookup (research.py) when "Estimate" is clicked
  4. nothing else shows until an agency is loaded
  5. the dashboard: cards at the top, then inputs, workings, comparison grid and sources
"""

import datetime as dt
import json
import os
import time
from html import escape
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv

import content
from content import bar_row, card, detail_row, donut, link, review_row, safe_url, source_tag
from calc import (SCENARIOS, compute, inputs_from_profile, opener_line, profile_flags,
                  recovered, scenario_range)
from research import ResearchError, research_agency

load_dotenv()
st.set_page_config(page_title="Phone Gap Calculator", page_icon=":material/call:",
                   layout="wide", initial_sidebar_state="auto")
st.markdown(content.DASHBOARD_CSS, unsafe_allow_html=True)

DAILY_LOOKUP_LIMIT = 60          # protects the API key if the link is shared widely
CACHE_SECONDS = 24 * 60 * 60     # the same agency is only researched once a day
EXAMPLES_DIR = Path(__file__).parent / "examples"
COVER_TEXT = "Text-only AI (e.g. Alto Lead Flow)"
COVER_NESTI = "Calls and text (Nesti)"

# ---- Input fields: (key, label, widget settings, tag, source note) ----
FIELDS = [
    ("branches", "Branches", dict(min_value=1, max_value=500, step=1), "Assumption",
     "The agency's own number."),
    ("calls", "Inbound calls per branch per month", dict(min_value=0, max_value=20000, step=10), "Assumption",
     "Ask the agent, or check their phone system's call log."),
    ("ooh", "Share of calls out of hours (%)", dict(min_value=0, max_value=100, step=1), "Public data",
     'InStep AI client data: 27% of leads arrived outside office hours.<sup><a class="ref" href="#s1">1</a></sup> '
     'Supplier figures range from 26% to 65%.<sup><a class="ref" href="#s2">2</a></sup>'),
    ("unans", "Out-of-hours calls unanswered (%)", dict(min_value=0, max_value=100, step=1), "Public data",
     "InStep AI rang 3,047 UK agency numbers, 6pm–9pm weekdays, May–Jul 2026: 94.1% unanswered. "
     'InStep sells voice AI.<sup><a class="ref" href="#s1">1</a></sup>'),
    ("val", "Calls that are valuation enquiries (%)", dict(min_value=0, max_value=100, step=1), "Assumption",
     "Vendors and landlords wanting a sales or lettings valuation."),
    ("comp", "Missed vendors who go to a competitor (%)", dict(min_value=0, max_value=100, step=1), "Assumption",
     "Share who book another agent instead of calling back."),
    ("conv", "Valuation-to-instruction rate (%)", dict(min_value=0, max_value=100, step=1), "Assumption",
     "Share of valuations that become instructions."),
    ("fee", "Average fee per instruction (£)", dict(min_value=0, max_value=200000, step=50), "Assumption",
     "A blend of sales and lettings fees. Use the agency's own average."),
    ("rec", "Share of the phone loss Nesti recovers (%)", dict(min_value=0, max_value=100, step=1), "Nesti's claim",
     'Nesti\'s own claim: "95%+ handled start to finish".<sup><a class="ref" href="#s7">7</a></sup> '
     'Used only when "Calls and text" is selected.'),
]


# ---------------- helpers ----------------
def esc(x) -> str:
    return escape(str(x)) if x is not None else ""


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
    """Load an agency (or nothing) into the inputs."""
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


# ---------------- sidebar, header, search ----------------
with st.sidebar:
    st.markdown(content.SIDEBAR, unsafe_allow_html=True)

st.markdown(content.HEADER, unsafe_allow_html=True)

with st.form("lookup"):
    c1, c2, c3 = st.columns([2.2, 1.7, 0.8], vertical_alignment="bottom")
    agency = c1.text_input("Estate or letting agency", placeholder="e.g. Keatons")
    hint = c2.text_input("Town or website (optional)", placeholder="e.g. Bow, east London")
    submitted = c3.form_submit_button("Estimate", type="primary", width="stretch")

examples = load_examples()
if examples:
    st.caption("Or load an example researched on 7 Oct 2026 (instant, no lookup needed):")
    cols = st.columns(len(examples) + 1)
    for col, label in zip(cols, examples):
        col.button(label, on_click=load_example, args=(label,), width="stretch")
    if st.session_state.profile:
        cols[-1].button("Clear agency", on_click=clear_agency, width="stretch")

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
                         "Try one of the examples instead.")
            elif store["count"] >= DAILY_LOOKUP_LIMIT:
                st.error("Today's lookup limit has been reached. Try again tomorrow, or load an example.")
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

profile = st.session_state.profile
if not profile:
    # Nothing below the search until an agency has been looked up or an example loaded.
    st.markdown(content.FOOTER, unsafe_allow_html=True)
    st.stop()

top = st.container()  # the dashboard cards; filled in once the inputs below have been read


# ---------------- inputs ----------------
st.markdown('<span id="inputs"></span>', unsafe_allow_html=True)
with st.container(border=True):
    st.markdown('<div class="card-title-row"><div><div class="card-title">Inputs</div>'
                '<div class="card-kicker">Every number is editable. Each one is labelled with where it comes from.</div>'
                '</div><div class="card-menu">···</div></div>', unsafe_allow_html=True)
    b1, b2, b3, _ = st.columns([1, 1, 1.2, 3])
    b1.button("Central", on_click=set_scenario, args=("central",), width="stretch",
              help="27% of calls out of hours, 50% of missed vendors go elsewhere")
    b2.button("Low", on_click=set_scenario, args=("low",), width="stretch",
              help="20% of calls out of hours, 30% of missed vendors go elsewhere")
    b3.button("Reset inputs", on_click=reset_inputs, width="stretch")

    found = st.session_state.found
    v = {}
    for key, label, opts, tag, note in FIELDS:
        c1, c2, c3 = st.columns([2.6, 1.1, 0.8], vertical_alignment="center")
        if key in found:
            tag, note = "From lookup", esc(found[key])
        with c1:
            st.markdown(f'<div class="input-label">{esc(label)}</div><div class="input-note">{note}</div>',
                        unsafe_allow_html=True)
        with c2:
            v[key] = st.number_input(label, key=f"in_{key}", label_visibility="collapsed", **opts)
        with c3:
            st.markdown(source_tag(tag), unsafe_allow_html=True)


# ---------------- the numbers ----------------
r = compute(v)
lo, hi = scenario_range(v)
agency_name = profile.get("agency_name") or "This agency"


# ---------------- dashboard cards (shown above the inputs) ----------------
with top:
    # Row 1: fee income + agency profile
    left, right = st.columns([1.12, 0.88], gap="medium")
    with left:
        inst_year = r["inst_lost"] * 12
        body = (
            f'<div class="money">{gbp(r["year"])}</div>'
            f'<div class="money-period">a year · <b>{gbp(r["month"])}</b> a month · '
            f'<b>{num(inst_year, 1 if inst_year < 10 else 0)}</b> instructions lost a year</div>'
            f'<div class="range-box">Low to central range: <b>{gbp_k(lo)}–{gbp_k(hi)} a year</b></div>'
            f'<div class="metric-grid">'
            f'<div class="mini-metric"><div class="mini-value">{num(r["missed"], 0)}</div><div class="mini-label">calls missed a month</div></div>'
            f'<div class="mini-metric"><div class="mini-value">{num(r["val_missed"], 1)}</div><div class="mini-label">valuation enquiries missed a month</div></div>'
            f'<div class="mini-metric"><div class="mini-value">{num(r["waiting"], 0)}</div><div class="mini-label">buyers and tenants left waiting a month</div></div>'
            f'</div><div class="caveat">Estimate from public data, the agency lookup and labelled assumptions. '
            f'See the workings below.</div>')
        st.markdown(card("Fee income at risk from unanswered out-of-hours calls", body, kicker=agency_name),
                    unsafe_allow_html=True)

    with right:
        services = {"sales": "Sales", "lettings": "Lettings", "both": "Sales and lettings"}.get(
            profile.get("services"), "Not found")
        branches = [b for b in (profile.get("branches") or []) if isinstance(b, str)]
        bcount = profile.get("branch_count") or (len(branches) if branches else None)
        branch_val = esc(bcount) if bcount else "Not found"
        if branches:
            branch_val += f"<small>{esc(', '.join(branches[:8]))}{'…' if len(branches) > 8 else ''}</small>"

        hours = profile.get("opening_hours") if isinstance(profile.get("opening_hours"), dict) else {}
        def hour_line(lbl, val):  # don't write "Mon–Fri Mon-Thu …" when the days are already there
            text = str(val)
            has_days = any(d in text for d in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"))
            return esc(text) if has_days else f"{lbl} {esc(text)}"

        hour_parts = [hour_line(lbl, hours.get(k)) for lbl, k in
                      (("Mon–Fri", "weekdays"), ("Sat", "saturday"), ("Sun", "sunday")) if hours.get(k)]
        hours_val = "<br>".join(hour_parts) if hour_parts else "Not found"
        if safe_url(profile.get("opening_hours_source")):
            hours_val += f"<small>{link(profile['opening_hours_source'], 'source')}</small>"

        cover = profile.get("out_of_hours_phone_cover") or {}
        cover_val = {"yes": "Yes", "maintenance_only": "Tenant emergencies only"}.get(cover.get("status"), "None found")
        if cover.get("status") == "yes" and cover.get("detail"):
            cover_val += f"<small>{esc(cover['detail'])}</small>"

        def yes_no(x):
            return {True: "Yes", False: "No"}.get(x, "Not checked")

        def price_val(p, suffix=""):
            if not isinstance(p, dict) or not p.get("value"):
                return "Not found"
            try:
                out = f"£{float(p['value']):,.0f}{suffix}"
            except (TypeError, ValueError):
                return "Not found"
            detail = ", ".join(esc(x) for x in (p.get("measure"), p.get("area")) if x)
            return out + f"<small>{detail} · {link(p.get('source_url'), p.get('source_name') or 'source')}</small>"

        website = profile.get("website")
        site_val = (link(website, urlparse(website).netloc.removeprefix("www.") or website)
                    if safe_url(website) else "Not found")
        rows = [
            ("Website", site_val),
            ("Services", services),
            ("Branches", branch_val),
            ("Opening hours", hours_val),
            ("Out-of-hours phone cover", cover_val),
            ("WhatsApp", yes_no(profile.get("whatsapp"))),
            ("Live chat", yes_no(profile.get("live_chat"))),
            ("Average house price", price_val(profile.get("avg_property_price"))),
            ("Average rent", price_val(profile.get("avg_monthly_rent"), " a month")),
        ]
        if profile.get("crm"):
            rows.insert(5, ("CRM (if visible)", esc(profile["crm"])))
        flags = "".join(f'<div class="flag flag-{f["kind"]}">{esc(f["text"])}</div>' for f in profile_flags(profile))
        match = f'<div class="match-note">{esc(profile.get("match_note"))}</div>' if profile.get("match_note") else ""
        researched = profile.get("_researched")
        body = match + "".join(detail_row(lbl, val) for lbl, val in rows) + flags
        st.markdown(card("Agency profile", body, kicker=f"Researched {researched}" if researched else "From public research",
                         anchor="agency-profile"), unsafe_allow_html=True)

    # Row 2: reviews + leakage bars
    reviews_col, leakage_col = st.columns([1.12, 0.88], gap="medium")
    with reviews_col:
        reviews = [x for x in (profile.get("review_evidence") or []) if isinstance(x, dict) and x.get("quote")]
        if reviews:
            body = "".join(review_row(x["quote"], x.get("site"), x.get("url")) for x in reviews[:3])
            body += '<div class="caveat">Found by AI search. Open each link to check the wording before quoting it.</div>'
        else:
            body = '<div class="empty-state">No public reviews about unanswered calls turned up in this lookup.</div>'
        st.markdown(card("What reviewers say about getting through", body,
                         kicker="Public reviews found in the lookup"), unsafe_allow_html=True)

    with leakage_col:
        vals = [("Calls missed", r["missed"] * 12), ("Valuation enquiries missed", r["val_missed"] * 12),
                ("Buyers and tenants waiting", r["waiting"] * 12)]
        top_val = max(max(x for _, x in vals), 1)
        body = "".join(bar_row(lbl, num(x, 0), x / top_val * 100) for lbl, x in vals)
        body += '<div class="caveat">Out-of-hours calls a year, from the inputs below.</div>'
        st.markdown(card("Opportunity leakage", body, kicker="Each year"), unsafe_allow_html=True)

    # Row 3: AI cover + donut
    st.markdown('<span id="ai-cover"></span>', unsafe_allow_html=True)
    cover_col, donut_col = st.columns([1.12, 0.88], gap="medium")
    with cover_col:
        with st.container(border=True):
            st.markdown('<div class="card-title-row"><div><div class="card-title">AI cover</div>'
                        '<div class="card-kicker">How much of the phone gap comes back with each type of cover</div>'
                        '</div><div class="card-menu">···</div></div>', unsafe_allow_html=True)
            cover_choice = st.segmented_control("AI cover", [COVER_TEXT, COVER_NESTI], default=COVER_TEXT,
                                                key="cover", label_visibility="collapsed")
            cover_kind = "nesti" if cover_choice == COVER_NESTI else "text"
            rec = recovered(r["year"], cover_kind, v["rec"])
            note = ('Alto lists portals, email, WhatsApp and web for Lead Flow, not phone calls.'
                    '<sup><a class="ref" href="#s4">4</a></sup> A caller who rings at 7pm still gets no answer, '
                    'so none of the phone loss comes back.' if cover_kind == "text" else
                    "Nesti answers calls 24/7 as well as messages. Recovery uses Nesti's own \"95%+ handled start "
                    'to finish" figure, which you can change in the inputs.<sup><a class="ref" href="#s7">7</a></sup>')
            st.markdown(f'<div class="money" style="font-size:34px;color:#0f8a5a">{gbp(rec)}</div>'
                        f'<div class="money-period">recovered a year · <b>{gbp(r["year"] - rec)}</b> still lost</div>'
                        f'<div class="caveat" style="font-size:12px">{note}</div>', unsafe_allow_html=True)
    with donut_col:
        share = rec / r["year"] * 100 if r["year"] else 0
        st.markdown(card("Recovered vs still lost", donut(share, gbp(rec), gbp(r["year"] - rec)),
                         kicker=cover_choice or COVER_TEXT), unsafe_allow_html=True)

    # Sales opener
    with st.container(border=True):
        st.markdown('<div class="card-title-row"><div><div class="card-title">Opening line for a call or email</div>'
                    '<div class="card-kicker">Built only from what the lookup found. Use the copy button.</div>'
                    '</div><div class="card-menu">···</div></div>', unsafe_allow_html=True)
        st.code(opener_line(profile, r["year"], int(v["branches"])), language=None, wrap_lines=True)


# ---------------- workings ----------------
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
    ("E", "Fee income at risk", f"D {num(r['inst_lost'], 2)} × {gbp(v['fee'])} fee", gbp(r["month"]), gbp(r["year"]), "money-row"),
    ("F", "Buyers and tenants left waiting", f"B {num(r['missed'], 1)} − C {num(r['val_missed'], 1)} (not counted in £)",
     num(r["waiting"], 1), num(r["waiting"] * 12, 0), "soft"),
    ("G", "Recovered with Nesti" if cover_kind == "nesti" else "Recovered with text-only AI",
     f"E × {pc(v['rec'])} (Nesti's claim)" if cover_kind == "nesti" else "E × 0% (no calls answered)",
     gbp(rec / 12), gbp(rec), "recov"),
]
rows_html = "".join(
    f'<tr class="{cls}"><td class="ref">{a}</td><td>{esc(item)}</td><td class="w">{esc(w)}</td>'
    f'<td class="r">{m}</td><td class="r">{y}</td></tr>' for a, item, w, m, y, cls in sheet)
workings = (
    '<div class="table-scroll"><table class="sheet"><thead><tr><th class="ref">Ref</th><th>Item</th><th>Working</th>'
    f'<th class="r">Per month</th><th class="r">Per year</th></tr></thead><tbody>{rows_html}</tbody></table></div>'
    '<div class="caveat">Each line uses the one above it. Workings show rounded figures; results use unrounded values, '
    "so a line can differ from its working by a few pounds. Only phone calls are counted; WhatsApp, email and "
    "portal leads are left out.</div>")
st.markdown(card("Workings", workings, kicker="Line-by-line calculation", anchor="workings"), unsafe_allow_html=True)


# ---------------- how Nesti fits ----------------
st.markdown(card("How Nesti fits alongside CRM AI", content.FIT, kicker="Filled only from public pages",
                 anchor="how-nesti-fits"), unsafe_allow_html=True)
st.markdown(card('When an agent says "my CRM already does AI"', content.ANSWER), unsafe_allow_html=True)


# ---------------- sources ----------------
agency_sources = [s for s in (profile.get("sources") or []) if isinstance(s, dict) and safe_url(s.get("url"))]
src_left, src_right = st.columns([1, 1], gap="medium")
with src_left:
    st.markdown(card("Where the numbers come from", content.NOTES, anchor="sources"), unsafe_allow_html=True)
    if agency_sources:
        body = '<ol class="src-list">' + "".join(
            f"<li>{link(s['url'], s.get('label') or s['url'])}</li>" for s in agency_sources) + "</ol>"
        st.markdown(card(f"Sources for {agency_name}", body, kicker="Pages the lookup used"), unsafe_allow_html=True)
with src_right:
    st.markdown(card("Sources", content.SOURCES, kicker="Numbered references used on this page"), unsafe_allow_html=True)

st.markdown(content.FOOTER, unsafe_allow_html=True)
