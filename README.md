# Phone Gap Calculator

A prototype by Zak for Nesti. Type in any UK estate or letting agency. The app researches it on the web and estimates the fee income it loses each year to phone calls nobody answers out of hours. It then shows how much of that comes back with AI that answers calls (Nesti) versus text-only CRM AI.

## How it works

1. **Lookup** (`research.py` + `prompts/research_prompt.txt`): Claude Sonnet 5.5 with web search finds the agency's branches, opening hours, out-of-hours phone cover, WhatsApp/chat, local average house price and rent, and reviews that complain about unanswered calls. It returns a JSON profile with a source link for each fact. Takes about 15–30 seconds and costs roughly 10–15p.
2. **Inputs** (`calc.py`): the branch count and the average fee come from the lookup. Every other input is a labelled public figure or assumption, and every number can be edited on screen.
3. **Maths** (`calc.py`):
   - Out-of-hours calls = branches × calls per branch × out-of-hours share
   - Missed calls = out-of-hours calls × unanswered rate
   - Missed valuation enquiries = missed calls × valuation share
   - Instructions lost = missed valuation enquiries × competitor rate × conversion rate
   - Fee income at risk = instructions lost × fee (per month, × 12 per year)
4. **Fee from local prices**: sales = 1.2% of the local average price; lettings = 12% of a year's rent; agencies doing both get the average of the two.

## Run locally

```
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
streamlit run app.py
python -m pytest -q        # checks the maths (£47,968 central, £21,319 low)
```

## Deploy (Streamlit Community Cloud)

New app → this repo → branch `main` → file `app.py`. Under Advanced settings → Secrets, add:

```
ANTHROPIC_API_KEY = "sk-ant-..."
```

## Guardrails

- Lookups are capped at 60 a day across all users (`DAILY_LOOKUP_LIMIT` in `app.py`), and each agency is cached for 24 hours.
- The three examples in `examples/` load instantly with no API call. They were researched on 7 Oct 2026.
- Agency facts come from an AI web search. Check the linked sources before quoting them.
- Not affiliated with or endorsed by Nesti, Alto or any agency named.
