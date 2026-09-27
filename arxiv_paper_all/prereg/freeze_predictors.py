"""Freeze the predictors of the pre-registered jury-outcome analysis before any outcome is known.

Builds one row per active repository (at least one team commit in the event window) with the
track label and every predictor named in jury_preregistration.md, writes it to the private
data/prereg/jury_predictors.csv, and prints its SHA-256. The hash goes into the registration,
so anyone can later check that the predictors were fixed before the winners were announced.

Only the hash and aggregate counts are public; the table itself contains repository names.
Usage: python arxiv_paper_all/prereg/freeze_predictors.py
"""
from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATA = ROOT / "data"
OUT = DATA / "prereg" / "jury_predictors.csv"
HASH = HERE / "jury_predictors.sha256"
sys.path.insert(0, str(ROOT / "src"))
from plot_bilingual_charts import CASE_FIXES  # noqa: E402

TZ = timezone(timedelta(hours=5))
START = datetime(2026, 9, 23, 13, 0, tzinfo=TZ).timestamp()
LAST_HOUR = datetime(2026, 9, 23, 17, 0, tzinfo=TZ).timestamp()
END = datetime(2026, 9, 23, 18, 0, tzinfo=TZ).timestamp()


def main() -> int:
    repos = pd.read_csv(DATA / "repo_table.csv")
    stack = pd.read_csv(DATA / "stack.csv")
    crepo = pd.read_csv(DATA / "commit_repo_features.csv")
    readme = pd.read_csv(DATA / "readme_features.csv")
    commits = pd.read_csv(DATA / "commits.csv", usecols=["repo", "ctime"])
    labels = pd.read_csv(DATA / "hackalem_repos_analysis.csv")[["repo", "case_guess"]]
    labels["track"] = labels.case_guess.str.extract(r"^(\d{2})\b", expand=False)
    for repo, (_, new) in CASE_FIXES.items():
        labels.loc[labels.repo == repo, "track"] = new

    active = repos[repos.window_commits > 0][["repo", "window_commits", "hours_active"]]
    wc = commits[(commits.ctime >= START) & (commits.ctime < END)]
    last = wc[wc.ctime >= LAST_HOUR].groupby("repo").size()
    pre = commits[commits.ctime < START].groupby("repo").size()

    t = active.merge(labels[["repo", "track"]], on="repo", how="left")
    t["last_hour_share"] = (t.repo.map(last).fillna(0) / t.window_commits).round(4)
    t["pre_event_commits"] = t.repo.map(pre).fillna(0).astype(int)
    s = stack.set_index("repo")
    for col in ["tests", "dockerfile", "deploy_config", "agents_md", "claude_md"]:
        t[col] = t.repo.map(s[col]).fillna(0).astype(int)
    t["llm_sdk"] = t.repo.map(s.llm_sdks.notna() & (s.llm_sdks.astype(str) != "")).fillna(False).astype(int)
    c = crepo.set_index("repo")
    t["agent_signed"] = (t.repo.map(c.agent_signed_commits).fillna(0) > 0).astype(int)
    t["codex_branch"] = t.repo.map(c.agent_branch_kinds.fillna("").str.contains("codex")).fillna(False).astype(int)
    r = readme.set_index("repo")
    t["readme_words"] = t.repo.map(r.words).fillna(0).astype(int)
    t["deployed_link"] = t.repo.map(r.deployed_link).fillna(0).astype(int)

    t = t.sort_values("repo").reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT, index=False, lineterminator="\n")
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    HASH.write_text(f"{digest}  data/prereg/jury_predictors.csv\n", encoding="utf-8")

    print(f"rows: {len(t)} active repositories; with track: {t.track.notna().sum()}; columns: {', '.join(t.columns)}")
    print(t.drop(columns=["repo", "track"]).describe().T[["mean", "50%", "max"]].round(3).to_string())
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
