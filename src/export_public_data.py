"""Export the public, derived dataset -> public_data_generated/

What is released (see public_data_generated/DATA_CARD.md):
  repositories.csv   one row per organiser-created repository, with a random identifier
  commits.csv        one row per team commit: timing, size, script, agent kind; no SHA, text or author
  aggregates/*.csv   the tables behind the figures, and RQ4 credential results as aggregates only
  recollection.csv   repository names and the commit each clone ended at, with no link to the identifiers
  SHA256SUMS

What is never released: names or e-mail addresses, commit messages or SHAs next to features, README
text, any secret value, and any per-repository flag about credentials or committed .env files.
Random identifiers are kept stable across runs through a private map in data/public_id_map.csv.
"""
from __future__ import annotations

import csv
import hashlib
import json
import secrets
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PAPER = ROOT / "arxiv_paper_all"
OUT = ROOT / "public_data_generated"
ID_MAP = DATA / "public_id_map.csv"
TZ = timezone(timedelta(hours=5))
START = datetime(2026, 9, 23, 13, 0, tzinfo=TZ).timestamp()
END = datetime(2026, 9, 23, 18, 0, tzinfo=TZ).timestamp()


def id_map(names: list[str]) -> dict[str, str]:
    known = {}
    if ID_MAP.exists():
        known = {r["repo"]: r["id"] for r in csv.DictReader(ID_MAP.open(encoding="utf-8"))}
    used = set(known.values())
    for n in names:
        while n not in known:
            candidate = "r" + secrets.token_hex(5)
            if candidate not in used:
                known[n] = candidate
                used.add(candidate)
    with ID_MAP.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["repo", "id"])
        w.writerows(sorted(known.items()))
    return known


def main() -> None:
    repos = pd.read_csv(DATA / "repo_table.csv")
    meta = pd.read_csv(DATA / "repos.csv").rename(columns={"name": "repo"})
    stack = pd.read_csv(DATA / "stack.csv")
    crepo = pd.read_csv(DATA / "commit_repo_features.csv")
    readme = pd.read_csv(DATA / "readme_features.csv")
    commits = pd.read_csv(DATA / "commits.csv")
    labels = pd.read_csv(DATA / "hackalem_repos_analysis.csv")[["repo", "case_guess"]]
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from plot_bilingual_charts import CASE_FIXES  # noqa: E402

    ids = id_map(sorted(repos.repo))
    r = repos.merge(meta[["repo", "updated_at"]], on="repo")
    created = pd.to_datetime(r.created_at, utc=True).dt.tz_convert(TZ)
    updated = pd.to_datetime(r.updated_at, utc=True).dt.tz_convert(TZ)
    labels["track"] = labels.case_guess.str.extract(r"^(\d{2})\b", expand=False)
    labels["track_source"] = labels.track.notna().map({True: "earlier_table", False: "unclear"})
    for repo, (_, new) in CASE_FIXES.items():
        labels.loc[labels.repo == repo, ["track", "track_source"]] = [new, "corrected"]
    wc = commits[(commits.ctime >= START) & (commits.ctime < END)]
    last_hour = wc[wc.ctime >= END - 3600].groupby("repo").size()
    out = pd.DataFrame({
        "id": r.repo.map(ids),
        "created_date": created.dt.strftime("%Y-%m-%d"),
        "evening_batch": ((created.dt.strftime("%Y-%m-%d") == "2026-09-22") & created.dt.hour.isin([18, 19])).astype(int),
        "archived_before_event": (updated.map(lambda t: t.timestamp()) < START).astype(int),
        "archive_date": updated.dt.strftime("%Y-%m-%d"),
        "template_found": r.template_found,
        "team_commits": r.team_commits, "window_commits": r.window_commits,
        "window_commits_author_time": r.window_commits_author_time, "hours_active": r.hours_active,
        "pr_only_commits": r.pr_only_commits, "branches": r.branches,
    })
    out["active"] = (out.window_commits > 0).astype(int)
    out["last_hour_share"] = (r.repo.map(last_hour).fillna(0) / r.window_commits.where(r.window_commits > 0)).round(4)
    lab = labels.set_index("repo")
    out["track"] = r.repo.map(lab.track)
    out["track_source"] = r.repo.map(lab.track_source)
    s = stack.set_index("repo")
    keep_stack = ["primary_language", "frameworks", "llm_sdks", "dockerfile", "compose", "tests", "ci", "deploy_config",
                  "gitignore_covers_env", "env_example", "node_modules_committed", "virtualenv_committed", "pycache_committed",
                  "agents_md", "claude_md", "gemini_md", "cursor_rules", "copilot_instructions", "other_agent_rules"]
    for col in keep_stack:
        v = r.repo.map(s[col])
        out[col] = v.astype("Int64") if pd.api.types.is_numeric_dtype(s[col]) else v
    c = crepo.set_index("repo")
    out["pr_refs"] = r.repo.map(c.pr_refs).astype("Int64")
    out["agent_branch_kinds"] = r.repo.map(c.agent_branch_kinds)
    sig = commits[((commits.agent_trailer == 1) | (commits.agent_generated_marker == 1) | (commits.agent_account == 1))]
    for kind in ["claude", "codex", "cursor", "copilot", "devin", "bot"]:
        out[f"signed_commits_{kind}"] = r.repo.map(sig[sig.agent_kind == kind].groupby("repo").size()).fillna(0).astype(int)
    rd = readme.set_index("repo")
    for col in ["language", "words", "headings", "install_instructions", "deployed_link", "images", "mentions_agent_tool"]:
        v = r.repo.map(rd[col])
        out[f"readme_{col}"] = v.astype("Int64") if pd.api.types.is_numeric_dtype(rd[col]) else v
    out = out.rename(columns={"readme_install_instructions": "readme_run_instructions"})
    OUT.mkdir(exist_ok=True)
    out.sort_values("id").to_csv(OUT / "repositories.csv", index=False)

    # Commits: timing relative to the start, no SHA, no text, authors as an ordinal within the repository.
    cm = commits.copy()
    cm["author"] = cm.groupby("repo").author_key.transform(lambda k: pd.factorize(k)[0] + 1)
    pub = pd.DataFrame({
        "id": cm.repo.map(ids), "minutes_from_start": ((cm.ctime - START) / 60).round(2),
        "author_minutes_from_start": ((cm.atime - START) / 60).round(2), "in_window": cm.in_window,
        "is_merge": cm.is_merge, "files": cm.files, "added": cm.added, "deleted": cm.deleted,
        "conventional": cm.conventional, "subject_script": cm.subject_script,
        "agent_kind": cm.agent_kind.where(((cm.agent_trailer == 1) | (cm.agent_generated_marker == 1) | (cm.agent_account == 1)), ""),
        "author": cm.author, "author_is_bot": cm.author_bot})
    pub.sort_values(["id", "minutes_from_start"]).to_csv(OUT / "commits.csv", index=False)

    agg = OUT / "aggregates"
    agg.mkdir(exist_ok=True)
    for name in ["timeline_10min.csv", "last_hour_share.csv", "tracks.csv", "tool_traces.csv",
                 "codex_trace_combinations.csv", "frameworks.csv"]:
        shutil.copy(PAPER / "tables" / name, agg / name)
    facts = json.loads((PAPER / "analysis" / "facts_paper.json").read_text())
    (agg / "credentials_aggregate.json").write_text(json.dumps(facts["rq4"], indent=2), encoding="utf-8")

    with (OUT / "recollection.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["full_name", "head_commit_at_collection"])
        for n in sorted(repos.repo):
            head = subprocess.run(["git", f"--git-dir={DATA / 'clones' / (n + '.git')}", "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
            w.writerow([f"BAITC-Hacks/{n}", head])

    # Safety check: no released file except the re-collection list may contain a repository name.
    names = set(repos.repo)
    for p in OUT.rglob("*"):
        if p.is_file() and p.name not in ("recollection.csv", "SHA256SUMS"):
            text = p.read_text(encoding="utf-8")
            if "hack-" in text or any(n in text for n in names):
                raise SystemExit(f"refusing to release: {p.name} contains repository names")
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (OUT / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}\n"
                                            for p in files), encoding="utf-8")
    print(f"wrote {len(out)} repositories, {len(pub)} commits, {len(files)} files -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
