"""Phase 5c: Chart the officially published 12 hackathon tracks.

Unlike extract_tracks.py (which infers tracks from README text-mining because
most repos never stated one), the track *labels* here (partner/task) come
from an authoritative external source, but the repo *counts* are derived
directly from data/hackalem_repos_analysis.csv — a per-repo `case_guess`
column that maps each repo to a track using its commit-timing pattern. That
keeps the chart traceable to raw per-repo data instead of a hand-typed total.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from plotting import FG_COLOR, PALETTE, new_square_figure, save

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
META_FILE = DATA_DIR / "official_tracks.csv"
REPOS_FILE = DATA_DIR / "hackalem_repos_analysis.csv"
OUT_FILE = DATA_DIR / "official_tracks_summary.csv"
CHART_DIR = Path(__file__).resolve().parent.parent / "charts"
CHART_FILE = CHART_DIR / "official_tracks_distribution.png"

CODE_PATTERN = re.compile(r"^(\d{2})\b")


def track_code(label: str) -> str | None:
    match = CODE_PATTERN.match(str(label).strip())
    return match.group(1) if match else None


def main() -> None:
    meta = pd.read_csv(META_FILE)
    meta["code"] = meta["track"].apply(track_code)
    hand_entered_counts = meta.set_index("code")["repo_count"]

    repos = pd.read_csv(REPOS_FILE)
    repos["code"] = repos["case_guess"].apply(track_code)

    # Repos whose case_guess isn't one of the 12 numeric track codes (no
    # commits in the event window, commits outside the window, or an
    # ambiguous match) — reported separately, not part of the 12 tracks.
    non_track = repos[repos["code"].isna()]["case_guess"].value_counts()

    verified_counts = repos.dropna(subset=["code"]).groupby("code").size()
    meta["repo_count"] = meta["code"].map(verified_counts).fillna(0).astype(int)

    mismatches = meta.set_index("code")["repo_count"].compare(hand_entered_counts)
    if not mismatches.empty:
        print(f"WARNING: repo_count mismatches vs hand-entered totals:\n{mismatches}")
    else:
        print("Verified: per-repo counts match the hand-entered totals exactly.")

    df = meta.sort_values("repo_count", ascending=False)
    df[["track", "partner", "task", "repo_count"]].to_csv(OUT_FILE, index=False)

    total = df["repo_count"].sum()
    print(df[["track", "partner", "repo_count"]].to_string(index=False))
    print(f"Total repos matched to one of the 12 official tracks: {total}")
    print("Repos not matched to a track (by reason):")
    print(non_track.to_string())

    plot_df = df.iloc[::-1]  # reverse for horizontal bar top-to-bottom (largest on top)
    labels = [
        f"{track} ({partner})"
        for track, partner in zip(plot_df["track"], plot_df["partner"])
    ]

    CHART_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = new_square_figure(
        "BAITC Hacks — Official Tracks",
        subtitle=f"Repos matched per track via commit-timing (n={total})",
    )
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(plot_df))]
    bars = ax.barh(labels, plot_df["repo_count"], color=colors)
    ax.set_xlabel("Repos")
    ax.tick_params(axis="y", labelsize=12)
    for bar, count in zip(bars, plot_df["repo_count"]):
        ax.text(
            bar.get_width() + total * 0.01,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center",
            fontsize=11,
            color=FG_COLOR,
        )
    save(fig, str(CHART_FILE))


if __name__ == "__main__":
    main()
