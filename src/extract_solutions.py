"""Per-solution features for comparing how teams solved the same brief -> data/solutions_private.jsonl

For every repository with team commits, from the default-branch HEAD of its mirror clone:
  deps      all dependency names from package manifests (normalised; as in extract_stack.py)
  paths     file paths outside vendored folders, lower case
  blobs     git object IDs of source-code files of at least MIN_BYTES (identical IDs = identical content)
  headings  README headings, lower case, without markup, emoji or numbering
Only names, IDs and headings are stored, never file contents. The output stays private (data/),
because paths and headings can identify a repository.
"""
from __future__ import annotations

import csv
import json
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import PurePosixPath

from tqdm import tqdm

from extract_stack import CLONE_DIR, DATA_DIR, TABLE, VENDORED, deps_from, git

OUT_FILE = DATA_DIR / "solutions_private.jsonl"
MIN_BYTES = 200
CODE = re.compile(r"\.(py|js|jsx|ts|tsx|mjs|cjs|go|java|kt|cs|php|rb|dart|vue|svelte)$", re.I)
GENERATED = re.compile(r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml)$|\.min\.(js|css)$|\.d\.ts$", re.I)
MANIFEST = re.compile(r"^(package\.json|pyproject\.toml|pipfile|go\.mod|requirements[^/]*\.txt)$", re.I)
README = re.compile(r"^readme(\.(md|markdown|txt|rst))?$", re.I)
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", re.M)
DEP_NAME = re.compile(r"^@?[a-z][a-z0-9._\-]*(/[a-z0-9._\-]+)?$")  # drops version strings such as "0.1.0" or "."


def clean_heading(text: str) -> str:
    text = re.sub(r"[*_`~\[\]()<>]|https?://\S+", " ", text.lower())
    text = re.sub(r"[^\w\s\-/+.&]", " ", text)             # emoji and symbols
    text = re.sub(r"^\s*(\d+[.)]?|[ivx]+\.)\s+", "", text)  # numbering
    return re.sub(r"\s+", " ", text).strip(" -.")


def process(name: str) -> dict:
    git_dir = CLONE_DIR / f"{name}.git"
    rows = []
    for line in git(git_dir, "ls-tree", "-r", "-l", "HEAD").splitlines():
        meta, path = line.split("\t", 1)
        _, kind, oid, size = meta.split()
        if kind == "blob" and not VENDORED.search(path):
            rows.append((path, oid, int(size) if size.isdigit() else 0))
    deps: set[str] = set()
    for path in [p for p, _, _ in rows if MANIFEST.match(PurePosixPath(p).name)][:30]:
        deps |= deps_from(git_dir, path)
    readme = next((p for p, _, _ in rows if README.match(p)), None)
    text = git(git_dir, "show", f"HEAD:{readme}")[:60_000] if readme else ""
    headings = sorted({h for h in (clean_heading(m) for m in HEADING.findall(text)) if len(h) >= 2})
    return {"repo": name, "deps": sorted(d for d in deps if DEP_NAME.match(d)),
            "paths": sorted({p.lower() for p, _, _ in rows}),
            "blobs": sorted({o for p, o, s in rows if CODE.search(p) and not GENERATED.search(p) and s >= MIN_BYTES}),
            "headings": headings}


def main() -> None:
    with TABLE.open(encoding="utf-8") as f:
        names = [r["repo"] for r in csv.DictReader(f) if int(r["team_commits"]) > 0]
    with ProcessPoolExecutor() as pool:
        rows = list(tqdm(pool.map(process, names, chunksize=8), total=len(names), desc="Solutions", unit="repo"))
    with OUT_FILE.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} repos -> {OUT_FILE}")


if __name__ == "__main__":
    main()
