# Claim ledger

Every factual claim in the paper, with its evidence. A claim without a row here does not go into the paper.
Status: `ok` = evidence checked; `todo` = evidence still needed; `pending` = waiting on an outside event.

| # | Claim (as worded in the paper) | Evidence | Status |
|---|---|---|---|
| 1 | The event took place in Astana on 23 September 2026, in person | hackalem.ai (accessed 2026-09-24) | ok |
| 2 | Teams had up to three members; solo entry was allowed | hackalem.ai FAQ | ok |
| 3 | Codex use was required during development | hackalem.ai rules | ok |
| 4 | 2,500 seats; 6,586 applications | hackalem.ai (seats); Qumash.kz and Ulys Media (applications) | ok |
| 5 | Participants from 21 countries | Kazinform; The Astana Times | ok |
| 6 | Organised as an official Guinness World Records attempt (most participants in an agentic AI hackathon); previous record 2,089 (India, Dec 2025); result pending | The Astana Times | pending |
| 7 | 12 tracks: 10 sector tracks and 2 special tracks, with the partners listed in Table 2 | Author's track table; partner names confirmed in team READMEs; track numbers cited in READMEs (Trade = 10 by elimination) | ok |
| 8 | Coding window 13:00–18:00 local time | Commit and archive timestamps; press reports of five hours | todo: official source |
| 9 | 3,649 team repositories; all archived after the event | GitHub API (repos.csv), rechecked live 2026-09-24 | ok |
| 10 | 2,395 repositories (65.6%) have no team commits | Rebuilt from clones (data/repo_table.csv); matches published value; see analysis/validation_m1.md | ok |
| 11 | 1,057 repositories have team commits in the event window | Rebuilt from clones; matches published value (validation_m1.md) | ok |
| 12 | 984 active repositories matched to a track; 73 unclear; 7 labels corrected by hand | facts.json, CASE_FIXES in src/plot_bilingual_charts.py | todo: double-coding |
| 13 | 16 early test repositories had their template commit made by a second organiser account | Live GitHub audit of 402 repos (data/verification/template_check.json) | ok |
| 14 | 3,201 repositories were archived between 18:01 and 18:51 | repos.csv updated_at | ok (infer "archived" from updated_at; state this) |
| 15 | Winners announced on 1 October 2026 at Digital Bridge | hackalem.ai timeline | pending |
| 16 | Clone and GitHub API default-branch commit counts agree for all repositories | validation_m1.md (3,649/3,649) | ok |
| 17 | More than 2,500 participants from 21 countries and 129 universities took part | The Astana Times (re-read 2026-09-27, verbatim) | ok |
| 18 | Jury review of submitted projects 24–28 Sep; finalists present and winners are announced at Demo Day on 29 Sep; awards on 1 Oct at Digital Bridge | hackalem.ai timeline (read 2026-09-27) | ok |
| 19 | 446 repositories were archived before the event, in bulk operations on 15, 17 and 22 Sep | repos.csv updated_at (GitHub API, 24 Sep); run_analysis.py rq1.prearchived | ok (inferred from updated_at; stated as such) |
| 20 | Core counts reproduced by independent code for all repositories | checks/recompute_core.py → recompute_core_result.json | ok |
| 21 | The organisers were informed privately by e-mail on 28 September 2026 | Sent e-mail to team@baitc.org (contact on hackalem.ai), saved as .eml in data/secrets_private/ | ok |
| 22 | `AGENTS.md` is an open format read by many agents (Codex, Cursor, Copilot's coding agent, Gemini CLI and others) | agents.md (read 2026-09-28) | ok |
| 23 | Current versions of Claude Code read `AGENTS.md` when a repository has no `CLAUDE.md` | code.claude.com/docs/en/memory, section "AGENTS.md" (read 2026-09-28; needs v2.1.277 or later) | ok ("current versions"; version at the event unknown) |
| 24 | GitHub reports partner-format secrets in public repositories to the provider, which decides whether to revoke; OpenAI API keys are covered by partner alerts and push protection | GitHub Docs: about secret scanning for partners; supported patterns table, OpenAI row (read 2026-09-28) | ok |
| 25 | Push protection for users is on by default for pushes to public repositories and can be bypassed; repository/organisation push protection is off by default | GitHub Docs: push protection (read 2026-09-28) | ok |
| 26 | Language models still lag on Kazakh benchmarks behind high-resource languages | KazMMLU abstract: "significant performance gaps compared to high-resource languages" (read 2026-09-28) | ok |
| 27 | Which Codex interface leaves which trace is not documented in the sources we read | Codex docs (cloud, AGENTS.md pages) read 2026-09-28; branch prefixes appear only in issues and forum posts | ok (stated as not documented) |
