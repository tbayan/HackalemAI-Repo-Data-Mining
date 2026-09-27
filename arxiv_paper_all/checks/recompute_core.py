"""Recount the core per-repository numbers from the mirror clones with code that shares nothing
with src/build_repo_table.py, and compare them with data/repo_table.csv.

Counted independently for each of the organisation's repositories:
  - team commits: commits reachable from any branch, deduplicated by SHA, minus the template commit;
  - window commits: team commits with committer time in 13:00-18:00 local time (UTC+5), 23 Sep 2026;
  - hours with commits: distinct clock hours (13..17) among window commits.
The template commit is found here from scratch: a parentless commit whose subject is exactly
"Initial commit", made within 120 seconds of the repository's creation, adding 2 lines and
deleting none in 1 file. Creation times come from the GitHub API listing (data/repos.csv).

Writes checks/recompute_core_result.json. Usage: python checks/recompute_core.py
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
DATA = PAPER.parent / "data"
OUT = Path(__file__).resolve().parent / "recompute_core_result.json"
T0 = datetime.fromisoformat("2026-09-23T13:00:00+05:00").timestamp()
T1 = datetime.fromisoformat("2026-09-23T18:00:00+05:00").timestamp()


def count(repo: str, created: float) -> dict:
    git_dir = DATA / "clones" / f"{repo}.git"
    out = subprocess.run(["git", f"--git-dir={git_dir}", "log", "--branches", "--format=%x00%H %P%x01%ct%x01%s",
                          "--shortstat"], capture_output=True, text=True, errors="replace").stdout
    seen, team, window, hours = set(), 0, 0, set()
    for block in out.split("\x00")[1:]:
        head, _, stat = block.partition("\n")
        ids, ct, subject = head.split("\x01", 2)
        sha, *parents = ids.split()
        if sha in seen:
            continue
        seen.add(sha)
        ct = int(ct)
        stat = " ".join(stat.split())
        template = (not parents and subject == "Initial commit" and abs(ct - created) <= 120
                    and stat.startswith("1 file changed, 2 insertions(+)") and "deletion" not in stat)
        if template:
            continue
        team += 1
        if T0 <= ct < T1:
            window += 1
            hours.add(int((ct - T0) // 3600))
    return {"repo": repo, "team_commits": team, "window_commits": window, "hours_active": len(hours)}


def main() -> int:
    created = {r["name"]: datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")).timestamp()
               for r in csv.DictReader((DATA / "repos.csv").open(encoding="utf-8"))}
    table = {r["repo"]: r for r in csv.DictReader((DATA / "repo_table.csv").open(encoding="utf-8"))}
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(lambda n: count(n, created[n]), sorted(created)))
    result = {"repos": len(rows)}
    for field in ("team_commits", "window_commits", "hours_active"):
        agree = sum(int(table[r["repo"]][field]) == r[field] for r in rows)
        result[f"{field}_agree"] = agree
        result[f"{field}_differ"] = [r["repo"] for r in rows if int(table[r["repo"]][field]) != r[field]][:20]
    result["active"] = sum(r["window_commits"] > 0 for r in rows)
    result["with_team_commits"] = sum(r["team_commits"] > 0 for r in rows)
    result["window_commits_total"] = sum(r["window_commits"] for r in rows)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print({k: v for k, v in result.items() if not k.endswith("_differ")})
    return 0 if all(result[f"{f}_agree"] == len(rows) for f in ("team_commits", "window_commits", "hours_active")) else 1


if __name__ == "__main__":
    sys.exit(main())
