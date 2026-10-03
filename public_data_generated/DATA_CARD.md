# HackAlem AI repositories: derived dataset

Derived, pseudonymised data for the paper *Agentic AI Under a Five-Hour Deadline: Traces of Coding Agents in 3,649 Hackathon Repositories* (Bayan, 2026).

- **Source:** the 3,649 public GitHub repositories that the organisers of HackAlem AI (Astana, 23 September 2026) created in the organisation `BAITC-Hacks`. All of them were archived when collected.
- **Collected:** 24 September 2026, through the GitHub REST and GraphQL APIs and full mirror clones.
- **Licence:** CC BY 4.0 for this derived data. No source code, README text or commit message is redistributed.
- **Citation:** Bayan, T. (2026). *HackAlem AI repository study: pseudonymised data and code* (v1.0.4). Zenodo. https://doi.org/10.5281/zenodo.23091476

## Files

| File | Rows | Content |
|---|---|---|
| `repositories.csv` | one per repository (3,649) | Timing, activity, track, stack, artefacts, agent traces and README features, under a random identifier (`id`) |
| `commits.csv` | one per team commit (31,955) | Commit time relative to the start, size, conventional-commit flag, script of the subject line, agent kind, and author as an ordinal within the repository |
| `aggregates/` | | The tables behind the figures, and `credentials_aggregate.json` with the credential results (aggregates only) |
| `recollection.csv` | one per repository | Repository name and the default-branch commit at which each clone ended, so the data can be collected again (the clones also kept every other branch and pull-request reference; their tips are not listed). It carries no identifier, but rows of the other files can often be matched to it through their features (see Privacy). |
| `SHA256SUMS` | | Checksums of every file |

## Main columns of `repositories.csv`

Columns marked (1/0) are flags; `readme_words`, `readme_headings`, `readme_images` and `readme_kazakh_letters` are counts, so a share of repositories with images is the share with `readme_images > 0`. Lists (`frameworks`, `llm_sdks`, `agent_branch_kinds`) are separated by `;`. Stack, artefact, context-file and README columns are empty for repositories without team commits, which were not scanned. Read `track` as a string (`01` to `12`).

| Column | Meaning |
|---|---|
| `created_date`, `archive_date` | Day of creation and day of the last update (UTC+5). The last update is the archive time |
| `template_found` | The organisers' template commit was found by the account-independent rule (1/0; 0 means the history was rewritten) |
| `evening_batch` | Created between 18:00 and 20:00 on 22 September (an organiser batch; see the paper) |
| `archived_before_event` | Last update before 13:00 on 23 September, so read-only during the event |
| `team_commits`, `window_commits`, `window_commits_author_time`, `hours_active` | Team commits on all branches (template commit excluded); commits between 13:00 and 18:00 on committer time and on author time; number of the five clock hours of the window with at least one team commit |
| `active` | At least one team commit in the event window |
| `last_hour_share` | Share of window commits made between 17:00 and 18:00 (active repositories only) |
| `pr_only_commits`, `branches`, `pr_refs` | Commits reachable only through pull-request references; number of branches; number of pull-request references |
| `track`, `track_source` | Track `01`–`12` (names below); `earlier_table`, `corrected` (read against the README) or `unclear` |
| `primary_language`, `frameworks`, `llm_sdks` | From file sizes, manifests, imports and API endpoints at the final state |
| `tests`, `dockerfile`, `compose`, `ci`, `deploy_config` | Engineering artefacts present at the final state (1/0). A test file lies in a `test`, `tests` or `__tests__` folder or is named like `test_*.py`, `*_test.py`, `*_test.go` or `*.test.ts` / `*.spec.js` |
| `test_functions` | A test file in Python, JavaScript, TypeScript or Go defines a test (`def test_…`, `class Test…`, `it(`, `test(`, `describe(` or `func Test…`) (1/0) |
| `gitignore_covers_env`, `env_example`, `node_modules_committed`, `virtualenv_committed`, `pycache_committed` | Repository hygiene (1/0) |
| `agents_md`, `claude_md`, `gemini_md`, `cursor_rules`, `copilot_instructions`, `other_agent_rules` | Agent context files outside vendored folders (1/0). `agents_md` and `claude_md` leave out the files Next.js writes itself: an AGENTS.md holding only its managed block, and a CLAUDE.md holding only `@AGENTS.md` next to such a block |
| `nextjs_agent_files` | An AGENTS.md with the Next.js managed block is present (1/0) |
| `agent_branch_kinds` | Agents named at the start of branch names |
| `signed_commits_<kind>` | Commits with an agent signature (co-author trailer, "generated with" line or agent service account), by agent. `bot` means a generic bot account, such as the organisers' application, and is not an agent |
| `named_commits_<kind>` | Commits whose author or committer is named exactly after the tool (for example "Codex"), with no other signature |
| `codex_prefix_branches`, `claude_prefix_branches` | Branches whose names start with `codex` or `claude` |
| `readme_language`, `readme_words`, `readme_headings`, `readme_run_instructions`, `readme_deployed_link`, `readme_images`, `readme_kazakh_letters` | README features. Language is `russian`, `english`, `kazakh`, `mixed`, `template`, `no_readme` or `too_short`; a *written* README is one of the first four. `readme_kazakh_letters` counts the nine letters that Kazakh has and Russian does not |
| `readme_mentions_agent_tool` | Earlier broad measure: `codex`, `claude`, `copilot`, `cursor` or `agents.md` anywhere in the README (1/0); not used in the paper |
| `approach_core_method`, `approach_secondary_method`, `approach_llm_role`, `approach_interface`, `approach_evaluation`, `approach_provided_data`, `approach` | How the team solved its brief, coded from the README and file list by a language model (`deepseek-flash`, 28 September 2026) with the codebook in `src/llm_codebook.py`; track-labelled active repositories only. Methods: `llm_prompt`, `llm_agent`, `ml_model`, `algorithm`, `pretrained`, `unclear`; LLM role: `none`, `core`, `support`, `unclear`; `approach` is the model's summary in at most 12 words |
| `readme_names_codex`, `readme_names_claude_code` | The tool named in README prose, not as part of a file or model name (strict) |
| `readme_mentions_codex`, `readme_mentions_claude` | The word anywhere in the raw README (broad) |

### Tracks

| Code | Track | Partner |
|---|---|---|
| 01 | Energy | Samruk-Kazyna |
| 02 | Finance | Freedom |
| 03 | Management | Halyk Bank |
| 04 | Telecom | Beeline |
| 05 | Logistics | ekt.kz |
| 06 | Creative industries | Firebird |
| 07 | Education | AI Sana |
| 08 | Innovation | Samruk-Kazyna |
| 09 | Communications | Halyk Bank |
| 10 | Trade | ekt.kz |
| 11 | Special (structure) | Kazakhtelecom |
| 12 | Special (city) | Astana Innovations |

## Columns of `commits.csv`

One row per team commit (all branches, counted once, template commit excluded).

| Column | Meaning |
|---|---|
| `id` | Repository identifier, as in `repositories.csv` |
| `minutes_from_start`, `author_minutes_from_start` | Committer time and author time, in minutes from 13:00 UTC+5 on 23 September 2026 (negative before the event) |
| `in_window` | Committer time between 13:00 and 18:00 (1/0) |
| `is_merge` | More than one parent (1/0) |
| `files`, `added`, `deleted` | Files changed, lines added and lines deleted |
| `code_lines` | Lines added plus deleted outside lock files (`package-lock.json`, `yarn.lock`, `poetry.lock`, `go.sum` and similar), data and media files (`.csv`, `.jsonl`, `.xlsx`, `.pdf`, images, audio, video, `.ipynb`, `.zip`), minified or map files, and vendored or build folders (`node_modules`, `dist`, `build`, `.next`, `vendor`, `venv`) |
| `conventional` | Subject starts with a conventional-commit type such as `feat:` or `fix(scope):` (1/0) |
| `subject_script` | Script of the subject's letters: `kazakh` (Kazakh-specific letters, and Cyrillic at least as common as Latin), `cyrillic` (more Cyrillic than Latin), `latin`, or `none` (no letters) |
| `agent_kind` | Agent named by a signature or by an author named after the tool: `claude`, `codex`, `cursor`, `copilot`, `devin`, or `bot` for a generic bot account that is not an agent; empty otherwise |
| `agent_name_only` | The only trace is an author or committer named exactly after the tool (1/0) |
| `author` | Author as an ordinal within the repository (1, 2, …), from a salted hash |
| `author_is_bot` | Author is a bot account (1/0) |

The paper (Section 3, "Data collection and definitions" and "Measures") gives the exact definitions. Its code is in `src/` and `arxiv_paper_all/analysis/`.

## Privacy and ethics

- No names, e-mail addresses, commit SHAs next to features, commit messages or README text.
- Authors appear only as an ordinal within one repository, derived from a salted hash whose salt was never saved.
- **Credentials:** no secret value, no per-repository credential flag and no committed-`.env` flag are released. Credential results are aggregates only.
- **Pseudonymisation, not anonymisation:** the identifiers are random, but the source repositories are public, so a determined reader could match rows to repositories through their features. Please do not try to identify individuals or teams.
- **Removal:** to request that a repository be removed from a future version, contact the author.

## Reproducing the paper

`python arxiv_paper_all/analysis/reproduce_public.py` recomputes the headline numbers on participation, work timing, agent traces, README naming and artefacts from these files alone and compares them with the paper (42 of 42 match in this release). The full pipeline, which needs the clones, is `src/` followed by `arxiv_paper_all/analysis/run_analysis.py`. The figures are drawn by `arxiv_paper_all/figure_code/make_figures.py` from the paper's facts file and the tables in `aggregates/`, not from the record-level files.

Some numbers in the paper cannot be recomputed from these files:

- credential results (released as aggregates only);
- creation and archive times finer than a day, so the batch creation rate and the archive bursts;
- the validation checks against the GitHub API, the separate recount and the template audit (Table 2), apart from the window shifts and author time;
- the README-language validation sample and its labels;
- the similarity of dependency sets between solutions (full dependency lists are not released; `frameworks` and `llm_sdks` hold the main ones).

## Known limitations

- A repository stands for a registration, not a person.
- Features are measured at the final state.
- Agent traces are partial.
- The README language rule is a letter heuristic.
- Track labels were checked by one person.

The paper's threats-to-validity section covers each of these.
