"""Phase 6: Final combined summary across all analysis outputs.

Run this last, after fetch_repos / fetch_commit_counts / analyze_buckets /
fetch_commit_timings / analyze_timing / fetch_readmes / extract_tracks have
all completed. Prints one console summary tying every metric together.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    repos = pd.read_csv(DATA_DIR / "repos.csv")
    counts = pd.read_csv(DATA_DIR / "commit_counts.csv")
    buckets = pd.read_csv(DATA_DIR / "bucket_summary.csv")

    total_teams = len(repos)
    active_teams = int((counts["commit_count"] > 1).sum())

    print("=" * 60)
    print("HACKALEMAI ASTANA — FINAL SUMMARY")
    print("=" * 60)
    print(f"Total registered teams:      {total_teams}")
    print(f"Teams that actually committed: {active_teams} "
          f"({active_teams/total_teams*100:.1f}%)")
    print()
    print("-- Commit count buckets --")
    print(buckets.to_string(index=False))

    timestamps_file = DATA_DIR / "commit_timestamps.csv"
    if timestamps_file.exists():
        ts = pd.read_csv(timestamps_file, parse_dates=["committed_at"])
        peak_hour = ts["committed_at"].dt.hour.value_counts().idxmax()
        print()
        print("-- Commit timing --")
        print(f"Commits analyzed: {len(ts)} across {ts['name'].nunique()} repos")
        print(f"Peak commit hour (UTC): {peak_hour}:00")
        print(f"Window: {ts['committed_at'].min()} -> {ts['committed_at'].max()}")

    tracks_file = DATA_DIR / "tracks_summary.csv"
    if tracks_file.exists():
        tracks = pd.read_csv(tracks_file)
        print()
        print("-- Top tracks/clusters --")
        print(tracks.head(10).to_string(index=False))

    print("=" * 60)


if __name__ == "__main__":
    main()
