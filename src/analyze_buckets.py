"""Phase 3: Bucket repos by commit count -> data/bucket_summary.csv + chart.

Bucket "1 (template only)" is kept separate from the rest since every repo in
this org starts with exactly one auto-generated commit; a repo with
commit_count == 1 never had a human commit on top of the template.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from plotting import PALETTE, new_square_figure, save

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"
REPOS_FILE = DATA_DIR / "repos.csv"
COUNTS_FILE = DATA_DIR / "commit_counts.csv"
OUT_FILE = DATA_DIR / "bucket_summary.csv"
CHART_FILE = CHARTS_DIR / "commit_buckets.png"

BIN_EDGES = [0, 1, 5, 10, 15, 20, 30, 50, 100, float("inf")]
BIN_LABELS = [
    "1 (template only)",
    "2-5",
    "6-10",
    "11-15",
    "16-20",
    "21-30",
    "31-50",
    "51-100",
    "101+",
]


def main() -> None:
    repos = pd.read_csv(REPOS_FILE)
    counts = pd.read_csv(COUNTS_FILE)
    df = repos.merge(counts, on="name", how="left")

    total_repos = len(df)
    no_data = int((df["commit_count"] == -1).sum())
    valid = df[df["commit_count"] != -1].copy()

    valid["bucket"] = pd.cut(
        valid["commit_count"], bins=BIN_EDGES, labels=BIN_LABELS, right=True
    )

    summary = (
        valid.groupby("bucket", observed=True)
        .size()
        .reindex(BIN_LABELS, fill_value=0)
        .rename("repo_count")
        .reset_index()
        .rename(columns={"index": "bucket"})
    )
    summary["pct_of_total"] = (summary["repo_count"] / total_repos * 100).round(2)

    active_total = int((valid["commit_count"] > 1).sum())
    inactive_total = int((valid["commit_count"] <= 1).sum())

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_FILE, index=False)

    print(f"Total registered teams (repos): {total_repos}")
    print(f"Repos with unresolved commit data: {no_data}")
    print(f"Active teams (commit_count > 1): {active_total} "
          f"({active_total/total_repos*100:.1f}%)")
    print(f"Inactive teams (commit_count <= 1): {inactive_total} "
          f"({inactive_total/total_repos*100:.1f}%)")
    print(summary.to_string(index=False))

    # --- Chart ---
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = new_square_figure(
        title="Hackalemai Astana — Commit Activity",
        subtitle=(
            f"{total_repos} teams registered · {active_total} actually committed code "
            f"({active_total/total_repos*100:.0f}%)"
        ),
    )
    bars = ax.bar(
        summary["bucket"].astype(str),
        summary["repo_count"],
        color=PALETTE[: len(summary)],
        edgecolor="none",
    )
    for bar, pct in zip(bars, summary["pct_of_total"]):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + total_repos * 0.005,
            f"{int(height)}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=11,
            color="#F5F5F7",
        )
    ax.set_ylabel("Number of repos")
    ax.set_xlabel("Commits per repo")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    save(fig, str(CHART_FILE))

    # --- Second chart: zoom into active teams only (drop the dominant
    # "template only" bar so the real distribution is legible) ---
    active_summary = summary[summary["bucket"] != "1 (template only)"].copy()
    active_summary["pct_of_active"] = (
        active_summary["repo_count"] / active_total * 100
    ).round(2)

    fig2, ax2 = new_square_figure(
        title="Hackalemai Astana — Active Teams Only",
        subtitle=f"{active_total} teams with real commits, by commit-count range",
    )
    bars2 = ax2.bar(
        active_summary["bucket"].astype(str),
        active_summary["repo_count"],
        color=PALETTE[1: len(active_summary) + 1],
        edgecolor="none",
    )
    for bar, pct in zip(bars2, active_summary["pct_of_active"]):
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            height + active_summary["repo_count"].max() * 0.02,
            f"{int(height)}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=12,
            color="#F5F5F7",
        )
    ax2.set_ylabel("Number of repos")
    ax2.set_xlabel("Commits per repo")
    plt.setp(ax2.get_xticklabels(), rotation=25, ha="right")
    save(fig2, str(CHARTS_DIR / "commit_buckets_active_only.png"))


if __name__ == "__main__":
    main()
