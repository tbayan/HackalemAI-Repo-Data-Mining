"""Phase M2b: Commit-level features and agent signatures -> data/commits.csv, data/commit_repo_features.csv

For every team commit (all branches, template commit excluded; same rules as
build_repo_table.py) we record timing, size and message features, plus agent
signatures: co-author trailers or "Generated with" markers that name a coding
agent, and agent/bot author accounts. Author names and emails are only matched
against agent patterns in memory; they are never written out. Commit messages
are reduced to features (length, conventional prefix, script); the text itself
is not stored.

Branch names are checked for agent prefixes (e.g. codex/..., claude/...), which
some agents use when they open branches on their own.
"""
from __future__ import annotations

import csv
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from build_repo_table import ASTANA, WINDOW_END, WINDOW_START, is_template

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLONE_DIR = DATA_DIR / "clones"
TABLE = DATA_DIR / "repo_table.csv"
COMMITS_OUT = DATA_DIR / "commits.csv"
REPO_OUT = DATA_DIR / "commit_repo_features.csv"

AGENTS = r"codex|openai|chatgpt|claude|anthropic|copilot|cursor|gemini|devin|aider|windsurf|cline|jules|lovable|bolt"
AGENT_TOKEN = re.compile(rf"\b({AGENTS})\b", re.I)
TRAILER = re.compile(r"^co-authored-by:(.*)$", re.I | re.M)
GENERATED = re.compile(rf"generated (with|by)[^\n]*\b({AGENTS})\b", re.I)
BOT_ACCOUNT = re.compile(r"\[bot\]|noreply@anthropic\.com|@openai\.com|cursoragent|copilot", re.I)
AGENT_BRANCH = re.compile(rf"^({AGENTS})[/_-]", re.I)
CONVENTIONAL = re.compile(r"^(feat|fix|chore|docs|refactor|test|tests|style|perf|ci|build|revert)(\([^)]*\))?!?:", re.I)
KAZAKH = re.compile(r"[әғқңөұүһіӘҒҚҢӨҰҮҺІ]")
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
LATIN = re.compile(r"[A-Za-z]")
RS, US = "\x1e", "\x1f"

COMMIT_FIELDS = ["repo", "ctime", "atime", "in_window", "is_merge", "files", "added", "deleted",
                 "subject_chars", "body_lines", "conventional", "script", "agent_trailer",
                 "agent_generated_marker", "agent_account", "agent_kind"]


def git(git_dir: Path, *args: str) -> str:
    return subprocess.run(["git", f"--git-dir={git_dir}", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def script_of(text: str) -> str:
    kz, cy, la = len(KAZAKH.findall(text)), len(CYRILLIC.findall(text)), len(LATIN.findall(text))
    if kz and kz + cy >= la:
        return "kazakh"
    if cy + kz > la:
        return "cyrillic"
    return "latin" if la else "none"


def agent_kind(text: str) -> str:
    m = AGENT_TOKEN.search(text)
    if not m:
        return ""
    token = m.group(1).lower()
    return {"openai": "codex", "chatgpt": "codex", "anthropic": "claude"}.get(token, token)


def process(args: tuple[str, str]) -> tuple[list[dict], dict]:
    name, created_at = args
    git_dir = CLONE_DIR / f"{name}.git"
    created_ts = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()

    stats: dict[str, dict] = {}
    current = None
    for line in git(git_dir, "log", "--branches", "--numstat", "--format=@@%H").splitlines():
        if line.startswith("@@"):
            current = stats.setdefault(line[2:], {"files": 0, "added": 0, "deleted": 0})
        elif line.strip() and current is not None:
            a, d, _ = line.split("\t", 2)
            current["files"] += 1
            current["added"] += int(a) if a.isdigit() else 0
            current["deleted"] += int(d) if d.isdigit() else 0

    fmt = f"--format=%H{US}%P{US}%ct{US}%at{US}%an <%ae>{US}%cn <%ce>{US}%B{RS}"
    commits = []
    for record in git(git_dir, "log", "--branches", fmt).split(RS):
        record = record.strip("\n")
        if not record:
            continue
        sha, parents, ctime, atime, author, committer, body = record.split(US, 6)
        st = stats.get(sha, {"files": 0, "added": 0, "deleted": 0})
        subject = body.split("\n", 1)[0]
        probe = {"parents": parents.split(), "subject": subject, "ctime": int(ctime), **st}
        if is_template(probe, created_ts):
            continue
        trailers = " ".join(TRAILER.findall(body))
        account_hit = bool(BOT_ACCOUNT.search(author) or BOT_ACCOUNT.search(committer)
                           or AGENT_TOKEN.search(author) or AGENT_TOKEN.search(committer))
        kind = agent_kind(trailers) or agent_kind(" ".join(GENERATED.findall(body) and [body]))
        if not kind and account_hit:
            kind = agent_kind(author + " " + committer) or "bot"
        commits.append({
            "repo": name, "ctime": int(ctime), "atime": int(atime),
            "in_window": int(WINDOW_START <= int(ctime) < WINDOW_END),
            "is_merge": int(len(parents.split()) > 1), **st,
            "subject_chars": len(subject), "body_lines": max(0, len(body.strip().splitlines()) - 1),
            "conventional": int(bool(CONVENTIONAL.match(subject))), "script": script_of(body),
            "agent_trailer": int(bool(AGENT_TOKEN.search(trailers))),
            "agent_generated_marker": int(bool(GENERATED.search(body))),
            "agent_account": int(account_hit), "agent_kind": kind,
        })

    branches = git(git_dir, "for-each-ref", "--format=%(refname:short)", "refs/heads").split()
    agent_branches = [b for b in branches if AGENT_BRANCH.match(b)]
    window = [c for c in commits if c["in_window"]]
    per_minute: dict[int, int] = {}
    for c in window:
        per_minute[c["ctime"] // 60] = per_minute.get(c["ctime"] // 60, 0) + 1
    repo_row = {
        "repo": name,
        "branches": len(branches),
        "agent_branches": len(agent_branches),
        "agent_branch_kinds": ";".join(sorted({agent_kind(b) for b in agent_branches})),
        "pr_refs": len(git(git_dir, "for-each-ref", "--format=%(refname)", "refs/pull").split()),
        "team_commits": len(commits),
        "merges": sum(c["is_merge"] for c in commits),
        "agent_signed_commits": sum(bool(c["agent_trailer"] or c["agent_generated_marker"] or c["agent_account"]) for c in commits),
        "agent_kinds": ";".join(sorted({c["agent_kind"] for c in commits if c["agent_kind"]})),
        "conventional_share": round(sum(c["conventional"] for c in commits) / len(commits), 4) if commits else 0,
        "max_commits_per_minute": max(per_minute.values(), default=0),
        "median_lines_changed": sorted(c["added"] + c["deleted"] for c in commits)[len(commits) // 2] if commits else 0,
    }
    return commits, repo_row


def main() -> None:
    with TABLE.open(encoding="utf-8") as f:
        repos = [(r["repo"], r["created_at"]) for r in csv.DictReader(f) if int(r["team_commits"]) > 0]
    all_commits, repo_rows = [], []
    with ProcessPoolExecutor() as pool:
        for commits, row in tqdm(pool.map(process, repos, chunksize=8), total=len(repos), desc="Commits", unit="repo"):
            all_commits.extend(commits)
            repo_rows.append(row)
    for path, rows, fields in ((COMMITS_OUT, all_commits, COMMIT_FIELDS), (REPO_OUT, repo_rows, list(repo_rows[0]))):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {len(all_commits)} commits -> {COMMITS_OUT}; {len(repo_rows)} repos -> {REPO_OUT}")


if __name__ == "__main__":
    main()
