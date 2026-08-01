# BRD → Jira Story Generator

Feeds a BRD file (`.docx`, `.pdf`, or `.txt`) into Claude, gets back
structured user stories with Gherkin-style acceptance criteria (Scenario /
Given / When / Then), and optionally pushes them straight into Jira as
issues.

## Setup — follow these steps in order

1. **Get the files.** Download/unzip the whole project into one flat
   folder (no nested subfolders) — e.g. `C:\Users\you\brd_to_jira` on
   Windows, or `~/brd_to_jira` on Mac/Linux. You should see `main.py`,
   `brd_parser.py`, `requirements.txt`, `.env`, and the rest of the files
   directly inside — not one level deeper.

2. **Open a terminal in that exact folder.**
   - Windows: open the folder in File Explorer, click the address bar,
     type `cmd`, press Enter.
   - Mac/Linux: `cd` into the folder.

3. **Create and activate a virtual environment, then install dependencies.**
   Type these one at a time and wait for each to finish:

   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate.bat
   pip install -r requirements.txt

   # Mac/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   After activating, your prompt should show `(.venv)` at the start of the
   line. If `python`/`python3` isn't recognized at all, Python itself isn't
   installed or isn't on your PATH — install it from python.org first.

   (`install.sh` / `install.bat` do the same three commands for you, but
   Windows SmartScreen may block a downloaded `.bat` file from running —
   if so, just type the three commands above manually instead.)

4. **Confirm your Anthropic API key is set.** Open `.env` in a text editor
   and check it has a line like:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

   No quotes, no spaces around the `=`. `main.py` and `test_smoke.py` load
   this automatically on startup — no manual `export`/`set` needed.

5. **Run the smoke test** to confirm everything works before touching a
   real BRD:

   ```bash
   python test_smoke.py
   ```

   This always checks `brd_parser` against the included `sample_brd.docx`
   (no API key needed). If `ANTHROPIC_API_KEY` is set, it also runs a real
   `story_generator` call and asserts every acceptance criterion has a
   scenario name plus separate Given/When/Then fields. It never touches
   Jira — that's a deliberate separate step so you don't accidentally
   create real issues while testing.

## Jira setup (only needed if you plan to push stories to Jira)

You need four values:

| Value | Where to find it |
|---|---|
| `JIRA_URL` | Your Jira site's base URL, e.g. `https://yourcompany.atlassian.net` |
| `JIRA_EMAIL` | The email you log into Jira/Atlassian with |
| `JIRA_API_TOKEN` | Create one at https://id.atlassian.com/manage-profile/security/api-tokens — copy it immediately, it's only shown once |
| `JIRA_PROJECT_KEY` | The prefix on your issue keys, e.g. `BXY` if tickets look like `BXY-101` |

You'll also need **Create Issue** permission on that Jira project — if a
push comes back with a 403, that's a permissions issue, not a config
mistake.

Add all four to your `.env` file, below the Anthropic key:

```
JIRA_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=your-token-here
JIRA_PROJECT_KEY=BXY
```

## CLI usage

Just generate stories to a JSON file:
```bash
python main.py --file /path/to/brd.docx --output stories.json
```

**Preview a Jira push first, without creating anything** — recommended
before your first real push:
```bash
python main.py --file /path/to/brd.docx --output stories.json --push-jira --dry-run
```
This validates your Jira config and builds the exact payload each story
would send (visible under `jira_preview` in the output JSON), but makes no
network calls to Jira and creates no issues.

Generate AND push to Jira for real:
```bash
python main.py --file /path/to/brd.docx --output stories.json --push-jira
```

You can also pass Jira config as flags instead of `.env`/env vars:
```bash
python main.py --file brd.pdf --push-jira \
  --jira-url https://yourcompany.atlassian.net \
  --jira-email you@company.com \
  --jira-token xxxx \
  --jira-project BXY
```

## Programmatic usage

```python
from main import process_brd

result = process_brd(
    file_path="brd.docx",
    output_path="stories.json",
    push_jira=True,
)

for story in result["stories"]:
    print(story["jira_key"], story["title"])
```

## Output shape

Each acceptance criterion is a structured Gherkin scenario (not one long
sentence):

```json
{
  "stories": [
    {
      "title": "Allow users to reset their password",
      "description": "As a user, I want to reset my password, so that I can regain access to my account.",
      "acceptance_criteria": [
        {
          "scenario": "Valid reset request",
          "given": "A registered email is submitted",
          "when": "The user requests a reset",
          "then": "A reset link is emailed within 1 minute"
        },
        {
          "scenario": "Expired reset link",
          "given": "A reset link is more than 30 minutes old",
          "when": "The user clicks it",
          "then": "They see a clear expiry message"
        }
      ],
      "priority": "High",
      "labels": ["auth"],
      "jira_key": "BXY-123"
    }
  ]
}
```

When pushed to Jira, each scenario renders as a bold "Scenario: ..."
heading followed by separate Given / When / Then bullets, rather than one
dense paragraph.

## Files

- `brd_parser.py` — extracts raw text from `.docx` / `.pdf` / `.txt`
- `story_generator.py` — calls Claude to turn that text into structured
  stories with Gherkin-style acceptance criteria
- `jira_client.py` — builds Jira issue payloads (ADF descriptions) and
  pushes stories to Jira via the REST API v3; also supports dry-run preview
- `main.py` — CLI + `process_brd()` programmatic entry point
- `test_smoke.py` — sanity check: parser always, story generation if a key
  is set, never touches Jira
- `.env` — your real secrets (never commit this)
- `.env.example` — a blank template safe to share/commit instead

## Notes

- Model defaults to `claude-sonnet-5`; override with `--model` or the
  `CLAUDE_MODEL` env var.
- Jira issue creation uses the Cloud REST API v3 (Atlassian Document Format
  descriptions). If you're on Jira Server/Data Center, you'll need to switch
  to the v2 API and a plain-text description.
- `.env` is in `.gitignore` — never commit it. Share `.env.example` instead
  if handing this project to someone else.
- No web server/UI here — it's a plain Python module you call directly or
  via the CLI.
