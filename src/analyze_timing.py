"""Phase 4b: Analyze commit timing -> hourly activity + day x hour heatmap.

Reads data/commit_timestamps.csv (committedDate in ISO8601 UTC), converts to
Astana local time (UTC+5), and produces two charts focused on the
hackathon's actual working window: 13:00-18:00 local time (a single
~5-hour sprint), matching the commits_13_18_local column used in the
official per-repo track analysis (data/hackalem_repos_analysis.csv).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from plotting import BG_COLOR, FG_COLOR, PALETTE, SUBTITLE_COLOR, new_square_figure, save

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"
TIMESTAMPS_FILE = DATA_DIR / "commit_timestamps.csv"

ASTANA_UTC_OFFSET_HOURS = 5
WINDOW_START_HOUR = 13
WINDOW_END_HOUR = 18  # inclusive
WINDOW_HOURS = list(range(WINDOW_START_HOUR, WINDOW_END_HOUR + 1))


def main() -> None:
    df = pd.read_csv(TIMESTAMPS_FILE, parse_dates=["committed_at"])
    df["local_time"] = df["committed_at"] + pd.Timedelta(hours=ASTANA_UTC_OFFSET_HOURS)
    df["local_hour"] = df["local_time"].dt.hour
    df["local_date"] = df["local_time"].dt.date

    print(f"Loaded {len(df)} commit timestamps across {df['name'].nunique()} repos")
    print(f"Raw UTC range: {df['committed_at'].min()} -> {df['committed_at'].max()}")

    day_counts = df["local_date"].value_counts()
    main_day = day_counts.idxmax()
    main_day_count = int(day_counts.max())
    print(
        f"Main event day (Astana local): {main_day} — {main_day_count} commits "
        f"({main_day_count / len(df) * 100:.1f}% of all commits)"
    )

    in_window = df[df["local_hour"].isin(WINDOW_HOURS)]
    print(
        f"Commits within {WINDOW_START_HOUR}:00-{WINDOW_END_HOUR}:00 local time: "
        f"{len(in_window)} ({len(in_window) / len(df) * 100:.1f}% of all commits)"
    )

    # --- Chart 1: hour-of-day histogram, focused on the event window ---
    hourly = df["local_hour"].value_counts().reindex(WINDOW_HOURS, fill_value=0)
    fig, ax = new_square_figure(
        title="Hackalemai Astana — When Did Teams Code?",
        subtitle=(
            f"Commits by hour, Astana local time (UTC+{ASTANA_UTC_OFFSET_HOURS}) "
            f"— official {WINDOW_START_HOUR}:00-{WINDOW_END_HOUR}:00 event window"
        ),
    )
    ax.bar(range(len(WINDOW_HOURS)), hourly.values, color=PALETTE[0], width=0.7)
    ax.set_xlabel("Local time (Astana, UTC+5)")
    ax.set_ylabel("Number of commits")
    ax.set_xticks(range(len(WINDOW_HOURS)))
    ax.set_xticklabels([f"{h:02d}:00" for h in WINDOW_HOURS])
    save(fig, str(CHARTS_DIR / "hourly_activity.png"))

    # --- Chart 2: day x hour heatmap, columns restricted to the event window ---
    pivot = df.pivot_table(
        index="local_date", columns="local_hour", values="name",
        aggfunc="count", fill_value=0,
    )
    pivot = pivot.reindex(columns=WINDOW_HOURS, fill_value=0)
    # Keep only dates with at least one commit in the window, for readability.
    pivot = pivot.loc[(pivot.sum(axis=1) > 0)]

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
        cmap="Blues",
        ax=ax2,
        cbar_kws={"label": "commits"},
        linewidths=0.5,
        linecolor=BG_COLOR,
    )
    fig2.suptitle(
        "Hackalemai Astana — Commit Heatmap", fontsize=24, fontweight="bold",
        color=FG_COLOR, y=0.97,
    )
    ax2.set_title(
        f"Commits per day x hour, Astana local time ({WINDOW_START_HOUR}:00-{WINDOW_END_HOUR}:00 window)",
        fontsize=14, color=SUBTITLE_COLOR, pad=14,
    )
    ax2.set_xticklabels([f"{h:02d}:00" for h in WINDOW_HOURS])
    ax2.set_xlabel("Local time (Astana, UTC+5)")
    ax2.set_ylabel("Date")
    save(fig2, str(CHARTS_DIR / "commit_timing_heatmap.png"))


if __name__ == "__main__":
    main()
