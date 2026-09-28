"""Reproduce the paper's main numbers from the released data alone (public_data_generated/).

Anyone can run this without the private clones or files. It recomputes RQ1-RQ3 headline numbers
from repositories.csv and commits.csv and compares each with analysis/facts_paper.json.
RQ4 (credentials) is released only as aggregates, so it is not recomputed here.
Usage: python arxiv_paper_all/analysis/reproduce_public.py
"""
from __future__ import annotations

import json
import math
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd
from scipy import stats

PAPER = Path(__file__).resolve().parent.parent
PUB = PAPER.parent / "public_data_generated"


def rhu(x, places: int = 1) -> float:
    """Round half up, as the paper does (86.25 -> 86.3)."""
    return float(Decimal(str(float(x))).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def pct(a, b) -> float:
    return rhu(100 * a / b, 1)


def chi2(table) -> float:
    return rhu(stats.chi2_contingency(table, correction=False)[0], 1)


def haldane_or(said, trace) -> float:
    a, b = (said & trace).sum() + 0.5, (said & ~trace).sum() + 0.5
    c, d = (~said & trace).sum() + 0.5, (~said & ~trace).sum() + 0.5
    return rhu(math.exp(math.log(a * d / (b * c))), 2)


def main() -> int:
    F = json.loads((PAPER / "analysis" / "facts_paper.json").read_text())
    r = pd.read_csv(PUB / "repositories.csv", dtype={"track": str})
    c = pd.read_csv(PUB / "commits.csv")
    act = r[r.active == 1]
    open_nb = r[(r.archived_before_event == 0) & (r.evening_batch == 0)]
    w = c[(c.in_window == 1) & c.id.isin(act.id)]
    share = act.last_hour_share
    codex_spec = (act.codex_prefix_branches > 0) | (act.signed_commits_codex > 0) | (act.named_commits_codex > 0)
    codex = codex_spec | (act.agents_md == 1)
    claude = (act.claude_md == 1) | (act.claude_prefix_branches > 0) | (act.signed_commits_claude > 0) | (act.named_commits_claude > 0)
    written = act[act.readme_language.isin(["russian", "english", "kazakh", "mixed"])]
    names_cx, names_cl = act.readme_names_codex == 1, act.readme_names_claude_code == 1
    ww = c[(c.in_window == 1) & c.id.isin(act.id)]
    SR, T = F["rq2"]["traces"]["self_report"], F["rq2"]["traces"]
    # creation-date groups (day level); the batch is its own group except in the naive view
    day = r.created_date
    grp = pd.cut(pd.to_datetime(day), bins=pd.to_datetime(["2000-01-01", "2026-09-01", "2026-09-15", "2026-09-22",
                                                            "2026-09-23", "2026-09-24"]), right=False,
                 labels=["before_sep01", "sep01_14", "sep15_21", "sep22", "sep23"]).astype(str)
    onb = open_nb.assign(g=grp[open_nb.index])
    onb = onb[onb.g != "sep23"]
    naive = r.assign(g=grp)
    naive = naive[naive.g != "sep23"]
    # commit size: non-merge window commits of the repositories with both signed and other commits
    nm = w[w.is_merge == 0].assign(signed=w.agent_kind.fillna("").isin(["claude", "codex", "cursor", "copilot", "devin"]))
    kinds = nm.groupby("id").signed.agg(["any", "all"])
    both = nm[nm.id.isin(kinds[kinds["any"] & ~kinds["all"]].index)]
    tr = act.dropna(subset=["track"])
    early = r.id.map(c.groupby("id").minutes_from_start.min()).lt(0)
    arch = r.archived_before_event == 1
    ap = tr[tr.approach_core_method.notna()]
    ct_ap = pd.crosstab(ap.track, ap.approach_core_method)
    checks = [
        ("repositories", len(r), F["rq1"]["total"]),
        ("archived before the event", int(r.archived_before_event.sum()), F["rq1"]["prearchived"]["n"]),
        ("evening batch", int(r.evening_batch.sum()), F["rq1"]["batch"]["n"]),
        ("active", len(act), F["rq1"]["active"]["n"]),
        ("active % of all", pct(len(act), len(r)), F["rq1"]["active"]["pct"]),
        ("active % of open, not batch", pct(open_nb.active.sum(), len(open_nb)), F["rq1"]["active_of_open_nonbatch"]["pct"]),
        ("window commits (active)", len(w), F["rq2"]["window_commits"]),
        ("median last-hour share %", round(100 * share.median(), 1), F["rq2"]["team_share"]["median"]),
        ("majority in last hour %", pct((share > 0.5).sum(), len(act)), F["rq2"]["teams_majority_last_hour"]["pct"]),
        ("commits in 4+ of the 5 hours %", pct((act.hours_active >= 4).sum(), len(act)), F["rq2"]["teams_4plus_hours"]["pct"]),
        ("all window commits in last hour", int((share == 1).sum()), F["rq2"]["teams_all_last_hour"]["n"]),
        ("active of open, not batch (n)", int(open_nb.active.sum()), F["rq1"]["active_of_open_nonbatch"]["n"]),
        ("chi2 creation date, open not batch", chi2(pd.crosstab(onb.g, onb.active)), F["rq1"]["creation_chi2_open_nonbatch"]["chi2"]),
        ("chi2 creation date, all (naive)", chi2(pd.crosstab(naive.g, naive.active)), F["rq1"]["creation_chi2_all"]["chi2"]),
        ("pre-event commits, archived before", int((early & arch).sum()), F["rq1"]["pre_event_commits"]["prearchived"]["n"]),
        ("pre-event commits, open", int((early & ~arch).sum()), F["rq1"]["pre_event_commits"]["open"]["n"]),
        ("Codex-specific trace %", pct(codex_spec.sum(), len(act)), T["codex"]["specific"]["pct"]),
        ("Codex trace incl. AGENTS.md %", pct(codex.sum(), len(act)), T["codex"]["any"]["pct"]),
        ("Claude Code trace %", pct(claude.sum(), len(act)), T["claude"]["any"]["pct"]),
        ("README names Codex (of written) %", pct(names_cx.sum(), len(written)), SR["codex_strict"]["mention"]["pct"]),
        ("Codex-specific | names Codex %", pct((names_cx & codex_spec).sum(), names_cx.sum()),
         SR["codex_strict"]["specific_given_mention"]["pct"]),
        ("Codex signature | names Codex %", pct((names_cx & (act.signed_commits_codex > 0)).sum(), names_cx.sum()),
         SR["codex_strict"]["signature_given_mention"]["pct"]),
        ("Claude signature | names Claude Code %", pct((names_cl & (act.signed_commits_claude > 0)).sum(), names_cl.sum()),
         SR["claude_strict"]["signature_given_mention"]["pct"]),
        ("OR naming vs trace, Codex (Haldane)", haldane_or(names_cx.values, codex.values), SR["codex_strict"]["assoc"]["or"]),
        ("OR naming vs trace, Claude (Haldane)", haldane_or(names_cl.values, claude.values), SR["claude_strict"]["assoc"]["or"]),
        ("signed window commits %", pct((ww.agent_kind.fillna("").isin(["claude", "codex", "cursor", "copilot", "devin"])).sum(), len(ww)),
         T["signed_commits"]["pct"]),
        ("pooled median size, signed", float(both[both.signed].code_lines.median()), T["commit_size"]["pooled_signed"]),
        ("pooled median size, other", float(both[~both.signed].code_lines.median()), T["commit_size"]["pooled_unsigned"]),
        ("test files %", pct(act.tests.sum(), len(act)), F["rq3"]["tests"]["pct"]),
        ("test file defines a test %", pct(act.test_functions.sum(), len(act)), F["rq3"]["test_functions"]["pct"]),
        ("median window commits, T1", float(tr[tr.track == "01"].window_commits.median()), F["rq3"]["tracks"]["t01"]["commits"]),
        ("median window commits, T5", float(tr[tr.track == "05"].window_commits.median()), F["rq3"]["tracks"]["t05"]["commits"]),
        ("Kruskal-Wallis H, commits by track", rhu(stats.kruskal(*[g.window_commits for _, g in tr.groupby("track")]).statistic, 1),
         F["rq3"]["commits_by_track"]["h"]),
        ("Dockerfile %", pct(act.dockerfile.sum(), len(act)), F["rq3"]["dockerfile"]["pct"]),
        ("README Russian %", pct((written.readme_language == "russian").sum(), len(written)), F["rq3"]["readme_russian"]["pct"]),
        ("README Kazakh %", pct((written.readme_language == "kazakh").sum(), len(written)), F["rq3"]["readme_kazakh"]["pct"]),
        ("README with a Kazakh-specific letter %", pct((written.readme_kazakh_letters > 0).sum(), len(written)),
         F["rq3"]["readme_any_kazakh_letter"]["pct"]),
        ("README median words", int(written.readme_words.median()), F["rq3"]["readme_words"]["median"]),
        ("approach: rules/model + LLM explains %", pct((ap.approach_core_method.isin(["algorithm", "ml_model"])
                                                        & (ap.approach_llm_role == "support")).sum(), len(ap)),
         F["rq3"]["approach"]["pattern"]["explains"]["pct"]),
        ("approach: LLM produces the result %", pct((ap.approach_llm_role == "core").sum(), len(ap)),
         F["rq3"]["approach"]["pattern"]["llm_task"]["pct"]),
        ("approach by track, Cramer's V", rhu(math.sqrt(stats.chi2_contingency(ct_ap, correction=False)[0]
                                                     / (len(ap) * (min(ct_ap.shape) - 1))), 2),
         F["rq3"]["approach"]["by_track"]["v"]),
        ("briefs with one method >= 75%", int((ct_ap.max(axis=1) / ct_ap.sum(axis=1) >= 0.75).sum()),
         F["rq3"]["approach"]["briefs_top75"]),
    ]
    bad = 0
    for name, mine, paper in checks:
        ok = float(mine) == float(paper)
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {name:40s} public data {mine!s:>8}   paper {paper!s:>8}")
    print(f"{len(checks) - bad} of {len(checks)} numbers reproduced from the public data")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
