"""Reproduce the paper's main numbers from the released data alone (public_data_generated/).

Anyone can run this without the private clones or files. It recomputes RQ1-RQ3 headline numbers
from repositories.csv and commits.csv and compares each with analysis/facts_paper.json.
RQ4 (credentials) is released only as aggregates, so it is not recomputed here.
Usage: python arxiv_paper_all/analysis/reproduce_public.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

PAPER = Path(__file__).resolve().parent.parent
PUB = PAPER.parent / "public_data_generated"


def pct(a, b) -> float:
    return round(100 * a / b, 1)


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
        ("committed in all 5 hours %", pct((act.hours_active == 5).sum(), len(act)), F["rq2"]["teams_all_5_hours"]["pct"]),
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
        ("signed window commits %", pct((ww.agent_kind.fillna("").isin(["claude", "codex", "cursor", "copilot", "devin"])).sum(), len(ww)),
         T["signed_commits"]["pct"]),
        ("test files %", pct(act.tests.sum(), len(act)), F["rq3"]["tests"]["pct"]),
        ("Dockerfile %", pct(act.dockerfile.sum(), len(act)), F["rq3"]["dockerfile"]["pct"]),
        ("README Russian %", pct((written.readme_language == "russian").sum(), len(written)), F["rq3"]["readme_russian"]["pct"]),
        ("README Kazakh %", pct((written.readme_language == "kazakh").sum(), len(written)), F["rq3"]["readme_kazakh"]["pct"]),
        ("README median words", int(written.readme_words.median()), F["rq3"]["readme_words"]["median"]),
    ]
    bad = 0
    for name, mine, paper in checks:
        ok = float(mine) == float(paper)
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {name:32s} public data {mine!s:>8}   paper {paper!s:>8}")
    print(f"{len(checks) - bad} of {len(checks)} numbers reproduced from the public data")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
