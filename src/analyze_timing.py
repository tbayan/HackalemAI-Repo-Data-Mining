"""Phase 4b: Analyze commit timing -> hourly activity + day x hour heatmap.

Reads data/commit_timestamps.csv (committedDate in ISO8601 UTC) and produces
two charts: overall hour-of-day histogram, and a day x hour heatmap covering
the hackathon window.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from plotting import BG_COLOR, FG_COLOR, GRID_COLOR, PALETTE, new_square_figure, save

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"
TIMESTAMPS_FILE = DATA_DIR / "commit_timestamps.csv"


def main() -> None:
    df = pd.read_csv(TIMESTAMPS_FILE, parse_dates=["committed_at"])
    df["hour"] = df["committed_at"].dt.hour
    df["date"] = df["committed_at"].dt.date

    print(f"Loaded {len(df)} commit timestamps across {df['name'].nunique()} repos")
    print(f"Date range: {df['committed_at'].min()} -> {df['committed_at'].max()}")

    # --- Chart 1: hour-of-day histogram ---
    hourly = df.groupby("hour").size().reindex(range(24), fill_value=0)
    fig, ax = new_square_figure(
        title="Hackalemai Astana — When Did Teams Code?",
        subtitle="Commits by hour of day (UTC), across all active teams",
    )
    ax.bar(hourly.index, hourly.values, color=PALETTE[0], width=0.8)
    ax.set_xlabel("Hour of day (UTC)")
    ax.set_ylabel("Number of commits")
    ax.set_xticks(range(0, 24, 2))
    save(fig, str(CHARTS_DIR / "hourly_activity.png"))

    # --- Chart 2: day x hour heatmap ---
    pivot = df.pivot_table(
        index="date", columns="hour", values="name", aggfunc="count", fill_value=0
    )
    pivot = pivot.reindex(columns=range(24), fill_value=0)

    plt.rcParams.update({
        "font.size": 14,
        "text.color": FG_COLOR,
        "axes.labelcolor": FG_COLOR,
        "xtick.color": FG_COLOR,
        "ytick.color": FG_COLOR,
    })
    fig2, ax2 = plt.subplots(figsize=(10.8, 10.8), dpi=100)
    fig2.patch.set_facecolor(BG_COLOR)
    ax2.set_facecolor(BG_COLOR)
    sns.heatmap(
        pivot,
        cmap="magma",
        ax=ax2,
        cbar_kws={"label": "commits"},
        linewidths=0.5,
        linecolor=BG_COLOR,
    )
    fig2.suptitle(
        "Hackalemai Astana — Commit Heatmap", fontsize=24, fontweight="bold",
        color=FG_COLOR, y=0.97,
    )
    ax2.set_title("Commits per day x hour (UTC)", fontsize=14, color="#B4B6C9", pad=14)
    ax2.set_xlabel("Hour of day (UTC)")
    ax2.set_ylabel("Date")
    save(fig2, str(CHARTS_DIR / "commit_timing_heatmap.png"))


if __name__ == "__main__":
    main()
