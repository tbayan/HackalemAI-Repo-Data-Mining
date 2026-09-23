"""Phase 4: Commit timestamps for active repos -> data/commit_timestamps.csv

Only pulls timestamps for repos that actually have real work (commit_count > 1)
to keep API usage proportional to what matters. Caps at the first 300 commits
per repo (a single-day hackathon repo won't have more meaningful history than
that, and it keeps GraphQL query cost low).
"""
from __future__ import annotations

import csv
from pathlib import Path

from tqdm import tqdm

from github_client import GITHUB_ORG, GraphQLError, graphql_request

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COUNTS_FILE = DATA_DIR / "commit_counts.csv"
OUT_FILE = DATA_DIR / "commit_timestamps.csv"

FIELDS = ["name", "committed_at"]
MAX_COMMITS_PER_REPO = 300
PAGE_SIZE = 100


def load_active_repo_names() -> list[str]:
    with COUNTS_FILE.open(encoding="utf-8") as f:
        return [
            row["name"]
            for row in csv.DictReader(f)
            if int(row["commit_count"]) > 1
        ]


def load_done_names() -> set[str]:
    if not OUT_FILE.exists():
        return set()
    with OUT_FILE.open(encoding="utf-8") as f:
        return {row["name"] for row in csv.DictReader(f)}


QUERY = """
query($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: %d, after: $after) {
            pageInfo { hasNextPage endCursor }
            nodes { committedDate }
          }
        }
      }
    }
  }
}
""" % PAGE_SIZE


def fetch_timestamps_for_repo(name: str) -> list[str]:
    timestamps: list[str] = []
    after = None
    while len(timestamps) < MAX_COMMITS_PER_REPO:
        try:
            data = graphql_request(QUERY, {"owner": GITHUB_ORG, "name": name, "after": after})
        except GraphQLError as exc:
            print(f"[warn] {name}: {exc}")
            break
        branch_ref = data.get("repository", {}).get("defaultBranchRef")
        if not branch_ref or not branch_ref.get("target"):
            break
        history = branch_ref["target"]["history"]
        for node in history["nodes"]:
            timestamps.append(node["committedDate"])
        if not history["pageInfo"]["hasNextPage"]:
            break
        after = history["pageInfo"]["endCursor"]
    return timestamps[:MAX_COMMITS_PER_REPO]


def main() -> None:
    active_names = load_active_repo_names()
    done = load_done_names()
    pending = [n for n in active_names if n not in done]
    print(f"{len(active_names)} active repos total, {len(pending)} remaining")

    file_exists = OUT_FILE.exists()
    with OUT_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        for name in tqdm(pending, desc="Fetching commit timestamps", unit="repo"):
            timestamps = fetch_timestamps_for_repo(name)
            writer.writerows({"name": name, "committed_at": ts} for ts in timestamps)
            f.flush()

    print(f"Done -> {OUT_FILE}")


if __name__ == "__main__":
    main()
