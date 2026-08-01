"""
jira_client.py
Minimal Jira Cloud REST API (v3) client for creating story issues
with acceptance criteria in the description.
"""
from typing import Dict, Any, List, Optional

import requests


def _build_adf_description(description: str, acceptance_criteria: List[Dict[str, str]]) -> Dict[str, Any]:
    """Builds an Atlassian Document Format (ADF) body for the issue description.

    Each acceptance criterion is a dict with "scenario", "given", "when", "then"
    keys and is rendered as a labeled scenario block followed by a Given/When/Then
    bullet list, rather than one flat sentence.
    """
    content = [
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": description}],
        }
    ]

    if acceptance_criteria:
        content.append(
            {
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Acceptance Criteria"}],
            }
        )

        for criterion in acceptance_criteria:
            scenario_name = criterion.get("scenario", "Scenario")
            content.append(
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Scenario: {scenario_name}",
                            "marks": [{"type": "strong"}],
                        }
                    ],
                }
            )
            content.append(
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Given ",
                                            "marks": [{"type": "strong"}],
                                        },
                                        {"type": "text", "text": criterion.get("given", "")},
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "When ",
                                            "marks": [{"type": "strong"}],
                                        },
                                        {"type": "text", "text": criterion.get("when", "")},
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Then ",
                                            "marks": [{"type": "strong"}],
                                        },
                                        {"type": "text", "text": criterion.get("then", "")},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            )

    return {"type": "doc", "version": 1, "content": content}


AUTOMATION_LABEL = "Automated-Jira-Creation"


def _build_issue_payload(
    project_key: str,
    story: Dict[str, Any],
    issue_type: str = "Story",
) -> Dict[str, Any]:
    """Builds the Jira issue-create payload for a single story (used by both
    the real push and the dry-run preview, so they never drift apart).

    Every issue created this way is automatically tagged with
    AUTOMATION_LABEL, in addition to any story-specific labels, so
    tool-generated issues are easy to find/filter in Jira.
    """
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": story.get("title", "Untitled story"),
            "description": _build_adf_description(
                story.get("description", ""), story.get("acceptance_criteria", [])
            ),
            "issuetype": {"name": issue_type},
        }
    }

    labels = list(story.get("labels") or [])
    if AUTOMATION_LABEL not in labels:
        labels.append(AUTOMATION_LABEL)
    payload["fields"]["labels"] = labels

    priority = story.get("priority")
    if priority:
        payload["fields"]["priority"] = {"name": priority}

    return payload


def create_jira_issue(
    jira_url: str,
    email: str,
    api_token: str,
    project_key: str,
    story: Dict[str, Any],
    issue_type: str = "Story",
) -> Optional[str]:
    """
    Creates a single Jira issue from a story dict.

    Args:
        jira_url: base URL, e.g. https://yourcompany.atlassian.net
        email: Jira account email (used with API token for auth)
        api_token: Jira API token
        project_key: target project key, e.g. "BXY"
        story: dict with title, description, acceptance_criteria, priority, labels
        issue_type: Jira issue type name (default "Story")

    Returns:
        The created issue key (e.g. "BXY-123"), or None if creation failed.
    """
    url = f"{jira_url.rstrip('/')}/rest/api/3/issue"
    payload = _build_issue_payload(project_key, story, issue_type)

    response = requests.post(
        url,
        json=payload,
        auth=(email, api_token),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )

    if response.status_code >= 300:
        print(f"[jira] Failed to create '{story.get('title')}': "
              f"{response.status_code} {response.text}")
        return None

    return response.json().get("key")


def preview_stories(
    project_key: str,
    stories: List[Dict[str, Any]],
    issue_type: str = "Story",
) -> List[Dict[str, Any]]:
    """
    Dry-run version of push_stories: builds the exact same Jira issue-create
    payload for each story, but never sends a request or creates real issues.

    Returns each story with its would-be payload attached under "jira_preview".
    """
    results = []
    for story in stories:
        payload = _build_issue_payload(project_key, story, issue_type)
        results.append({**story, "jira_preview": payload})
    return results


def push_stories(
    jira_url: str,
    email: str,
    api_token: str,
    project_key: str,
    stories: List[Dict[str, Any]],
    issue_type: str = "Story",
) -> List[Dict[str, Any]]:
    """
    Pushes a list of stories to Jira, returning each with its created issue key attached.
    """
    results = []
    for story in stories:
        key = create_jira_issue(jira_url, email, api_token, project_key, story, issue_type)
        results.append({**story, "jira_key": key})
    return results
