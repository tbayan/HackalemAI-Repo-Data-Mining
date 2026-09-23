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
        ts["local_time"] = ts["committed_at"] + pd.Timedelta(hours=5)  # Astana, UTC+5
        peak_local_hour = ts["local_time"].dt.hour.value_counts().idxmax()
        main_day = ts["local_time"].dt.date.value_counts().idxmax()
        main_day_count = int(ts["local_time"].dt.date.value_counts().max())
        in_window = ts["local_time"].dt.hour.between(13, 18).sum()
        print()
        print("-- Commit timing --")
        print(f"Commits analyzed: {len(ts)} across {ts['name'].nunique()} repos")
        print(f"Main event day (Astana local): {main_day} "
              f"({main_day_count/len(ts)*100:.1f}% of all commits)")
        print(f"Peak commit hour (Astana local, UTC+5): {peak_local_hour}:00")
        print(f"Commits within 13:00-18:00 local event window: {in_window} "
              f"({in_window/len(ts)*100:.1f}% of all commits)")
        print(f"Peak commit hour (UTC): {peak_hour}:00")
        print(f"Window: {ts['committed_at'].min()} -> {ts['committed_at'].max()}")

    tracks_file = DATA_DIR / "tracks_summary.csv"
    if tracks_file.exists():
        tracks = pd.read_csv(tracks_file)
        print()
        print("-- Top tracks/clusters (from README text-mining) --")
        print(tracks.head(10).to_string(index=False))

    official_file = DATA_DIR / "official_tracks_summary.csv"
    if official_file.exists():
        official = pd.read_csv(official_file)
        print()
        print("-- Official tracks (verified via per-repo commit-timing match) --")
        print(official[["track", "partner", "repo_count"]].to_string(index=False))

    repo_analysis_file = DATA_DIR / "hackalem_repos_analysis.csv"
    if repo_analysis_file.exists():
        analysis = pd.read_csv(repo_analysis_file)
        matched = analysis["case_guess"].str.match(r"^\d{2}\b").sum()
        print()
        print("-- Event-window participation (from commit-timing analysis) --")
        print(f"Matched to one of the 12 official tracks: {matched}")
        print(analysis.loc[~analysis["case_guess"].str.match(r"^\d{2}\b"),
                            "case_guess"].value_counts().to_string())

    print("=" * 60)


if __name__ == "__main__":
    main()
