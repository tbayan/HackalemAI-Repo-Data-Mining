"""Check of the LLM-coded approaches: agreement between the LLM coding and the adjudicated reference coding.

Procedure: the author and a second coder (an AI assistant) each coded the 60 sampled repositories from the same
material, without seeing the model's answers. Where the two codings differed, or the author's was missing, the
author decided the final label (adjudication.csv). This script reports, as aggregates only:
  - agreement of the model with the final labels (raw, Wilson interval, Cohen's kappa with a bootstrap interval,
    track-weighted agreement, confusion matrices) for the core method, the LLM role and the derived pattern;
  - agreement between the two codings before adjudication (items the author had coded);
  - how the disputed items were resolved (as the author's first coding, as the second coding, or otherwise).
The model's answers are read from the private key (data/llm_codebook/validation_key.csv).

    python llm_validation_agreement.py <repository root> <adjudication.csv>
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
from sklearn.metrics import cohen_kappa_score

ROOT = Path(sys.argv[1]).resolve()
ADJ = Path(sys.argv[2]).resolve()
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


def compare(a, b, tracks, size, rng):
    agree = [x == y for x, y in zip(a, b)]
    kappa = cohen_kappa_score(a, b)
    idx = np.arange(len(a))
    boots = []
    for _ in range(10_000):
        s = rng.choice(idx, len(idx))
        aa, bb = [a[i] for i in s], [b[i] for i in s]
        if len(set(aa) | set(bb)) > 1:
            boots.append(cohen_kappa_score(aa, bb))
    by_track = {t: [g for g, tr in zip(agree, tracks) if tr == t] for t in size}
    total = sum(size.values())
    weighted = sum(size[t] / total * (sum(v) / len(v)) for t, v in by_track.items() if v)
    return {"agreement": wilson(sum(agree), len(agree)), "kappa": rhu(kappa, 2),
            "kappa_lo": rhu(np.percentile(boots, 2.5), 2), "kappa_hi": rhu(np.percentile(boots, 97.5), 2),
            "weighted_agreement_pct": rhu(100 * weighted)}


key = {r["item"]: r for r in csv.DictReader((ROOT / "data/llm_codebook/validation_key.csv").open(encoding="utf-8"))}
adj = list(csv.DictReader(ADJ.open(encoding="utf-8")))
assert len(adj) == 60 and sorted(int(r["item"]) for r in adj) == list(range(1, 61))
for r in adj:
    assert r["final_core_method"] in CORE and r["final_llm_role"] in ROLE, f"item {r['item']}: final label missing or invalid"
coded = list(csv.DictReader((ROOT / "data/llm_codebook/all.csv").open(encoding="utf-8")))
size = Counter(r["track"] for r in coded if r["repo"])
tracks = [key[r["item"]]["track"] for r in adj]
rng = np.random.default_rng(2026)

R: dict = {"n": len(adj)}
# 1. model vs final labels (the validation result)
fc, fr = [r["final_core_method"] for r in adj], [r["final_llm_role"] for r in adj]
mc, mr = [key[r["item"]]["model_core_method"] for r in adj], [key[r["item"]]["model_llm_role"] for r in adj]
R["model_vs_final"] = {
    "core_method": compare(fc, mc, tracks, size, rng),
    "llm_role": compare(fr, mr, tracks, size, rng),
    "pattern": compare([pattern(c, r) for c, r in zip(fc, fr)], [pattern(c, r) for c, r in zip(mc, mr)], tracks, size, rng),
    "confusion_core_model_by_final": {f"{m}|{f}": n for (m, f), n in Counter(zip(mc, fc)).items()},
    "confusion_role_model_by_final": {f"{m}|{f}": n for (m, f), n in Counter(zip(mr, fr)).items()},
}
# 2. the two codings before adjudication (items the author had coded completely)
done = [r for r in adj if r["author_first_core"] in CORE and r["author_first_role"] in ROLE]
R["coders_before_adjudication"] = {
    "items": len(done),
    "core_method": compare([r["author_first_core"] for r in done], [r["second_core"] for r in done], [key[r["item"]]["track"] for r in done], size, rng),
    "llm_role": compare([r["author_first_role"] for r in done], [r["second_role"] for r in done], [key[r["item"]]["track"] for r in done], size, rng),
}
# 3. how the disputed items were resolved
res = Counter()
for r in adj:
    if r["status"] != "DECIDE":
        continue
    fin = (r["final_core_method"], r["final_llm_role"])
    res["as_author_first"] += fin == (r["author_first_core"], r["author_first_role"])
    res["as_second"] += fin == (r["second_core"], r["second_role"])
    res["other"] += fin not in {(r["author_first_core"], r["author_first_role"]), (r["second_core"], r["second_role"])}
R["adjudication"] = {"disputed": sum(r["status"] == "DECIDE" for r in adj), **res}
OUT.write_text(json.dumps(R, indent=1), encoding="utf-8")
m = R["model_vs_final"]
print(f"model vs final: core {m['core_method']['agreement']['pct']}% (kappa {m['core_method']['kappa']}), "
      f"role {m['llm_role']['agreement']['pct']}% (kappa {m['llm_role']['kappa']}), "
      f"pattern {m['pattern']['agreement']['pct']}% (kappa {m['pattern']['kappa']})")
c = R["coders_before_adjudication"]
print(f"coders before adjudication ({c['items']} items): core {c['core_method']['agreement']['pct']}%, role {c['llm_role']['agreement']['pct']}%")
print("adjudication:", R["adjudication"])
print("written", OUT)
