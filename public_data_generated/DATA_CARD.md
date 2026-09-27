# HackAlem AI repositories: derived dataset

Derived, pseudonymised data for the paper *Measuring AI Coding Agent Use from Repository Traces: Evidence from a Hackathon Where Codex Was Required* (Bayan, 2026).

- **Source:** the 3,649 public GitHub repositories that the organisers of HackAlem AI (Astana, 23 September 2026) created in the organisation `BAITC-Hacks`. All of them were archived when collected.
- **Collected:** 24 September 2026, through the GitHub REST and GraphQL APIs and full mirror clones.
- **Licence:** CC BY 4.0 for this derived data. No source code, README text or commit message is redistributed.
- **Citation:** see the paper. The archived release with its DOI is pending.

## Files

| File | Rows | Content |
|---|---|---|
| `repositories.csv` | one per repository (3,649) | Timing, activity, track, stack, artefacts, agent traces and README features, under a random identifier (`id`) |
| `commits.csv` | one per team commit (31,955) | Commit time relative to the start, size, conventional-commit flag, script of the subject line, agent kind, and author as an ordinal within the repository |
| `aggregates/` | | The tables behind the figures, and `credentials_aggregate.json` with the credential results (aggregates only) |
| `recollection.csv` | one per repository | Repository name and the commit each clone ended at, so the data can be collected again. It carries no identifier, but rows of the other files can often be matched to it through their features (see Privacy). |
| `SHA256SUMS` | | Checksums of every file |

## Main columns of `repositories.csv`

| Column | Meaning |
|---|---|
| `created_date`, `archive_date` | Day of creation and day of the last update (UTC+5). The last update is the archive time |
| `evening_batch` | Created between 18:00 and 20:00 on 22 September (an organiser batch; see the paper) |
| `archived_before_event` | Last update before 13:00 on 23 September, so read-only during the event |
| `team_commits`, `window_commits`, `window_commits_author_time`, `hours_active` | Team commits on all branches (template commit excluded); commits between 13:00 and 18:00 on committer time and on author time; clock hours with commits |
| `active` | At least one team commit in the event window |
| `last_hour_share` | Share of window commits made between 17:00 and 18:00 (active repositories only) |
| `pr_only_commits`, `branches`, `pr_refs` | Commits reachable only through pull-request references; number of branches; number of pull-request references |
| `track`, `track_source` | Track 01–12; `earlier_table`, `corrected` (read against the README) or `unclear` |
| `primary_language`, `frameworks`, `llm_sdks` | From file sizes, manifests, imports and API endpoints at the final state |
| `tests`, `dockerfile`, `compose`, `ci`, `deploy_config` | Engineering artefacts present at the final state (1/0) |
| `gitignore_covers_env`, `env_example`, `node_modules_committed`, `virtualenv_committed`, `pycache_committed` | Repository hygiene (1/0) |
| `agents_md`, `claude_md`, `gemini_md`, `cursor_rules`, `copilot_instructions`, `other_agent_rules` | Agent context files (1/0) |
| `agent_branch_kinds` | Agents named at the start of branch names |
| `signed_commits_<kind>` | Commits with an agent signature (co-author trailer, "generated with" line or agent service account), by agent. `bot` means a generic bot account, such as the organisers' application, and is not an agent |
| `named_commits_<kind>` | Commits whose author or committer is named exactly after the tool (for example "Codex"), with no other signature |
| `codex_prefix_branches`, `claude_prefix_branches` | Branches whose names start with `codex` or `claude` |
| `readme_language`, `readme_words`, `readme_headings`, `readme_run_instructions`, `readme_deployed_link`, `readme_images`, `readme_mentions_agent_tool` | README features. Language is `russian`, `english`, `kazakh`, `mixed`, `template`, `no_readme` or `too_short` |
| `readme_names_codex`, `readme_names_claude_code` | The tool named in README prose, not as part of a file or model name (strict) |
| `readme_mentions_codex`, `readme_mentions_claude` | The word anywhere in the raw README (broad) |

The paper (Section 4) gives the exact definitions. Its code is in `src/` and `arxiv_paper_all/analysis/`.

## Privacy and ethics

- No names, e-mail addresses, commit SHAs next to features, commit messages or README text.
- Authors appear only as an ordinal within one repository, derived from a salted hash whose salt was never saved.
- **Credentials:** no secret value, no per-repository credential flag and no committed-`.env` flag are released. Credential results are aggregates only.
- **Pseudonymisation, not anonymisation:** the identifiers are random, but the source repositories are public, so a determined reader could match rows to repositories through their features. Please do not try to identify individuals or teams.
- **Removal:** to request that a repository be removed from a future version, contact the author.

## Reproducing the paper

`python arxiv_paper_all/analysis/reproduce_public.py` recomputes the headline numbers on participation, work timing, agent traces, README naming and artefacts from these files alone and compares them with the paper (23 of 23 match in this release). Credential results are released only as aggregates and are not recomputed. The full pipeline, which needs the clones, is `src/` followed by `arxiv_paper_all/analysis/run_analysis.py`.

## Known limitations

- A repository stands for a registration, not a person.
- Features are measured at the final state.
- Agent traces are partial.
- The README language rule is a letter heuristic.
- Track labels were checked by one person.

The paper's threats-to-validity section covers each of these.
