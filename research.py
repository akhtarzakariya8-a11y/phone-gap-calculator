"""Agency lookup: asks Claude (with web search) to build a profile of one agency.

The instructions live in prompts/research_prompt.txt. This file only sends the
request, shows progress, and turns Claude's reply into a Python dict.
"""

import json
import re
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-5-5"
MAX_SEARCHES = 10
MAX_TOKENS = 6000
PROMPT_PATH = Path(__file__).parent / "prompts" / "research_prompt.txt"


class ResearchError(Exception):
    """Something went wrong that the person using the app should hear about."""


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_request(agency: str, hint: str = "") -> str:
    lines = [f"Agency name: {agency.strip()}"]
    if hint.strip():
        lines.append(f"Town or website: {hint.strip()}")
    lines.append("Build the profile now and reply with the JSON object only.")
    return "\n".join(lines)


def extract_json(text: str) -> dict:
    """Pull the JSON object out of Claude's reply, even with stray text around it."""
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ResearchError("The lookup didn't return a profile. Try again, or add the town.")
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ResearchError("The lookup returned a profile that couldn't be read. Try again.") from exc


def final_text(content) -> str:
    """Join the text written after the last search result (that is where the JSON is)."""
    last_result = -1
    for i, block in enumerate(content):
        if getattr(block, "type", "") == "web_search_tool_result":
            last_result = i
    parts = [b.text for b in content[last_result + 1 :] if getattr(b, "type", "") == "text"]
    if not "".join(parts).strip():  # fall back to every text block
        parts = [b.text for b in content if getattr(b, "type", "") == "text"]
    return "".join(parts)


def research_agency(agency: str, hint: str = "", api_key: str | None = None, on_progress=None) -> dict:
    """Return the agency profile dict. Calls on_progress(message) as searches run."""
    if not agency.strip():
        raise ResearchError("Type an agency name first.")

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    messages = [{"role": "user", "content": build_request(agency, hint)}]
    tools = [{
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": MAX_SEARCHES,
        "user_location": {"type": "approximate", "country": "GB", "timezone": "Europe/London"},
    }]
    searches = 0

    for _round in range(4):  # a long search turn can pause; continue it up to 3 times
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=load_prompt(),
                messages=messages,
                tools=tools,
            ) as stream:
                for event in stream:
                    if event.type == "content_block_stop":
                        block = event.content_block
                        if block.type == "server_tool_use" and on_progress:
                            searches += 1
                            query = (block.input or {}).get("query", "")
                            on_progress(f"Search {searches}: {query}")
                response = stream.get_final_message()
        except anthropic.AuthenticationError as exc:
            raise ResearchError("The Anthropic API key is missing or wrong.") from exc
        except anthropic.RateLimitError as exc:
            raise ResearchError("Too many lookups at once. Wait a minute and try again.") from exc
        except anthropic.BadRequestError as exc:
            raise ResearchError(f"The lookup request was refused: {exc.message}") from exc
        except anthropic.APIError as exc:
            raise ResearchError("The lookup service had a problem. Try again in a moment.") from exc

        if response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            if on_progress:
                on_progress("Still searching…")
            continue
        break

    profile = extract_json(final_text(response.content))
    profile["_searches"] = searches
    return profile


if __name__ == "__main__":  # quick manual test: python research.py "Agency name" "Town"
    import sys
    from dotenv import load_dotenv

    load_dotenv()
    name = sys.argv[1] if len(sys.argv) > 1 else "Hunters"
    town = sys.argv[2] if len(sys.argv) > 2 else ""
    result = research_agency(name, town, on_progress=print)
    print(json.dumps(result, indent=2, ensure_ascii=False))
