"""Revision R1: two exploratory checks of the registered jury analysis -> jury_revision.json (aggregates only).

Calls the registered code (analysis/prereg/jury_analysis.py) unchanged; its load() checks the hash of the frozen
predictor table. The base case must reproduce analysis/prereg/jury_results.json before anything else is reported.

1. Restricted comparison (Reviewer 1, comment 3): submission to the jury is not observable, so the comparison is
   repeated among repositories that look like a finished submission: at least one team commit in the last hour of
   the window and a written README with run or setup instructions. The rule is applied to awarded and other
   repositories alike.
2. Window start (Reviewer 2, comment 2): H1 with window commits counted from 12:00, 12:30 or 13:30 (end 18:00).

    python jury_revision.py <repository root>
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(__file__).resolve().parent / "jury_revision.json"
sys.path.insert(0, str(ROOT / "analysis/prereg"))
import jury_analysis as ja  # noqa: E402

TZ = timezone(timedelta(hours=5))
T0 = datetime(2026, 9, 23, 13, 0, tzinfo=TZ).timestamp()
T1 = datetime(2026, 9, 23, 18, 0, tzinfo=TZ).timestamp()

rows, tracks, y, cols = ja.load()
repo_ids = [r["repo"] for r in rows]
published = json.loads((ROOT / "analysis/prereg/jury_results.json").read_text(encoding="utf-8"))


def summary(res):
    out = []
    for r in res:
        d = {"hypothesis": r["hypothesis"], "variable": r["variable"], "p": r["p"], "p_holm": r["p_holm"],
             "awarded_median": r["awarded_median"], "other_median": r["other_median"],
             "awarded_mean": r["awarded_mean"], "other_mean": r["other_mean"]}
        if r["kind"] == "bin":
            d.update({"or": r["or"], "lo": r["lo"], "hi": r["hi"]})
        else:
            d.update({"delta": r["delta"], "lo": r["lo"], "hi": r["hi"]})
        out.append(d)
    return out


# base case reproduces the registered results
base = ja.primary(tracks, y, cols)
for b, p in zip(base, published["primary"]):
    assert abs(b["p_holm"] - p["p_holm"]) < 1e-12 and abs(b.get("delta", b.get("or")) - p.get("delta", p.get("or"))) < 1e-12

R: dict = {}
rf = pd.read_csv(ROOT / "data/readme_features.csv").set_index("repo").reindex(repo_ids)
written = rf.language.isin(["russian", "english", "kazakh", "mixed"]).values
run_instr = (rf.install_instructions.fillna(0) == 1).values
keep = (cols["last_hour_share"] > 0) & written & run_instr
res = ja.primary(tracks[keep], y[keep], {k: v[keep] for k, v in cols.items()})
R["restricted"] = {"rule": "team commit in 17:00-18:00 and a written README with run or setup instructions",
                   "n": int(keep.sum()), "awarded": int(y[keep].sum()), "other": int((~y[keep]).sum()),
                   "awarded_all_meet_rule": bool(y[keep].sum() == y.sum()), "removed": int((~keep).sum()),
                   "primary": summary(res)}

commits = pd.read_csv(ROOT / "data/commits.csv")
R["h1_start_moved"] = {}
for label, minutes in (("12:00", -60), ("12:30", -30), ("13:30", 30)):
    w = commits[(commits.ctime >= T0 + 60 * minutes) & (commits.ctime < T1)]
    wc = w.groupby("repo").size().reindex(repo_ids, fill_value=0).values.astype(float)
    c2 = dict(cols)
    c2["window_commits"] = wc
    k = wc > 0
    h1 = ja.primary(tracks[k], y[k], {kk: v[k] for kk, v in c2.items()})[0]
    R["h1_start_moved"][label] = {"n": int(k.sum()), "awarded": int(y[k].sum()), "delta": h1["delta"], "lo": h1["lo"],
                                  "hi": h1["hi"], "p": h1["p"], "p_holm": h1["p_holm"],
                                  "awarded_median": h1["awarded_median"], "other_median": h1["other_median"]}

OUT.write_text(json.dumps(R, indent=1), encoding="utf-8")
for r in R["restricted"]["primary"]:
    eff = f"OR {r['or']:.2f} ({r['lo']:.2f}-{r['hi']:.2f})" if "or" in r else f"delta {r['delta']:.2f} ({r['lo']:.2f}-{r['hi']:.2f})"
    print(f"{r['hypothesis']} {r['variable']:<16} {eff}  holm {r['p_holm']:.4f}")
print({k: v for k, v in R["restricted"].items() if k != "primary"})
for k, v in R["h1_start_moved"].items():
    print(k, f"n={v['n']} delta {v['delta']:.2f} ({v['lo']:.2f}-{v['hi']:.2f}) holm {v['p_holm']:.4f}")
