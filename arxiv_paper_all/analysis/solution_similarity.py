"""How similar are solutions to the same brief? Helpers for run_analysis.py (exploratory, added after the plan).

Each repository is a set of items of one kind (dependency names, file paths, README headings, IDs of
source-code files). The similarity of two repositories is the Jaccard index of their sets. Solutions to the
same brief are compared with solutions to different briefs; the difference is the similarity that the
shared task adds. A permutation test shuffles the track labels.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import sparse


def jaccard_matrix(sets: list[set]) -> np.ndarray:
    """Pairwise Jaccard index of item sets (diagonal and pairs of two empty sets set to NaN)."""
    vocab = {item: k for k, item in enumerate(sorted(set().union(*sets)))}
    rows = [i for i, s in enumerate(sets) for _ in s]
    cols = [vocab[item] for s in sets for item in s]
    x = sparse.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(sets), len(vocab)))
    inter = (x @ x.T).toarray()
    size = np.asarray(x.sum(axis=1)).ravel()
    union = size[:, None] + size[None, :] - inter
    with np.errstate(invalid="ignore", divide="ignore"):
        j = np.where(union > 0, inter / union, np.nan)
    np.fill_diagonal(j, np.nan)
    return j


def within_across(j: np.ndarray, groups: np.ndarray, mask: np.ndarray | None = None) -> tuple[float, float]:
    """Mean similarity of pairs in the same group and in different groups (upper triangle only)."""
    iu = np.triu_indices(len(groups), 1)
    same = groups[iu[0]] == groups[iu[1]]
    keep = ~np.isnan(j[iu])
    if mask is not None:
        keep &= mask[iu[0]] & mask[iu[1]]
    vals = j[iu]
    return float(vals[keep & same].mean()), float(vals[keep & ~same].mean())


def permutation_p(j: np.ndarray, groups: np.ndarray, runs: int, rng: np.random.Generator) -> float:
    """Share of label shuffles whose within-group mean reaches the observed one (one-sided, +1 smoothing)."""
    observed = within_across(j, groups)[0]
    hits = sum(within_across(j, rng.permutation(groups))[0] >= observed for _ in range(runs))
    return (hits + 1) / (runs + 1)


def excess_by_status(j: np.ndarray, groups: np.ndarray, status: np.ndarray) -> dict:
    """Within minus across similarity for pairs where both repositories have, or both lack, a status."""
    out = {}
    for key, mask in (("with", status), ("without", ~status)):
        w, a = within_across(j, groups, mask)
        out[key] = {"within": w, "across": a, "excess": w - a}
    return out


def status_permutation_p(j: np.ndarray, groups: np.ndarray, status: np.ndarray, runs: int,
                         rng: np.random.Generator) -> float:
    """Two-sided p for the difference in excess between the two statuses, shuffling status within groups."""
    def diff(st):
        e = excess_by_status(j, groups, st)
        return e["with"]["excess"] - e["without"]["excess"]
    observed = diff(status)
    idx = [np.flatnonzero(groups == g) for g in np.unique(groups)]
    hits = 0
    for _ in range(runs):
        st = status.copy()
        for ix in idx:
            st[ix] = rng.permutation(status[ix])
        hits += abs(diff(st)) >= abs(observed)
    return (hits + 1) / (runs + 1)


def distinctive_items(sets: list[set], groups: np.ndarray, min_share: float, min_lift: float, top: int) -> pd.DataFrame:
    """Items used by at least min_share of a group's repositories and min_lift times as often as elsewhere."""
    rows = []
    for g in np.unique(groups):
        inside = [s for s, gg in zip(sets, groups) if gg == g]
        outside = [s for s, gg in zip(sets, groups) if gg != g]
        counts = pd.Series([i for s in inside for i in s]).value_counts()
        for item, n in counts.items():
            share_in = n / len(inside)
            if share_in < min_share:
                break
            share_out = sum(item in s for s in outside) / len(outside)
            lift = share_in / share_out if share_out else np.inf
            if lift >= min_lift:
                rows.append({"group": g, "item": item, "share_in": share_in, "share_out": share_out, "lift": lift})
    df = pd.DataFrame(rows)
    return df.sort_values(["group", "share_in"], ascending=[True, False]).groupby("group").head(top) if len(df) else df
