# M1 validation: rebuilding the per-repository table from git (2026-09-24)

## What was done
- Mirror-cloned all 3,649 organisation repositories (`src/clone_repos.py`): 3,649 succeeded, 0 failed, 9.6 GB.
- Rebuilt every per-repository metric from git history (`src/build_repo_table.py` → `data/repo_table.csv`), replacing the earlier table whose generating script was not available.

## Checks and results

| Check | Result |
|---|---|
| Default-branch commit count, clone vs. GitHub API (`commit_counts.csv`, collected separately) | 3,649 / 3,649 identical |
| Repositories with no team commits | 2,395 (same as published) |
| Repositories with at least one team commit | 1,254 (same) |
| Repositories with team commits in the event window | 1,057 (same) |
| Repositories with commits only outside the window | 197 (same) |
| Template commit detected by the account-independent rule | 3,615 / 3,649 repositories (the other 34 rewrote their history) |
| Per-repo team commits, rebuilt vs. earlier table (after the 16 template fixes) | 3,641 / 3,649 equal |
| Per-repo event-window commits | 3,644 / 3,649 equal |
| Per-repo hours with commits | 3,648 / 3,649 equal |

## The remaining differences, explained
- **8 repositories differ in team commits.** For all 8, our clone's default-branch count equals the GitHub API count, so the clones reflect GitHub's final state.
  - Two differences come from commits reachable only through pull-request refs, which the earlier table counted. We count branches only and report PR-only commits separately (117 repositories have any).
  - For the other six, merge commits and late pushes do not explain the gap: all eight made their last push before 18:00. The earlier table's method is undocumented, so we treat the rebuilt values as authoritative.
- **Effect on reported figures:**
  - Event-window commits on all branches become 30,418 (published: 30,417).
  - One repository moves from 1 to 4 active hours, so the distribution is 41 / 46 / 132 / 368 / 470 (published: 42 / 46 / 132 / 367 / 470).
  - Teams active in at least four hours become 838 (79.3%; published 837, 79.2%).
  - All other headline numbers are unchanged.
- **Author counts differ by ±1 in 300 repositories.** We count distinct author emails (lower-cased); the earlier table probably used another identity key. Author counts are not used as a team-size measure in the paper: one person can commit under several emails, and teams had at most three members.

## Consequence for the paper
All paper numbers are computed from `data/repo_table.csv`. `data/hackalem_repos_analysis.csv` is kept only for the track labels (`case_guess`) and as the reference this validation compares against.
