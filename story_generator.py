"""
story_generator.py
Uses Claude to turn raw BRD text into structured Jira user stories
with acceptance criteria.
"""
import json
import os
from typing import List, Dict, Any

import anthropic

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

SYSTEM_PROMPT = """You are a senior business analyst who converts Business \
Requirements Documents (BRDs) into well-formed Jira user stories.

Read the BRD text provided and produce a JSON object ONLY — no markdown \
fences, no commentary, no preamble — with this exact shape:

{
  "stories": [
    {
      "title": "Short imperative story title",
      "description": "As a <role>, I want <goal>, so that <benefit>.",
      "acceptance_criteria": [
        {
          "scenario": "Short scenario name describing this case",
          "given": "Context or precondition",
          "when": "The action taken",
          "then": "The expected outcome"
        }
      ],
      "priority": "High" | "Medium" | "Low",
      "labels": ["optional", "short", "tags"]
    }
  ]
}

Guidelines:
- Break the BRD down into the smallest sensible independent stories.
- Every story must have at least 2 acceptance criteria.
- Every acceptance criterion MUST be a Gherkin-style scenario object with
  separate "scenario", "given", "when", and "then" fields — never collapse
  them into a single sentence. Each field holds only its own part (e.g.
  "given" holds just the precondition, not the whole Given/When/Then string).
- The "scenario" name should be short and descriptive (e.g. "Valid email
  submitted", "Reset link expired").
- Infer the user role from context; use "user" if genuinely unclear.
- Do not invent requirements that aren't implied by the text.
- Output valid JSON and nothing else.
"""


def generate_stories(brd_text: str, api_key: str = None, model: str = None) -> List[Dict[str, Any]]:
    """
    Calls Claude to convert BRD text into a list of story dicts.

    Args:
        brd_text: raw extracted BRD text.
        api_key: Anthropic API key (falls back to ANTHROPIC_API_KEY env var).
        model: model override (falls back to CLAUDE_MODEL env var, then a default).

    Returns:
        List of story dicts: title, description, acceptance_criteria, priority, labels.
    """
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=model or DEFAULT_MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"BRD content:\n\n{brd_text}"}],
    )

    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    ).strip()

    # Defensive cleanup in case the model wraps output in fences anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Claude did not return valid JSON. Raw output was:\n{raw_text}"
        ) from e

    return parsed.get("stories", [])
