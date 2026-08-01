"""
test_smoke.py
Quick sanity check before handing this off to anyone.

- Always tests brd_parser (no API key needed).
- Only tests story_generator (calls Claude) if ANTHROPIC_API_KEY is set.
- Never touches Jira, even if JIRA_* env vars are set — that's a separate,
  deliberate step (see README) since it creates real issues.

Run: python test_smoke.py
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from brd_parser import extract_text


def test_parser():
    print("1. Testing brd_parser on sample_brd.docx ...")
    text = extract_text("sample_brd.docx")
    assert "password" in text.lower(), "Expected sample BRD content not found"
    print("   OK — extracted", len(text), "characters\n")
    return text


def test_story_generation(brd_text):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("2. Skipping story_generator test — ANTHROPIC_API_KEY not set.")
        print("   Set it and re-run to test this step.\n")
        return

    print("2. Testing story_generator (calls Claude) ...")
    from story_generator import generate_stories

    stories = generate_stories(brd_text)
    assert len(stories) > 0, "Expected at least one story"
    for s in stories:
        assert s.get("acceptance_criteria"), f"Story '{s.get('title')}' has no acceptance criteria"
        for ac in s["acceptance_criteria"]:
            for field in ("scenario", "given", "when", "then"):
                assert ac.get(field), f"Acceptance criterion missing '{field}': {ac}"
    print(f"   OK — generated {len(stories)} stories, all with Given/When/Then scenarios\n")

    print("   Sample story:")
    print(f"   Title: {stories[0]['title']}")
    print(f"   Description: {stories[0]['description']}")
    print(f"   Acceptance criteria:")
    for ac in stories[0]["acceptance_criteria"]:
        print(f"     Scenario: {ac['scenario']}")
        print(f"       Given {ac['given']}")
        print(f"       When  {ac['when']}")
        print(f"       Then  {ac['then']}")


if __name__ == "__main__":
    brd_text = test_parser()
    test_story_generation(brd_text)
    print("Smoke test complete.")
