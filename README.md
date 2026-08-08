# BRD to Jira Story Generator

Parses a BRD (docx/pdf/txt/md) and generates a single, consolidated Jira
story via Claude — all acceptance criteria live inside that one story,
however long it gets.

## Setup

    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=your-key-here

## Mode 1: Brand new story from a BRD

    python brd_to_jira.py new --brd path/to/brd.docx --output out/story.json

## Mode 2: Enrich an existing story using a BRD

You can supply the existing story two ways — pick one:

**A. Fetch it live from Jira by issue key** (no export needed):

    export JIRA_BASE_URL=https://yourco.atlassian.net
    export JIRA_EMAIL=you@yourco.com
    export JIRA_API_TOKEN=your-jira-api-token

    python brd_to_jira.py update \
        --brd path/to/brd.docx \
        --jira-key BOX-142 \
        --output out/story.json

**B. Point at a local file** (JSON export, or a plain text/markdown paste):

    python brd_to_jira.py update \
        --brd path/to/brd.docx \
        --existing-story path/to/existing_story.json \
        --output out/story.json

`--existing-story` accepts either a JSON file (with key/summary/description/
acceptance_criteria fields) or a plain .txt/.md file with the story pasted
in as free text. `--jira-key` and `--existing-story` are mutually exclusive
— use one or the other.

## Optional: push straight to Jira

Add `--push` to either command. It needs the same `JIRA_BASE_URL`,
`JIRA_EMAIL`, `JIRA_API_TOKEN` env vars as `--jira-key` above, plus:

    export JIRA_PROJECT_KEY=BOX

`update --push` updates the existing issue (using its `key`, whether it
came from `--jira-key` or a file); `new --push` creates a brand new issue
in `JIRA_PROJECT_KEY`.

## Output

Either way, `--output` gets a JSON file shaped like:

    {
      "summary": "...",
      "description": "...",
      "acceptance_criteria": ["...", "...", "..."],
      "labels": ["..."]
    }
