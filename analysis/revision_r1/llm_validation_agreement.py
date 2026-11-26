"""Revision R1 (Reviewer 3, comment 3): agreement between the LLM coding and the author's blind hand coding.

Reads the filled sheet (LLM_validation_sheet.xlsx, sheet 'Label') and the private key
(data/llm_codebook/validation_key.csv), and writes llm_validation_agreement.json (aggregates only):
raw agreement with a Wilson interval, Cohen's kappa with a bootstrap interval (10,000 resamples, seed 2026),
agreement weighted by each track's share of the 984 coded repositories, confusion matrices, and agreement on
the pattern used in the paper (rules or trained model with an LLM in support / LLM produces the result /
no LLM / other).

    python llm_validation_agreement.py <repository root> <filled sheet.xlsx>
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
from openpyxl import load_workbook
from sklearn.metrics import cohen_kappa_score

ROOT = Path(sys.argv[1]).resolve()
SHEET = Path(sys.argv[2]).resolve()
OUT = Path(__file__).resolve().parent / "llm_validation_agreement.json"
CORE = {"llm_prompt", "llm_agent", "ml_model", "algorithm", "pretrained", "unclear"}
ROLE = {"none", "core", "support", "unclear"}


def rhu(x, p=1):
    return float(Decimal(str(x)).quantize(Decimal(1).scaleb(-p), rounding=ROUND_HALF_UP))


def wilson(k, n, z=1.959963984540054):
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return {"n": k, "of": n, "pct": rhu(100 * k / n), "lo": rhu(100 * (c - h)), "hi": rhu(100 * (c + h))}


def pattern(core, role):  # same rule as analysis/run_analysis.py
    if core in ("algorithm", "ml_model") and role == "support":
        return "explains"
    return {"core": "llm_task", "none": "no_llm"}.get(role, "other")


key = {r["item"]: r for r in csv.DictReader((ROOT / "data/llm_codebook/validation_key.csv").open(encoding="utf-8"))}
ws = load_workbook(SHEET, data_only=True)["Label"]
rows = []
for r in ws.iter_rows(min_row=2, values_only=True):
    item, core, role = str(r[0]), (r[5] or "").strip(), (r[6] or "").strip()
    assert core in CORE and role in ROLE, f"item {item}: missing or invalid label ({core!r}, {role!r})"
    k = key[item]
    rows.append({"track": k["track"], "h_core": core, "h_role": role, "m_core": k["model_core_method"], "m_role": k["model_llm_role"]})
assert len(rows) == 60

# track weights: share of the 984 coded repositories in each track
coded = list(csv.DictReader((ROOT / "data/llm_codebook/all.csv").open(encoding="utf-8")))
size = Counter(r["track"] for r in coded if r["repo"])
total = sum(size.values())

rng = np.random.default_rng(2026)
R: dict = {"n": len(rows)}
for name, h, m in (("core_method", "h_core", "m_core"), ("llm_role", "h_role", "m_role"), ("pattern", None, None)):
    if name == "pattern":
        hv = [pattern(r["h_core"], r["h_role"]) for r in rows]
        mv = [pattern(r["m_core"], r["m_role"]) for r in rows]
    else:
        hv, mv = [r[h] for r in rows], [r[m] for r in rows]
    agree = [a == b for a, b in zip(hv, mv)]
    kappa = cohen_kappa_score(hv, mv)
    boots = []
    idx = np.arange(len(rows))
    for _ in range(10_000):
        s = rng.choice(idx, len(idx))
        hs, ms = [hv[i] for i in s], [mv[i] for i in s]
        if len(set(hs) | set(ms)) > 1:
            boots.append(cohen_kappa_score(hs, ms))
    by_track = {t: [a for a, r in zip(agree, rows) if r["track"] == t] for t in size}
    weighted = sum(size[t] / total * (sum(v) / len(v)) for t, v in by_track.items() if v)
    R[name] = {"agreement": wilson(sum(agree), len(agree)), "kappa": rhu(kappa, 2),
               "kappa_lo": rhu(np.percentile(boots, 2.5), 2), "kappa_hi": rhu(np.percentile(boots, 97.5), 2),
               "weighted_agreement_pct": rhu(100 * weighted),
               "confusion_model_by_author": {f"{a}|{b}": c for (a, b), c in Counter(zip(mv, hv)).items()}}
OUT.write_text(json.dumps(R, indent=1), encoding="utf-8")
print(json.dumps(R, indent=1))
