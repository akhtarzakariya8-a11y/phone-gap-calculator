# CLAUDE.md — Phone Gap Calculator

Streamlit app, a prototype by Zak for Nesti (AI workforce for UK estate and letting agents). Type an agency name: it is researched with Claude + web search, then a calculator estimates the fee income lost to unanswered out-of-hours calls.

Zak is a beginner coder: explain changes plainly, keep it simple.

## Files
- `prompts/research_prompt.txt`: the lookup "brain" (rules + JSON shape). Change behaviour here first.
- `research.py`: sends the request (model `claude-sonnet-5-5`, tool `web_search_20250305`, max 10 searches), streams progress, parses the JSON.
- `calc.py`: all maths, fee estimates, flags, opener line. No Streamlit. Tested in `tests/test_calc.py`.
- `app.py`: the UI. `content.py`: CSS, comparison grid, notes, sources.
- `examples/*.json`: pre-researched agencies that load with no API call.

## Rules
- Every number on screen must be sourced or labelled as an assumption.
- Don't frame Nesti against Alto; say "alongside CRM AI". Only claim "Alto's Lead Flow doesn't list phone calls".
- Note that the 94% / 27% figures come from InStep AI, a voice-AI vendor.
- Run `python -m pytest -q` after touching `calc.py`. Central defaults must give £47,968 a year; low gives £21,319.
- Secrets: `.env` locally, Streamlit Secrets in the cloud. Never commit them.
