# Analysis plan (written before running M3 statistics, 2026-09-24)

Descriptive numbers from M1/M2 were inspected while building and validating the extractors (see `validation_m1.md`); the tests below were fixed before any comparison was run. Anything added later is marked *exploratory* in the paper.

## Data
- `data/repo_table.csv`: all 3,649 repositories (M1).
- `data/stack.csv`, `data/commits.csv`, `data/commit_repo_features.csv`, `data/readme_features.csv`: the 1,254 repositories with team commits (M2).
- `data/secrets_private/findings.csv`: secret-scan findings (M2c). Reported in aggregate only.
- Track labels: `case_guess` in `data/hackalem_repos_analysis.csv` with the seven corrections (CASE_FIXES).
- **Active** = at least one team commit in the event window (n = 1,057). Most comparisons use active repositories.

## General rules
- Report counts with percentages and 95% confidence intervals: Wilson intervals for proportions, bootstrap (10,000 resamples, fixed seed) for medians.
- Group comparisons use Mann–Whitney U for continuous measures, with Cliff's δ as the effect size, and χ² tests for proportions, with Cramér's V.
- Where several tests answer one question, p-values are Holm-corrected.
- No inferential claims about individuals. Everything is per repository.

## RQ1 Participation
- **Funnel:** repositories → any team commit → active → matched to a track (counts, %).
- **Registration timing vs. activity:**
  - Share of repositories that became active, by creation date group: before 1 Sep, 1–14 Sep, 15–21 Sep, 22 Sep (the day before), 23 Sep.
  - Test: χ² test across groups, then a logistic regression of active (0/1) on log days-before-event (odds ratio with CI).
  - Caveat: repository creation date is a proxy for registration date.
- **Repeated team names:** number of names on more than one repository, and the share of those groups where only one repository is active.

## RQ2 Work rhythm
- Commits per 10 minutes (main branches, as in the published timeline) and per hour (all branches).
- **Time to first and last team commit** (minutes after 13:00), for active repositories: medians with bootstrap CIs.
- **Deadline share:** fraction of each team's event-window commits made in 17:00–18:00. Report the distribution.
- **Rhythm archetypes:**
  - Each active repository's hourly commit counts are normalised to shares.
  - k-means with k = 2..6 on those profiles; k is chosen by silhouette score, with seed 42.
  - Report cluster sizes and centroids. Clusters are described, not over-interpreted.
- **Post-deadline commits:** event-day commits between 18:00 and the archive time (counts only).

## RQ3 Technology choices
- Prevalence among active repositories (Wilson CIs) of:
  - primary language,
  - frameworks with at least 20 repositories,
  - LLM SDKs (manifest or import),
  - Docker, tests, CI and deployment configs.
- By track: χ² test of primary language (Python / TypeScript / JavaScript / other) × track, and Cramér's V.

## RQ4 AI-agent footprint
- **Prevalence** of agent context files (AGENTS.md, CLAUDE.md, others), agent-signed commits (trailer, marker, account), agent-named branches, and PR refs.
- **Measurement note:**
  - Signatures reflect each tool's disclosure defaults: Claude Code adds co-author trailers by default; Codex does not.
  - So we report signatures per tool, and never as a share of use.
- **Association with activity:**
  - Compare repositories with and without an AGENTS.md on window commits, hours active, and tests present.
  - Tests: Mann–Whitney / χ², Holm-corrected across the three outcomes.
  - This is observational, so the paper states association only.
- **Commit size:** distribution of lines changed per commit (median, IQR), for agent-signed vs. other commits. *Exploratory.*

## RQ5 Documentation
- **README language** (kazakh / russian / english / mixed / template-only), with the rule's accuracy reported from the hand-labelled sample.
- **Commit-message script** (Latin / Cyrillic / Kazakh).
- **Completeness:** run instructions, deployed link, images, word count (median, IQR).

## RQ6 Security hygiene
- **Findings by gitleaks rule**, grouped into provider-specific rules (e.g. OpenAI, Telegram, GitHub token) and generic rules.
  - Generic rules are reported separately, because their precision is low.
- **Repositories with at least one finding**, overall and provider-specific. Split each into "still present at the final state" vs. "only in history".
- **Hygiene flags:** committed `.env`, `.gitignore` covering `.env`, `.env.example` present, committed `node_modules` / virtualenv / `__pycache__`.
- **Association:** provider-specific findings in repositories with vs. without `.gitignore` covering `.env` (χ², Cramér's V). *Exploratory.*

## RQ7 Track choice
- **Track counts:** as published (after the corrections), plus 73 unclear.
- **Per track:** median window commits, share with tests, share with a deployed link, and README language. Descriptive only; there is no ranking claim.

## Outputs
Every number used in the paper goes to `analysis/facts_paper.json`; tables go to `tables/`; the figures read the same files.
