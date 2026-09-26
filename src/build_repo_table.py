"""Phase M1b: Rebuild the per-repo table from the mirror clones -> data/repo_table.csv

Replaces data/hackalem_repos_analysis.csv, whose generating script is not in
this repo. Everything here is computed from git history:

- team commits: commits reachable from any branch (refs/heads/*), deduplicated
  by SHA, excluding the organisers' template commit. Commits reachable only from
  pull-request refs are counted separately (pr_only_commits).
- template commit: a root commit titled "Initial commit" that changes one file
  with 2 added and 0 deleted lines, committed within 2 minutes of the repo's
  creation. The rule ignores which account made it (two organiser accounts did).
- event window: 13:00-18:00 local time (UTC+5) on 23 September 2026, using the
  committer timestamp (as in the timeline chart); author-time counts are kept
  for a sensitivity check.
- authors: distinct author emails are counted in memory only; emails and names
  are never written to disk.
"""
from __future__ import annotations

import csv
import subprocess
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tqdm import tqdm

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPOS_FILE = DATA_DIR / "repos.csv"
CLONE_DIR = DATA_DIR / "clones"
OUT_FILE = DATA_DIR / "repo_table.csv"

ASTANA = timezone(timedelta(hours=5))
WINDOW_START = datetime(2026, 9, 23, 13, 0, tzinfo=ASTANA).timestamp()
WINDOW_END = datetime(2026, 9, 23, 18, 0, tzinfo=ASTANA).timestamp()
TEMPLATE_MAX_DELAY_S = 120
SEP = "\x1f"

FIELDS = [
    "repo", "created_at", "branches", "all_commits", "template_found", "team_commits",
    "pr_only_commits", "window_commits", "window_commits_author_time", "hours_active",
    "first_team_commit", "last_team_commit", "team_authors",
]


def git(git_dir: Path, *args: str) -> str:
    return subprocess.run(
        ["git", f"--git-dir={git_dir}", *args], capture_output=True, text=True, check=True,
        encoding="utf-8", errors="replace",
    ).stdout


def parse_log(text: str) -> dict[str, dict]:
    """Parse `git log --numstat` output written with our record format."""
    commits: dict[str, dict] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("@@"):
            sha, parents, ctime, atime, email, subject = line[2:].split(SEP, 5)
            current = {"parents": parents.split(), "ctime": int(ctime), "atime": int(atime),
                       "email": email.lower(), "subject": subject, "files": 0, "added": 0,
                       "deleted": 0}
            commits[sha] = current
        elif line.strip() and current is not None:
            added, deleted, _path = line.split("\t", 2)
            current["files"] += 1
            current["added"] += int(added) if added.isdigit() else 0
            current["deleted"] += int(deleted) if deleted.isdigit() else 0
    return commits


def is_template(commit: dict, created_ts: float) -> bool:
    return (not commit["parents"] and commit["subject"] == "Initial commit"
            and commit["files"] == 1 and commit["added"] == 2 and commit["deleted"] == 0
            and abs(commit["ctime"] - created_ts) <= TEMPLATE_MAX_DELAY_S)


def local_iso(ts: int | None) -> str:
    return datetime.fromtimestamp(ts, ASTANA).isoformat() if ts else ""


def process(args: tuple[str, str]) -> dict | None:
    name, created_at = args
    git_dir = CLONE_DIR / f"{name}.git"
    if not (git_dir / "CLONE_OK").exists():
        return None
    created_ts = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
    fmt = f"--format=@@%H{SEP}%P{SEP}%ct{SEP}%at{SEP}%ae{SEP}%s"
    branch_commits = parse_log(git(git_dir, "log", "--branches", "--numstat", fmt))
    all_shas = set(git(git_dir, "rev-list", "--all").split())
    branches = len(git(git_dir, "for-each-ref", "--format=%(refname)", "refs/heads").split())

    template = [s for s, c in branch_commits.items() if is_template(c, created_ts)]
    team = {s: c for s, c in branch_commits.items() if s not in template}
    in_window = [c for c in team.values() if WINDOW_START <= c["ctime"] < WINDOW_END]
    in_window_author = [c for c in team.values() if WINDOW_START <= c["atime"] < WINDOW_END]
    hours = {datetime.fromtimestamp(c["ctime"], ASTANA).hour for c in in_window}
    times = [c["ctime"] for c in team.values()]
    return {
        "repo": name,
        "created_at": created_at,
        "branches": branches,
        "all_commits": len(all_shas),
        "template_found": int(bool(template)),
        "team_commits": len(team),
        "pr_only_commits": len(all_shas - set(branch_commits)),
        "window_commits": len(in_window),
        "window_commits_author_time": len(in_window_author),
        "hours_active": len(hours),
        "first_team_commit": local_iso(min(times)) if times else "",
        "last_team_commit": local_iso(max(times)) if times else "",
        "team_authors": len({c["email"] for c in team.values()}),
    }


def main() -> None:
    with REPOS_FILE.open(encoding="utf-8") as f:
        repos = [(r["name"], r["created_at"]) for r in csv.DictReader(f)]
    rows, missing = [], []
    with ProcessPoolExecutor() as pool:
        for (name, _), row in tqdm(zip(repos, pool.map(process, repos, chunksize=16)),
                                   total=len(repos), desc="Rebuilding", unit="repo"):
            (rows.append(row) if row else missing.append(name))
    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} repos -> {OUT_FILE}; {len(missing)} without a finished clone")


if __name__ == "__main__":
    main()
