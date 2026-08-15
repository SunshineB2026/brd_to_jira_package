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

## Mode 3: Enrich an existing story — no BRD

Use this when the requirements are already written directly inside the
Jira story itself and there's no separate BRD document. It fleshes out the
description and generates acceptance criteria, positive/negative test
cases, and exit criteria based only on what's already in the story.

    python brd_to_jira.py enrich --jira-key BOX-142 --output out/story.json

Or from a local file instead of live Jira:

    python brd_to_jira.py enrich --existing-story path/to/story.json --output out/story.json

`--push` is optional here (see below) — useful if you only have view
access to the issue and want to review the generated content before
deciding how to get it into Jira (e.g. pasting it in yourself).

## Optional: push straight to Jira

Add `--push` to any of the three commands. It needs the same
`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` env vars as `--jira-key`
above, plus (for `new` only):

    export JIRA_PROJECT_KEY=BOX

`update --push` and `enrich --push` update the existing issue (using its
`key`, whether it came from `--jira-key` or a file); `new --push` creates
a brand new issue in `JIRA_PROJECT_KEY`.

If you don't pass `--push` at all — or if `--push` fails (e.g. you have
view but not edit permission on the issue) — the generated story is still
written to your `--output` file, and the script tells you so, so you can
copy/paste it into Jira manually.

Add `--attach-brd` alongside `--push` (only for `new`/`update`, since
`enrich` has no BRD file) to also upload the original BRD file itself as
an attachment on the Jira issue, so the source document is traceable
directly from the ticket:

    python brd_to_jira.py update --brd path/to/brd.docx --jira-key BOX-142 \
        --output out/story.json --push --attach-brd

## Output format

`--output` accepts either a `.md` or `.json` filename — the extension you
choose decides the format:

- **`.md` (recommended for reading)** — a clean, headed Markdown file with
  real bulleted/numbered lists for Acceptance Criteria, Positive Test
  Cases, Negative Test Cases, and Exit Criteria. Readable straight in any
  editor, GitHub, or Jira's markdown-friendly paste.
- **`.json`** — the raw structured data, useful if you're piping the
  output into another script or want it as `--existing-story` input later.

Example:

    python brd_to_jira.py enrich --jira-key BX-1118 --output out/story.md

produces something like:

    # Configurable dashboard notification preferences

    **Jira key:** BX-1118
    **Link:** https://boxsy.atlassian.net/browse/BX-1118

    ## Description

    Allow users and admins to configure notification channels...

    ## Acceptance Criteria

    1. User can toggle email vs in-app notifications per event type
    2. User can select a daily digest option instead of real-time notifications

    ## Positive Test Cases

    - User enables email notifications for task-assigned events and receives an email

    ## Negative Test Cases

    - Non-admin user attempts to change org-wide defaults and is denied

    ## Exit Criteria

    - All acceptance criteria verified
    - No open blocking bugs

When pushed to Jira (`--push`), it's always sent as proper Jira rich text
regardless of which local format you chose: paragraphs for the
description, then headed, listed sections for Acceptance Criteria
(numbered), Positive Test Cases, Negative Test Cases, and Exit Criteria
(bulleted) — not a flat wall of text.

**Filenames get the Jira key automatically.** If you pass
`--output out/story.json`:
- `update`/`enrich` (key already known) → written straight to
  `out/BX-1118_story.json`
- `new --push` (key only exists after creation) → written first as
  `out/story.json`, then renamed to `out/BX-1200_story.json` once Jira
  assigns the new key
- `new` without `--push` → stays `out/story.json`, since there's no key yet

**A clickable Jira link is also printed** whenever a key is known and
`JIRA_BASE_URL` is set, e.g.:

    Jira story: https://boxsy.atlassian.net/browse/BX-1118
