"""Phase 2: Batched GraphQL commit counts per repo -> data/commit_counts.csv

Batches many repos into a single GraphQL query (one alias per repo) so we
only spend a handful of API requests for thousands of repos. Auto-halves the
batch size and retries on GraphQL errors (timeouts / complexity limits), and
supports resuming from a partially-written output file.
"""
from __future__ import annotations

import csv
from pathlib import Path

from tqdm import tqdm

from github_client import GITHUB_ORG, GraphQLError, graphql_request

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPOS_FILE = DATA_DIR / "repos.csv"
OUT_FILE = DATA_DIR / "commit_counts.csv"

FIELDS = ["name", "commit_count", "has_default_branch"]

INITIAL_BATCH_SIZE = 50
MIN_BATCH_SIZE = 5


def load_repo_names() -> list[str]:
    with REPOS_FILE.open(encoding="utf-8") as f:
        return [row["name"] for row in csv.DictReader(f)]


def load_done_names() -> set[str]:
    if not OUT_FILE.exists():
        return set()
    with OUT_FILE.open(encoding="utf-8") as f:
        return {row["name"] for row in csv.DictReader(f)}


def build_query(names: list[str]) -> str:
    parts = []
    for i, name in enumerate(names):
        safe_name = name.replace('"', '\\"')
        parts.append(
            f'r{i}: repository(owner: "{GITHUB_ORG}", name: "{safe_name}") {{'
            f"    name"
            f"    defaultBranchRef {{"
            f"      target {{"
            f"        ... on Commit {{"
            f"          history {{ totalCount }}"
            f"        }}"
            f"      }}"
            f"    }}"
            f"  }}"
        )
    return "query {\n" + "\n".join(parts) + "\n}"


def fetch_batch(names: list[str]) -> list[dict]:
    """Fetch commit counts for a batch, recursively halving on failure."""
    if not names:
        return []
    try:
        data = graphql_request(build_query(names))
    except (GraphQLError, Exception) as exc:  # noqa: BLE001 - broad on purpose
        if len(names) <= MIN_BATCH_SIZE:
            print(f"[warn] giving up on {names} after min-batch failure: {exc}")
            return [
                {"name": n, "commit_count": -1, "has_default_branch": False}
                for n in names
            ]
        mid = len(names) // 2
        print(f"[retry] batch of {len(names)} failed ({exc}); splitting")
        return fetch_batch(names[:mid]) + fetch_batch(names[mid:])

    results = []
    for i, name in enumerate(names):
        repo_data = data.get(f"r{i}")
        if not repo_data:
            results.append(
                {"name": name, "commit_count": -1, "has_default_branch": False}
            )
            continue
        branch_ref = repo_data.get("defaultBranchRef")
        if not branch_ref or not branch_ref.get("target"):
            results.append(
                {"name": name, "commit_count": 0, "has_default_branch": False}
            )
            continue
        history = branch_ref["target"].get("history") or {}
        results.append(
            {
                "name": name,
                "commit_count": history.get("totalCount", 0),
                "has_default_branch": True,
            }
        )
    return results


def main() -> None:
    all_names = load_repo_names()
    done = load_done_names()
    pending = [n for n in all_names if n not in done]
    print(f"{len(done)} already done, {len(pending)} remaining")

    file_exists = OUT_FILE.exists()
    with OUT_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()

        batch_size = INITIAL_BATCH_SIZE
        i = 0
        with tqdm(total=len(pending), desc="Fetching commit counts", unit="repo") as pbar:
            while i < len(pending):
                batch = pending[i : i + batch_size]
                results = fetch_batch(batch)
                writer.writerows(results)
                f.flush()
                pbar.update(len(batch))
                i += len(batch)

    print(f"Done -> {OUT_FILE}")


if __name__ == "__main__":
    main()
