"""
main.py
Entry point for the BRD -> Jira story pipeline.

Programmatic use:
    from main import process_brd
    result = process_brd("path/to/brd.docx", push_jira=True)

CLI use:
    python main.py --file path/to/brd.docx --output stories.json
    python main.py --file path/to/brd.docx --push-jira \
        --jira-url https://yourcompany.atlassian.net \
        --jira-email you@company.com --jira-token <token> \
        --jira-project BXY
"""
import argparse
import json
import os
from typing import Optional, Dict, Any

from dotenv import load_dotenv

load_dotenv()

from brd_parser import extract_text
from story_generator import generate_stories
from jira_client import push_stories, preview_stories


def process_brd(
    file_path: str,
    output_path: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    model: Optional[str] = None,
    push_jira: bool = False,
    dry_run: bool = False,
    jira_url: Optional[str] = None,
    jira_email: Optional[str] = None,
    jira_api_token: Optional[str] = None,
    jira_project_key: Optional[str] = None,
    jira_issue_type: str = "Story",
) -> Dict[str, Any]:
    """
    Full pipeline: parse BRD -> generate stories -> (optionally) push to Jira -> write output file.

    If push_jira=True and dry_run=True, Jira config is validated and each story's
    would-be Jira payload is attached under "jira_preview", but no request is sent
    and no issues are created.

    Returns a dict: {"stories": [...], "output_path": str | None}
    """
    brd_text = extract_text(file_path)
    if not brd_text.strip():
        raise ValueError("No text could be extracted from the BRD file.")

    stories = generate_stories(brd_text, api_key=anthropic_api_key, model=model)

    if push_jira:
        jira_url = jira_url or os.environ.get("JIRA_URL")
        jira_email = jira_email or os.environ.get("JIRA_EMAIL")
        jira_api_token = jira_api_token or os.environ.get("JIRA_API_TOKEN")
        jira_project_key = jira_project_key or os.environ.get("JIRA_PROJECT_KEY")

        missing = [
            name for name, val in [
                ("jira_url", jira_url), ("jira_email", jira_email),
                ("jira_api_token", jira_api_token), ("jira_project_key", jira_project_key),
            ] if not val
        ]
        if missing:
            raise ValueError(f"Missing Jira config: {', '.join(missing)}")

        if dry_run:
            stories = preview_stories(jira_project_key, stories, jira_issue_type)
        else:
            stories = push_stories(
                jira_url, jira_email, jira_api_token, jira_project_key, stories, jira_issue_type
            )

    result = {"stories": stories}

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        result["output_path"] = output_path
    else:
        result["output_path"] = None

    return result


def _cli():
    parser = argparse.ArgumentParser(description="Convert a BRD into Jira stories with acceptance criteria.")
    parser.add_argument("--file", required=True, help="Path to the BRD file (.docx, .pdf, .txt)")
    parser.add_argument("--output", default="stories.json", help="Path to write the output JSON")
    parser.add_argument("--model", default=None, help="Override the Claude model")
    parser.add_argument("--push-jira", action="store_true", help="Push generated stories to Jira")
    parser.add_argument("--dry-run", action="store_true",
                         help="With --push-jira, preview the Jira payload for each story without creating real issues")
    parser.add_argument("--jira-url", default=None)
    parser.add_argument("--jira-email", default=None)
    parser.add_argument("--jira-token", default=None)
    parser.add_argument("--jira-project", default=None)
    parser.add_argument("--jira-issue-type", default="Story")
    args = parser.parse_args()

    result = process_brd(
        file_path=args.file,
        output_path=args.output,
        model=args.model,
        push_jira=args.push_jira,
        dry_run=args.dry_run,
        jira_url=args.jira_url,
        jira_email=args.jira_email,
        jira_api_token=args.jira_token,
        jira_project_key=args.jira_project,
        jira_issue_type=args.jira_issue_type,
    )

    print(f"Generated {len(result['stories'])} stories.")
    if args.push_jira and args.dry_run:
        print("[DRY RUN — no issues created]")
        for s in result["stories"]:
            print(f"  Would create: {s.get('title')}")
    elif args.push_jira:
        for s in result["stories"]:
            print(f"  {s.get('jira_key', 'FAILED')}: {s.get('title')}")
    if result["output_path"]:
        print(f"Written to {result['output_path']}")


if __name__ == "__main__":
    _cli()
