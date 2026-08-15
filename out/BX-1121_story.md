# Data Room - Document Generation (AI-Generated Documents from Uploaded Source Files)

**Jira key:** BX-1121
**Link:** https://boxsy.atlassian.net/browse/BX-1121

## Description

The Data Room organizes an investor's due-diligence requests into one folder per investor question, with folder subtitles indicating what belongs in each folder, and a readiness percentage showing founders how complete their data room is. Each folder supports per-folder sharing controls, including view-only versus download permissions, expiry dates on shared links, and contact-level (rather than org-level) access grants. The empty state for folders offers 'Import from Google Drive' and 'Import from Notion' options to help founders populate the room quickly.

This story extends that foundation with document generation: investors frequently request the same underlying facts in different formats (a one-pager, a specific slide, metrics in their own template), and today founders must manually assemble each requested format from their existing source documents. The Data Room already surfaces a 'Generate' button and an 'AI Generated' folder, indicating the intended direction. This story covers wiring that 'Generate' capability to an AI generation service (e.g., Claude) so a founder can issue a natural-language request (for example, 'give me the two-page version with unit economics up front') and receive a generated document assembled from the files already uploaded to the data room, without needing to manually copy and reformat content.

Generated documents are produced from existing uploaded source files, are placed into the 'AI Generated' folder, and are subject to the same sharing, permission, and readiness mechanics as other data room documents. This story does not introduce new functional areas beyond the generation capability implied by the existing 'Generate' button/'AI Generated' folder; it fleshes out the behavior, edge cases, and quality bar for that capability along with the existing folder/sharing/import behaviors already present in the Data Room.

## Acceptance Criteria

1. Given a Data Room with one folder per investor question, each folder should display a subtitle describing what type of content belongs in it.
2. Given a Data Room with folders populated to varying degrees, the system should display an overall readiness percentage reflecting how complete the data room is.
3. Given a folder in the Data Room, the founder should be able to configure sharing at the per-folder level, independent of other folders.
4. Given a shared folder, the founder should be able to set the access level to either view-only or download-enabled.
5. Given a shared folder, the founder should be able to set an expiry date after which access to that folder is revoked.
6. Given a shared folder, access should be grantable to specific individual contacts rather than to an entire organization.
7. Given an empty folder, the founder should see options to 'Import from Google Drive' and 'Import from Notion' in the empty state.
8. Given a folder or the data room contains a 'Generate' action, selecting it should allow the founder to request a generated document.
9. Given a founder submits a natural-language generation request (e.g., 'give me the two-page version with unit economics up front'), the system should produce a document that reflects the requested format and emphasis using content drawn from files already uploaded to the data room.
10. Given a document is generated, it should be placed into the 'AI Generated' folder.
11. Given a document has been generated, it should be subject to the same sharing controls (view-only/download, expiry, per-contact access) as other data room documents.
12. Given the founder has no relevant source documents uploaded for a requested generation, the system should inform the founder that it cannot fulfill the request rather than fabricating content.
13. Given a generation request is in progress, the founder should see a status/progress indication rather than an unexplained wait.
14. Given a generation request completes, the founder should be able to view, download, or share the resulting document from the 'AI Generated' folder.
15. Given a founder is not satisfied with a generated document, the founder should be able to re-request generation or adjust the request.

## Positive Test Cases

- Founder opens a folder with no documents and sees both 'Import from Google Drive' and 'Import from Notion' options displayed in the empty state.
- Founder uploads several source documents to the data room, then clicks 'Generate' and requests 'a two-page version with unit economics up front'; the resulting document is created, contains unit economics content near the beginning, and is roughly two pages.
- Founder generates a document and confirms it appears automatically in the 'AI Generated' folder.
- Founder sets a generated document's sharing to view-only and confirms an external contact can view but not download it.
- Founder sets a generated document's sharing to download-enabled and confirms an external contact can download it.
- Founder sets an expiry date on a shared folder and confirms access is available before the expiry date.
- Founder shares a folder with one specific contact and confirms another contact in the same organization cannot access it.
- Founder fills several folders with documents and confirms the readiness percentage increases accordingly.
- Founder requests a generated document in a different shape (e.g., 'one-pager' vs 'slide format') from the same source documents and receives outputs matching each requested format.
- Founder re-requests generation with revised instructions after reviewing an initial generated document and receives an updated document reflecting the new instructions.

## Negative Test Cases

- Founder clicks 'Generate' with no source documents uploaded anywhere in the data room; system informs the founder that generation cannot proceed rather than producing an empty or fabricated document.
- Founder submits a generation request referencing content not present in any uploaded source document; system does not fabricate that content and instead indicates the information is unavailable.
- Founder without edit/generation permission attempts to use the 'Generate' button; action is blocked or hidden.
- Contact whose folder access has expired attempts to open a shared link; access is denied.
- Contact granted view-only access attempts to download a document; download is blocked.
- Contact not explicitly granted access to a folder attempts to open its shared link; access is denied even if they belong to the same organization as a permitted contact.
- Founder submits an extremely vague or empty generation request (e.g., blank prompt); system prompts for clarification rather than generating an arbitrary document.
- Generation request fails due to a service error (e.g., AI service unavailable); founder sees an error message and no partial/corrupted document is added to the 'AI Generated' folder.
- Founder attempts to import from Google Drive or Notion without having authorized/connected the respective account; system prompts for authorization rather than failing silently.

## Exit Criteria

- All acceptance criteria have been implemented and verified.
- All listed positive and negative test cases have been executed and pass.
- No open blocking or high-severity bugs related to folder structure, sharing permissions, expiry enforcement, or document generation remain.
- Generated documents are confirmed to be produced only from existing uploaded source content, with no fabrication of unsupported facts.
- Sharing permission behavior (view-only vs download, expiry, per-contact access) has been verified for both the 'AI Generated' folder and standard folders.
- Import from Google Drive and Import from Notion flows have been verified to function from the folder empty state.
- Readiness percentage calculation has been verified to reflect folder completeness accurately.
- Stakeholder sign-off obtained confirming the generation experience meets the intent described (natural-language request to formatted output from existing files).
- Relevant documentation/help content updated to describe the Generate feature and its permission/sharing implications.

## Labels

data-room, ai-generation, document-management, sharing-permissions
