"""The maths. No Streamlit here, so every number can be tested on its own."""

import re

# ---- Default inputs (the generic, no-agency version) ----
DEFAULTS = {
    "branches": 1,      # agency's number
    "calls": 300,       # inbound calls per branch per month (assumption)
    "ooh": 27,          # % of calls out of hours (InStep AI client data)
    "unans": 94,        # % of out-of-hours calls unanswered (InStep AI mystery calls)
    "val": 10,          # % of calls that are valuation enquiries (assumption)
    "comp": 50,         # % of missed vendors who go to a competitor (assumption)
    "conv": 35,         # % valuation-to-instruction rate (assumption)
    "fee": 3000,        # £ average fee per instruction (assumption)
    "rec": 95,          # % of phone loss Nesti recovers (Nesti's own claim)
}

SCENARIOS = {
    "central": {"ooh": 27, "comp": 50},
    "low": {"ooh": 20, "comp": 30},
}

# ---- Fee assumptions (used when the lookup finds local prices) ----
# Sales: 1.2% inc VAT, the low end of typical sole-agency fees (1.2%-1.8% inc VAT),
# HomeOwners Alliance, 2026. Average across all agreements is 1.42% inc VAT.
SALES_FEE_RATE = 0.012
# Lettings: 12% of the first year's rent inc VAT (10% + VAT), the low end of
# fully managed fees (10-15% + VAT), LandlordVision, May 2026.
LETTINGS_FEE_RATE = 0.12

# Agencies listed on nesti.io as customers (checked 7 Oct 2026).
NESTI_CUSTOMERS = [
    "Northwood", "Johns & Co", "Belvoir", "Berkshire Hathaway", "Hunters", "Fine & Country",
    "Richard James", "Open House", "The Letting Station", "Anthony Jones", "Quealy & Co",
    "Forbes Global Properties", "Kay & Co", "Viewber", "Fardella & Bell", "Smart",
    "Luxury Hub", "Acaboom", "Trispens",
]


def compute(v: dict) -> dict:
    """Monthly figures from a dict of inputs. Percentages are whole numbers (27 = 27%)."""
    ooh_calls = v["branches"] * v["calls"] * v["ooh"] / 100
    missed = ooh_calls * v["unans"] / 100
    val_missed = missed * v["val"] / 100
    inst_lost = val_missed * v["comp"] / 100 * v["conv"] / 100
    month = inst_lost * v["fee"]
    return {
        "ooh_calls": ooh_calls,
        "missed": missed,
        "val_missed": val_missed,
        "inst_lost": inst_lost,
        "month": month,
        "year": month * 12,
        "waiting": missed - val_missed,
    }


def scenario_range(v: dict) -> tuple[float, float]:
    """Yearly loss under the Low and Central scenarios, keeping every other input."""
    low = compute({**v, **SCENARIOS["low"]})["year"]
    central = compute({**v, **SCENARIOS["central"]})["year"]
    return min(low, central), max(low, central)


def recovered(year_loss: float, cover: str, rec_pct: float) -> float:
    """Text-only AI recovers none of the phone loss; Nesti recovers rec_pct of it."""
    return year_loss * rec_pct / 100 if cover == "nesti" else 0.0


def round_to(n: float, step: int) -> int:
    return int(round(n / step) * step)


def estimate_fee(services, avg_price, avg_rent) -> dict:
    """Average fee per instruction from local prices. Returns value, basis text and source flag."""
    sales_fee = avg_price * SALES_FEE_RATE if avg_price else None
    let_fee = avg_rent * 12 * LETTINGS_FEE_RATE if avg_rent else None

    if services == "sales" and sales_fee:
        fee, basis = sales_fee, f"£{avg_price:,.0f} local average price × {SALES_FEE_RATE:.1%} sales fee"
    elif services == "lettings" and let_fee:
        fee, basis = let_fee, f"£{avg_rent:,.0f} a month × 12 × {LETTINGS_FEE_RATE:.0%} managed fee"
    elif sales_fee and let_fee:
        fee = (sales_fee + let_fee) / 2
        basis = (f"Half sales (£{avg_price:,.0f} × {SALES_FEE_RATE:.1%} = £{sales_fee:,.0f}), "
                 f"half lettings (£{avg_rent:,.0f} × 12 × {LETTINGS_FEE_RATE:.0%} = £{let_fee:,.0f})")
    elif sales_fee:
        fee, basis = sales_fee, f"£{avg_price:,.0f} local average price × {SALES_FEE_RATE:.1%} sales fee"
    elif let_fee:
        fee, basis = let_fee, f"£{avg_rent:,.0f} a month × 12 × {LETTINGS_FEE_RATE:.0%} managed fee"
    else:
        return {"value": DEFAULTS["fee"], "basis": None, "found": False}
    return {"value": max(round_to(fee, 50), 50), "basis": basis, "found": True}


def _num(x):
    """A positive number from the lookup, or None."""
    try:
        n = float(x)
        return n if n > 0 else None
    except (TypeError, ValueError):
        return None


def inputs_from_profile(profile: dict | None) -> dict:
    """Starting inputs for an agency, plus a note of which ones came from the lookup."""
    values = dict(DEFAULTS)
    found = {}
    if not profile or not profile.get("found"):
        return {"values": values, "found": found}

    branches = _num(profile.get("branch_count"))
    listed = [b for b in (profile.get("branches") or []) if isinstance(b, str) and b.strip()]
    if not branches and listed:
        branches = len(listed)
    if branches:
        values["branches"] = int(min(branches, 500))
        names = ", ".join(listed[:6]) + ("…" if len(listed) > 6 else "")
        found["branches"] = f"{int(branches)} found online" + (f": {names}" if names else "")

    price = (profile.get("avg_property_price") or {}).get("value")
    rent = (profile.get("avg_monthly_rent") or {}).get("value")
    fee = estimate_fee(profile.get("services"), _num(price), _num(rent))
    if fee["found"]:
        values["fee"] = fee["value"]
        found["fee"] = fee["basis"]
    return {"values": values, "found": found}


def _norm(name: str) -> str:
    name = name.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9 ]", "", name).strip()


def nesti_customer_match(agency_name: str | None) -> str | None:
    """The Nesti customer name this agency matches, if any."""
    if not agency_name:
        return None
    a = _norm(agency_name)
    for c in NESTI_CUSTOMERS:
        n = _norm(c)
        distinctive = len(n.split()) > 1 or len(n) > 6  # short names like "Smart" must match exactly
        if a == n or (distinctive and f" {n} " in f" {a} "):
            return c
    return None


def _closes(hours: str | None) -> list[tuple[int, str]]:
    """Every closing time in an hours string: '09:00-18:00, Fri 09:00-17:00' -> [(18,'00'), (17,'00')]."""
    if not hours or not isinstance(hours, str):
        return []
    return [(int(h), m) for h, m in re.findall(r"\d{1,2}[:.]\d{2}\s*[-–]\s*(\d{1,2})[:.](\d{2})", hours)]


def closing_time(hours: str | None) -> str | None:
    """'09:00-17:30' -> '5:30pm'. With several ranges, the latest closing time."""
    closes = _closes(hours)
    if not closes:
        return None
    h, mins = max(closes, key=lambda t: (t[0], t[1]))
    suffix = "pm" if h >= 12 else "am"
    h12 = h - 12 if h > 12 else (12 if h == 0 else h)
    return f"{h12}{'' if mins == '00' else ':' + mins}{suffix}"


def _hour(hours: str | None) -> int | None:
    closes = _closes(hours)
    return max(h for h, _ in closes) if closes else None


def profile_flags(profile: dict | None) -> list[dict]:
    """Things the rep should know before trusting the default inputs."""
    if not profile or not profile.get("found"):
        return []
    flags = []
    match = nesti_customer_match(profile.get("agency_name"))
    if match:
        flags.append({"kind": "info", "text": f"Nesti lists {match} as a customer on its website. "
                      "This agency or branch may already use Nesti."})
    cover = profile.get("out_of_hours_phone_cover") or {}
    if cover.get("status") == "yes":
        detail = f" ({cover['detail']})" if cover.get("detail") else ""
        flags.append({"kind": "warn", "text": f"This agency appears to answer calls out of hours{detail}. "
                      "The 94% unanswered rate may not apply, so lower it."})
    elif cover.get("status") == "maintenance_only":
        flags.append({"kind": "note", "text": "Has an out-of-hours line for tenant emergencies only. "
                      "Sales and lettings calls are not covered."})
    hours = profile.get("opening_hours") or {}
    close = _hour(hours.get("weekdays"))
    sunday = (hours.get("sunday") or "").strip().lower()
    late = close is not None and close >= 19
    sunday_open = bool(sunday) and sunday not in ("closed", "by appointment only", "by appointment")
    if late or sunday_open:
        bits = []
        if late:
            bits.append(f"open until {closing_time(hours.get('weekdays'))} on weekdays")
        if sunday_open:
            bits.append("open on Sundays")
        flags.append({"kind": "warn", "text": f"Published hours: {' and '.join(bits)}. Fewer calls fall out of "
                      "hours than at most agencies, so consider lowering the out-of-hours share."})
    return flags


def opener_line(profile: dict | None, year_loss: float, branches: int) -> str:
    """A one-line opener a sales rep can use, built only from what was found."""
    gbp_k = f"£{round(year_loss / 1000):,}k" if year_loss >= 1000 else f"£{year_loss:,.0f}"
    who = "your branch" if branches == 1 else f"your {branches} branches"
    if not profile or not profile.get("found"):
        return (f"Most agencies miss nearly every evening call. On conservative numbers that's about "
                f"{gbp_k} a year in instructions for {who}.")
    name = profile.get("agency_name") or "your agency"
    hours = profile.get("opening_hours") or {}
    close = closing_time(hours.get("weekdays"))
    several = len(_closes(hours.get("weekdays"))) > 1
    sunday = (hours.get("sunday") or "").strip().lower() if isinstance(hours.get("sunday"), str) else ""
    facts = []
    if close:
        facts.append(f"{name} closes {'by' if several else 'at'} {close} on weekdays")
    if sunday == "closed":
        facts.append("is shut on Sundays" if facts else f"{name} is shut on Sundays")
    lead = (" and ".join(facts) + ". ") if facts else ""
    return (f"{lead}On conservative numbers, unanswered out-of-hours calls could be costing "
            f"{who} about {gbp_k} a year in missed instructions.")
