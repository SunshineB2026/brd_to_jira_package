# Fix inconsistent repeat-query results and mismatched match-count narration in investor search

**Jira key:** BX-1122
**Link:** https://boxsy.atlassian.net/browse/BX-1122

## Description

### Problem

Running the identical one-word query `wearables` three times in a single session produced disjoint, inconsistent results:

- Run 1: 1 result
- Run 2: 20 results, all health-tagged (EIT Health, Healthbox, Mayo Clinic, Blueprint Health, XLerateHealth, J&J, Verily, Cigna, Penn Medicine, others)
- Run 3: 20 results, none health-tagged (Tenity, Google, Ulu Ventures, SICTIC, gener8tor, Pantera, Hashed, Orange DAO, NDRC, Heartcore, others)

There was zero overlap between runs 2 and 3.

**Known confound:** investors were added to the pipeline between runs. If already-added records are excluded from subsequent results, some of this variance is expected. However, this does not explain all of the discrepancy, since most of run 2's results were never added to the pipeline and still disappeared from run 3.

**Confirmed defect (independent of the above confound):** within a single response (run 2), the system opened with the statement `your exact filter 'Wearables' returned 0 tagged investors in the database (industry_focus match count = 0)`, then proceeded to return twenty health-tagged investors from that same database in that same response. The narrated telemetry directly contradicts the results delivered in the same response. This strongly suggests the system is generating a description of what a query might return rather than reporting the actual output of an executed query.

**Business impact:** the underlying corpus appears to contain more relevant data than the narration claims. A founder who runs a single query, is told the database has no tagged investors in their sector, and leaves as a result, has been talked out of relevant data by the product's own generated copy — even though matching records existed and were in fact returned in that same response. This is worse than a genuinely thin database, because it is both fixable and currently invisible to the team.

**Suggested direction (not a separate requirement, context only):** report counts derived strictly from the executed filter/query, or omit stated counts entirely when they cannot be tied to the actual result set returned. Surfacing the active filter as an editable chip (rather than only narrating it in text) would let users see filter broadening directly instead of relying on a textual description that may not match reality.

### Scope of this story

This story covers: (a) ensuring any match-count/telemetry narration accompanying search results is accurate and consistent with the actual results returned in that same response, (b) investigating and resolving the non-determinism/inconsistency of repeated identical queries within a session (independent of intentional pipeline-exclusion behavior), and (c) making any pipeline-based exclusion or filter-broadening behavior visible/consistent rather than only described in generated text.

## Acceptance Criteria

1. Given a user runs the exact same one-word query twice in the same session with no investors added to the pipeline in between, the system should return the same result set (or an equivalent, deterministic result set) both times.
2. Given investors are added to the pipeline between two runs of the identical query, the subsequent run should differ from the prior run only by the exclusion of the added investors; all other previously returned, non-added results should still appear.
3. Given a search response includes a narrated match count or telemetry statement (e.g. 'returned N tagged investors'), that stated count must equal the actual number of matching results returned within that same response.
4. The system should never state a zero or null match count for a filter while simultaneously returning non-zero results for that same filter in the same response.
5. If the system broadens or relaxes a filter because the exact filter returned no results, this broadening should be visibly reflected in the UI (e.g. as an editable filter chip or equivalent visible state) rather than communicated only through free-text narration.
6. When a filter has been broadened, the response should clearly indicate that broadening occurred and should not imply the results came from the original, unbroadened filter.
7. Any stated count of matches (e.g. 'industry_focus match count = 0') must be derived from the actual query execution against the database, not generated independently of the query result.
8. The active search filter should be visible and editable by the user (e.g. via filter chips), allowing the user to see and adjust the filter that produced the current results.
9. Pipeline-based exclusion of already-added investors, if applied, should behave consistently and predictably across repeated queries within a session.

## Positive Test Cases

- User runs the query 'wearables' twice in the same session with no pipeline changes in between -> both runs return the same result set (same records, same count).
- User runs the query 'wearables', and the response narrates a match count -> the narrated count matches the exact number of results returned in that response.
- User adds two investors returned by a prior run to their pipeline, then re-runs the identical query -> the new result set excludes only those two investors and otherwise matches the prior run's results.
- User runs a query where the exact filter returns zero results and the system broadens the filter -> the UI displays the broadened filter as an editable chip, and the response text explicitly states that broadening occurred.
- User edits or removes an active filter chip -> the query is re-executed with the updated filter and the displayed results correspond exactly to the new filter.
- User runs a query for a sector known to have tagged investors in the database -> the returned results and the narrated count both reflect the presence of those tagged investors.

## Negative Test Cases

- User runs the identical query twice in the same session with no pipeline changes -> if the two runs return disjoint result sets with no overlap, this is a failing defect reproduction.
- A response states '0 tagged investors returned' for a given filter but the same response lists 20 tagged investors matching that filter -> this is a failing defect reproduction (telemetry/result mismatch).
- A query under a strict/exact filter returns no matches, and the system silently substitutes broadened-filter results without disclosing the broadening anywhere in the UI or response text -> should fail.
- An investor previously added to the pipeline reappears in a later run of the same query without explanation -> should fail (exclusion logic inconsistency).
- A response includes a specific match-count statement (e.g. 'match count = N') where no corresponding query log or backing data exists to verify N -> should fail (unauditable/fabricated telemetry).
- User edits a filter chip but the underlying result set does not change to reflect the new filter -> should fail (filter chip not wired to actual query execution).

## Exit Criteria

- All acceptance criteria have been verified in a test/staging environment.
- All listed positive test cases pass.
- All listed negative test cases correctly fail to reproduce (i.e. the defects they describe no longer occur).
- Repeated identical queries in a session (with no pipeline changes) return consistent, deterministic results.
- Match-count/telemetry narration is verified to always match the actual returned result set across a representative regression sample of queries.
- Filter broadening, where it occurs, is visibly and accurately reflected in the UI rather than only in generated narrative text.
- No open blocking defects remain related to query/result inconsistency or telemetry-result mismatch.
- Documentation is updated to describe pipeline-exclusion behavior and filter-broadening behavior for internal reference.
- Reporting stakeholder/product owner has reviewed and signed off that the described behavior is resolved.

## Labels

bug, search, data-integrity, trust
