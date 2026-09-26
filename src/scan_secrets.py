"""Phase M2c: Scan every active repo's full history for secret-like strings -> data/secrets_private/

Uses gitleaks (tools/gitleaks/gitleaks, v8.30.1, checksum-verified) over all
refs of each mirror clone, including pull-request refs, which are also public.

Ethics:
- Output is redacted by gitleaks; we additionally drop the Secret, Match,
  Author and Email fields before writing anything.
- Nothing is tested against live services. A finding means "a string matching
  a secret pattern", not "a working key".
- The per-repository file (findings.csv) is private: it exists only so the
  organisers can be told which repositories to check. The paper reports
  aggregates only.

For repos with findings, the default-branch HEAD is exported and scanned again
to tell whether each finding is still present at the final state (in_head).
"""
from __future__ import annotations

import csv
import json
import subprocess
import tarfile
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CLONE_DIR = DATA_DIR / "clones"
TABLE = DATA_DIR / "repo_table.csv"
OUT_DIR = DATA_DIR / "secrets_private"
GITLEAKS = ROOT / "tools" / "gitleaks" / "gitleaks"
TIMEOUT_S = 900
KEEP = ["RuleID", "File", "Commit", "Date", "Entropy", "StartLine"]


def run_gitleaks(args: list[str], report: Path) -> list[dict]:
    subprocess.run([str(GITLEAKS), *args, "--redact", "--no-banner", "--report-format", "json",
                    "--report-path", str(report), "--exit-code", "0", "--log-level", "error"],
                   capture_output=True, timeout=TIMEOUT_S)
    if not report.exists():
        return []
    findings = json.loads(report.read_text() or "[]")
    return [{k: f.get(k) for k in KEEP} for f in findings]


def scan(name: str) -> tuple[str, list[dict], str | None]:
    git_dir = CLONE_DIR / f"{name}.git"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        try:
            history = run_gitleaks(["git", str(git_dir), "--log-opts=--all"], tmp / "history.json")
        except subprocess.TimeoutExpired:
            return name, [], "timeout"
        if history:
            export = tmp / "head"
            export.mkdir()
            archive = subprocess.run(["git", f"--git-dir={git_dir}", "archive", "HEAD"], capture_output=True)
            tar_path = tmp / "head.tar"
            tar_path.write_bytes(archive.stdout)
            with tarfile.open(tar_path) as tar:
                tar.extractall(export, filter="data")
            head = run_gitleaks(["dir", str(export)], tmp / "head.json")
            head_keys = {(f["RuleID"], str(PurePosixPath(f["File"]).relative_to(export.as_posix())))
                         for f in head if f["File"].startswith(export.as_posix())}
            for f in history:
                f["in_head"] = int((f["RuleID"], f["File"]) in head_keys)
        return name, history, None


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with TABLE.open(encoding="utf-8") as f:
        names = [r["repo"] for r in csv.DictReader(f) if int(r["team_commits"]) > 0]
    rows, errors = [], []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for name, findings, error in tqdm(pool.map(scan, names), total=len(names), desc="Secrets", unit="repo"):
            if error:
                errors.append({"repo": name, "error": error})
            for f in findings:
                rows.append({"repo": name, "rule_id": f["RuleID"], "file": f["File"],
                             "file_ext": PurePosixPath(f["File"]).suffix.lower() or PurePosixPath(f["File"]).name.lower(),
                             "commit": f["Commit"], "date": f["Date"], "entropy": f["Entropy"],
                             "line": f["StartLine"], "in_head": f.get("in_head", 0)})
    fields = ["repo", "rule_id", "file", "file_ext", "commit", "date", "entropy", "line", "in_head"]
    with (OUT_DIR / "findings.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with (OUT_DIR / "scan_errors.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["repo", "error"])
        writer.writeheader()
        writer.writerows(errors)
    print(f"Scanned {len(names)} repos: {len(rows)} findings in {len({r['repo'] for r in rows})} repos; "
          f"{len(errors)} errors -> {OUT_DIR}")


if __name__ == "__main__":
    main()
