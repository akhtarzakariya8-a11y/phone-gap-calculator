"""Run with: python -m pytest -q"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from calc import (DEFAULTS, closing_time, compute, estimate_fee, inputs_from_profile,
                  nesti_customer_match, opener_line, recovered, scenario_range)


def test_central_worked_example():
    r = compute(DEFAULTS)
    assert round(r["ooh_calls"]) == 81
    assert round(r["missed"], 2) == 76.14
    assert round(r["val_missed"], 3) == 7.614
    assert round(r["inst_lost"], 5) == 1.33245
    assert round(r["month"]) == 3997
    assert round(r["year"]) == 47968


def test_low_and_central_range():
    low, central = scenario_range(DEFAULTS)
    assert round(low) == 21319
    assert round(central) == 47968


def test_recovery():
    year = compute(DEFAULTS)["year"]
    assert recovered(year, "text", 95) == 0
    assert round(recovered(year, "nesti", 95)) == 45570


def test_fee_estimates():
    assert estimate_fee("sales", 300000, None)["value"] == 3600          # 300k x 1.2%
    assert estimate_fee("lettings", None, 1500)["value"] == 2150         # 1500 x 12 x 12% = 2160 -> nearest 50
    assert estimate_fee("both", 300000, 1500)["value"] == 2900           # (3600 + 2160) / 2 = 2880 -> 2900
    assert estimate_fee(None, None, None) == {"value": 3000, "basis": None, "found": False}


def test_inputs_from_profile():
    p = {"found": True, "branch_count": 4, "services": "sales", "avg_property_price": {"value": 250000}}
    out = inputs_from_profile(p)
    assert out["values"]["branches"] == 4
    assert out["values"]["fee"] == 3000
    assert set(out["found"]) == {"branches", "fee"}
    assert inputs_from_profile({"found": False})["values"] == DEFAULTS


def test_nesti_match():
    assert nesti_customer_match("Hunters York") == "Hunters"
    assert nesti_customer_match("Belvoir Lettings Swindon") == "Belvoir"
    assert nesti_customer_match("Smart") == "Smart"
    assert nesti_customer_match("Smart Homes Estate Agents") is None
    assert nesti_customer_match("Winkworth") is None


def test_branch_fallback_and_flags():
    from calc import profile_flags
    p = {"found": True, "agency_name": "Hunters Estate & Letting Agents York", "branch_count": None,
         "branches": ["York"], "opening_hours": {"weekdays": "08:00-20:00", "sunday": "08:00-20:00"},
         "out_of_hours_phone_cover": {"status": "no_evidence"}}
    assert inputs_from_profile(p)["values"]["branches"] == 1
    texts = " ".join(f["text"] for f in profile_flags(p))
    assert "Nesti lists Hunters" in texts
    assert "open until 8pm on weekdays and open on Sundays" in texts


def test_opener():
    assert closing_time("09:00-17:30") == "5:30pm"
    assert closing_time("08:30-18:00") == "6pm"
    assert closing_time("Mon-Thu 09:00-18:00, Fri 09:00-17:00") == "6pm"
    assert closing_time("by appointment") is None
    p = {"found": True, "agency_name": "Acme Homes", "opening_hours": {"weekdays": "09:00-17:30", "sunday": "closed"}}
    line = opener_line(p, 47968, 1)
    assert line.startswith("Acme Homes closes at 5:30pm on weekdays and is shut on Sundays.")
    assert "£48k" in line
