"""Phase 1: List every repo under the org -> data/repos.csv

This is the ground truth for "how many teams registered" since the org
auto-assigns exactly one repo per team.
"""
from __future__ import annotations

import csv
from pathlib import Path

from tqdm import tqdm

from github_client import GITHUB_ORG, rest_get_paginated

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_FILE = DATA_DIR / "repos.csv"

FIELDS = [
    "name",
    "full_name",
    "default_branch",
    "created_at",
    "pushed_at",
    "updated_at",
    "archived",
    "fork",
    "size",
    "html_url",
]


def fetch_all_repos() -> list[dict]:
    repos = []
    for repo in tqdm(
        rest_get_paginated(f"/orgs/{GITHUB_ORG}/repos", params={"type": "all"}),
        desc="Listing repos",
        unit="repo",
    ):
        repos.append({field: repo.get(field) for field in FIELDS})
    return repos


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    repos = fetch_all_repos()
    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(repos)
    print(f"Saved {len(repos)} repos -> {OUT_FILE}")


if __name__ == "__main__":
    main()
