"""Phase 5a: Fetch README text for every repo via raw.githubusercontent.com.

No cloning needed — a plain HTTP GET per repo against the raw content CDN.
Tries `main` then `master` branch, and a couple of common filename variants.
"""
from __future__ import annotations

import csv
from pathlib import Path

import requests
from tqdm import tqdm

from github_client import GITHUB_ORG

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPOS_FILE = DATA_DIR / "repos.csv"
README_DIR = DATA_DIR / "readmes"
FAILURES_FILE = DATA_DIR / "readme_failures.csv"

RAW_BASE = "https://raw.githubusercontent.com"
FILENAME_CANDIDATES = ["README.md", "readme.md", "Readme.md", "README.MD"]

_session = requests.Session()
_session.headers.update({"User-Agent": "hackalemai-datamining/1.0"})


def load_repos() -> list[dict]:
    with REPOS_FILE.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fetch_readme(name: str, default_branch: str) -> str | None:
    branches = [default_branch] if default_branch else []
    for b in ("main", "master"):
        if b not in branches:
            branches.append(b)
    for branch in branches:
        for filename in FILENAME_CANDIDATES:
            url = f"{RAW_BASE}/{GITHUB_ORG}/{name}/{branch}/{filename}"
            try:
                resp = _session.get(url, timeout=15)
            except requests.RequestException:
                continue
            if resp.status_code == 200 and resp.text.strip():
                return resp.text
    return None


def main() -> None:
    README_DIR.mkdir(parents=True, exist_ok=True)
    repos = load_repos()

    already = {p.stem for p in README_DIR.glob("*.md")}
    failures = []
    fetched = 0

    for repo in tqdm(repos, desc="Fetching READMEs", unit="repo"):
        name = repo["name"]
        if name in already:
            fetched += 1
            continue
        text = fetch_readme(name, repo.get("default_branch") or "main")
        if text is None:
            failures.append({"name": name})
            continue
        (README_DIR / f"{name}.md").write_text(text, encoding="utf-8")
        fetched += 1

    with FAILURES_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name"])
        writer.writeheader()
        writer.writerows(failures)

    print(f"Fetched {fetched}/{len(repos)} READMEs, {len(failures)} failures -> {README_DIR}")


if __name__ == "__main__":
    main()
