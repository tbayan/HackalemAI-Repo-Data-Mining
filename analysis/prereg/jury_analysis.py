"""Pre-registered analysis of the jury's decisions (OSF https://osf.io/bm3je; jury_preregistration.md).

Inputs (private, not released, because they link teams to repositories):
  data/prereg/jury_predictors.csv   frozen predictor table (SHA-256 checked below)
  data/prereg/award_matches.csv     official award list linked to repositories (match_awards.py)
Output (aggregate only, released): analysis/prereg/jury_results.json

Everything follows Section 5 of the registration. Two details the registration leaves open are fixed
here and listed as deviations in analysis/deviations.md:
  - within-track percentile rank = 100 * (mid-rank - 0.5) / n_track;
  - the bootstrap for Cliff's delta resamples awarded and other repositories separately within each track.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, norm

ROOT = Path(__file__).resolve().parents[2]
PRED = ROOT / "data/prereg/jury_predictors.csv"
MATCH = ROOT / "data/prereg/award_matches.csv"
OUT = Path(__file__).resolve().parent / "jury_results.json"
FROZEN_SHA = "9332945fb024e544c1f40bd37ec1bebf6a9fcf68ad6193a1af30a202449aba0b"

PRIMARY = [  # (hypothesis, variable, kind, direction for one-sided tests or None)
    ("H1", "window_commits", "cont", +1),
    ("H2", "deployed_link", "bin", +1),
    ("H3", "tests", "bin", None),
    ("H3", "dockerfile", "bin", None),
    ("H3", "readme_words", "cont", None),
    ("H4", "agents_md", "bin", None),
    ("H4", "agent_signed", "bin", None),
    ("H4", "codex_branch", "bin", None),
    ("H5", "last_hour_share", "cont", None),
]
N_PERM = 10_000
N_BOOT = 10_000
SEED = 2026


def load():
    assert hashlib.sha256(PRED.read_bytes()).hexdigest() == FROZEN_SHA, "frozen predictor file changed"
    rows = [r for r in csv.DictReader(PRED.open(encoding="utf-8")) if r["track"]]
    awarded = {m["repo"] for m in csv.DictReader(MATCH.open(encoding="utf-8")) if m["repo"]}
    tracks = np.array([r["track"] for r in rows])
    y = np.array([r["repo"] in awarded for r in rows], dtype=bool)
    cols = {k: np.array([float(r[k]) for r in rows]) for k in rows[0] if k not in ("repo", "track")}
    return rows, tracks, y, cols


def pct_rank(x, tracks):
    """Within-track percentile rank, 100 * (mid-rank - 0.5) / n."""
    out = np.empty_like(x)
    for t in np.unique(tracks):
        i = tracks == t
        out[i] = 100 * (rankdata(x[i]) - 0.5) / i.sum()
    return out


def stat(v, y, tracks, weights):
    """Stratified difference awarded minus other, weighted by the number awarded per track."""
    s = 0.0
    for t, w in weights.items():
        i = tracks == t
        a, o = v[i & y], v[i & ~y]
        s += w * (a.mean() - o.mean())
    return s


def permute(v, y, tracks, weights, direction, rng):
    obs = stat(v, y, tracks, weights)
    idx = {t: np.where(tracks == t)[0] for t in weights}
    count = 0
    yp = y.copy()
    for _ in range(N_PERM):
        for t, ii in idx.items():
            yp[ii] = rng.permutation(y[ii])
        s = stat(v, yp, tracks, weights)
        count += (s >= obs) if direction == +1 else (abs(s) >= abs(obs))
    return obs, (1 + count) / (1 + N_PERM)


def mh_or(x, y, tracks):
    """Mantel-Haenszel odds ratio with the Robins-Breslow-Greenland 95% interval."""
    R = S = PR = PSQR = QS = 0.0
    for t in np.unique(tracks):
        i = tracks == t
        if y[i].sum() == 0:
            continue
        a = np.sum(i & y & (x == 1)); b = np.sum(i & y & (x == 0))
        c = np.sum(i & ~y & (x == 1)); d = np.sum(i & ~y & (x == 0))
        n = a + b + c + d
        r, s, p, q = a * d / n, b * c / n, (a + d) / n, (b + c) / n
        R += r; S += s; PR += p * r; PSQR += p * s + q * r; QS += q * s
    if R == 0 or S == 0:
        return {"or": None, "lo": None, "hi": None}
    var = PR / (2 * R * R) + PSQR / (2 * R * S) + QS / (2 * S * S)
    lor = math.log(R / S)
    z = norm.ppf(0.975)
    return {"or": R / S, "lo": math.exp(lor - z * math.sqrt(var)), "hi": math.exp(lor + z * math.sqrt(var))}


def cliff(v, y, tracks):
    num = den = 0.0
    for t in np.unique(tracks):
        i = tracks == t
        a, o = v[i & y], v[i & ~y]
        if len(a) == 0:
            continue
        diff = np.sign(a[:, None] - o[None, :])
        num += diff.sum()
        den += len(a) * len(o)
    return num / den


def cliff_ci(v, y, tracks, rng):
    groups = [(v[(tracks == t) & y], v[(tracks == t) & ~y]) for t in np.unique(tracks) if ((tracks == t) & y).any()]
    boots = np.empty(N_BOOT)
    for b in range(N_BOOT):
        num = den = 0.0
        for a, o in groups:
            ab = rng.choice(a, len(a)); ob = rng.choice(o, len(o))
            num += np.sign(ab[:, None] - ob[None, :]).sum(); den += len(a) * len(o)
        boots[b] = num / den
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def holm(ps):
    order = np.argsort(ps)
    m = len(ps)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * ps[i]))
        adj[i] = running
    return adj


def primary(tracks, y, cols, rng_seed=SEED, var_override=None):
    weights = {t: (y & (tracks == t)).sum() / y.sum() for t in np.unique(tracks) if (y & (tracks == t)).any()}
    res = []
    rng = np.random.default_rng(rng_seed)
    for h, var, kind, direction in PRIMARY:
        name = (var_override or {}).get(var, var)
        x = cols[name]
        v = x if kind == "bin" else pct_rank(x, tracks)
        obs, p = permute(v, y, tracks, weights, direction, rng)
        r = {"hypothesis": h, "variable": name, "kind": kind, "one_sided": direction is not None,
             "T": obs, "p": p,
             "awarded_mean": float(x[y].mean()), "other_mean": float(x[~y].mean()),
             "awarded_median": float(np.median(x[y])), "other_median": float(np.median(x[~y]))}
        if kind == "bin":
            r.update(mh_or(x, y, tracks))
            r["negligible"] = r["lo"] is not None and 0.5 <= r["lo"] and r["hi"] <= 2.0
        else:
            r["delta"] = cliff(x, y, tracks)
            r["lo"], r["hi"] = cliff_ci(x, y, tracks, np.random.default_rng(rng_seed))
            r["negligible"] = -0.15 <= r["lo"] and r["hi"] <= 0.15
        res.append(r)
    adj = holm(np.array([r["p"] for r in res]))
    for r, a in zip(res, adj):
        r["p_holm"] = float(a)
        r["associated"] = bool(a < 0.05)
    return res


def conditional_logit(tracks, y, cols):
    """Exploratory: conditional logistic regression stratified by track (registration, Section 5.3)."""
    from statsmodels.discrete.conditional_models import ConditionalLogit
    names = ["window_commits", "deployed_link", "tests", "dockerfile", "readme_words",
             "agents_md", "agent_signed", "codex_branch", "last_hour_share", "hours_active"]
    X = np.column_stack([np.log1p(cols[n]) if n == "window_commits" else cols[n] for n in names])
    X[:, names.index("readme_words")] = X[:, names.index("readme_words")] / 1000   # per 1,000 words
    keep = np.isin(tracks, [t for t in np.unique(tracks) if (y & (tracks == t)).any()])
    try:
        fit = ConditionalLogit(y[keep].astype(float), X[keep], groups=tracks[keep]).fit(disp=0)
        ci = fit.conf_int()
        return [{"variable": n + (" (log 1+x)" if n == "window_commits" else " (per 1,000)" if n == "readme_words" else ""),
                 "or": float(np.exp(b)), "lo": float(np.exp(c[0])), "hi": float(np.exp(c[1])), "p": float(p)}
                for n, b, c, p in zip(names, fit.params, ci, fit.pvalues)]
    except Exception as e:  # separation: the registration names a Firth fit; report the failure instead of guessing
        return [{"error": repr(e)}]


def main() -> None:
    rows, tracks, y, cols = load()
    matches = list(csv.DictReader(MATCH.open(encoding="utf-8")))
    out = {
        "awarded_announced": len(matches),
        "awarded_matched": int(y.sum()),
        "unmatched": [{"track": m["track"], "place": m["place"], "reason": m["status"]} for m in matches if not m["repo"]],
        "tracklabelled_active": int(len(y)),
        "awarded_per_track": {t: int((y & (tracks == t)).sum()) for t in sorted(np.unique(tracks))},
        "primary": primary(tracks, y, cols),
        "secondary_conditional_logit": conditional_logit(tracks, y, cols),
    }
    # robustness (registration, Section 5.5)
    keep = cols["pre_event_commits"] == 0
    out["robust_no_pre_event"] = {"n": int(keep.sum()), "awarded": int(y[keep].sum()),
                                  "primary": primary(tracks[keep], y[keep], {k: v[keep] for k, v in cols.items()})}
    h1 = primary(tracks, y, cols, var_override={"window_commits": "hours_active"})[0]
    out["robust_hours_for_H1"] = h1
    out["robust_finalist_outcome"] = "not run: no official list of finalists was available to us"
    out["robust_unmatched_as_nonawarded"] = ("identical to the primary analysis: the unmatched team has no "
                                             "identifiable repository, so every repository in its track is already coded 0")
    OUT.write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    for r in out["primary"]:
        eff = (f"OR {r['or']:.2f} [{r['lo']:.2f}, {r['hi']:.2f}]" if r["kind"] == "bin" and r["or"]
               else f"delta {r.get('delta', float('nan')):.2f} [{r['lo']:.2f}, {r['hi']:.2f}]" if r["kind"] == "cont" else "OR n/a")
        print(f"{r['hypothesis']} {r['variable']:<16} awd {r['awarded_mean']:.3f} oth {r['other_mean']:.3f} "
              f"T {r['T']:+.3f} p {r['p']:.4f} holm {r['p_holm']:.4f} {eff} negl={r['negligible']}")
    print("matched", out["awarded_matched"], "of", out["awarded_announced"], "| per track", out["awarded_per_track"])


if __name__ == "__main__":
    main()
