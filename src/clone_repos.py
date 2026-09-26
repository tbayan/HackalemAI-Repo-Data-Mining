"""Phase M1a: Mirror-clone every repo in the org -> data/clones/<name>.git

Mirror clones keep all branches and full history, which the rebuilt per-repo
table (build_repo_table.py) and the secret scan need. All 3,649 repos are
cloned, not only active ones, so the rebuild does not depend on the older
per-repo table to decide what matters. Public repos: no token is sent.

Resumable: a clone counts as done once <name>.git/CLONE_OK exists. Failures
are retried with backoff and listed in data/clone_failures.csv.
"""
from __future__ import annotations

import csv
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from github_client import GITHUB_ORG

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPOS_FILE = DATA_DIR / "repos.csv"
CLONE_DIR = DATA_DIR / "clones"
FAILURES_FILE = DATA_DIR / "clone_failures.csv"

WORKERS = 8
ATTEMPTS = 3
TIMEOUT_S = 1800
GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def clone(name: str) -> tuple[str, str | None]:
    target = CLONE_DIR / f"{name}.git"
    if (target / "CLONE_OK").exists():
        return name, None
    url = f"https://github.com/{GITHUB_ORG}/{name}.git"
    error = None
    for attempt in range(ATTEMPTS):
        shutil.rmtree(target, ignore_errors=True)
        try:
            result = subprocess.run(
                ["git", "clone", "--mirror", "--quiet", url, str(target)],
                env=GIT_ENV, capture_output=True, text=True, timeout=TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            error = "timeout"
        else:
            if result.returncode == 0:
                (target / "CLONE_OK").write_text(time.strftime("%Y-%m-%dT%H:%M:%S%z") + "\n")
                return name, None
            error = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "git error"
        time.sleep(5 * 2**attempt)
    shutil.rmtree(target, ignore_errors=True)
    return name, error


def main() -> None:
    CLONE_DIR.mkdir(parents=True, exist_ok=True)
    with REPOS_FILE.open(encoding="utf-8") as f:
        names = [row["name"] for row in csv.DictReader(f)]
    pending = [n for n in names if not (CLONE_DIR / f"{n}.git" / "CLONE_OK").exists()]
    print(f"{len(names) - len(pending)} already cloned, {len(pending)} to go")

    failures = []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(clone, n) for n in pending]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Cloning", unit="repo"):
            name, error = future.result()
            if error:
                failures.append({"name": name, "error": error})

    with FAILURES_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "error"])
        writer.writeheader()
        writer.writerows(failures)
    done = sum((CLONE_DIR / f"{n}.git" / "CLONE_OK").exists() for n in names)
    print(f"Cloned {done}/{len(names)}; {len(failures)} failures -> {FAILURES_FILE}")


if __name__ == "__main__":
    main()
