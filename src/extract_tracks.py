"""Phase 5b: Extract the 10 hackathon tracks/questions from README text.

Pass A: regex scan for explicit "Track:" / "Challenge:" / "Topic:" style
headers that the org's README template likely contains verbatim.
Pass B: for READMEs without an explicit tag, TF-IDF vectorize + KMeans(k=10)
cluster the remaining text and label each cluster by its top TF-IDF terms.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from plotting import PALETTE, new_square_figure, save

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
README_DIR = DATA_DIR / "readmes"
OUT_FILE = DATA_DIR / "tracks_summary.csv"
ASSIGNMENTS_FILE = DATA_DIR / "track_assignments.csv"
CHART_DIR = Path(__file__).resolve().parent.parent / "charts"
CHART_FILE = CHART_DIR / "tracks_distribution.png"

N_CLUSTERS = 10

# Matches lines like "Track: Fintech", "## Challenge - Health", "Topic: XYZ"
TRACK_PATTERN = re.compile(
    r"(?:^|\n)\s*#{0,3}\s*(?:\*\*)?(track|challenge|topic|nomination|track name)"
    r"(?:\*\*)?\s*[:#\-–]\s*(?:\*\*)?([^\n*#]{3,80})",
    re.IGNORECASE,
)

CUSTOM_STOPWORDS = {
    "hackathon", "team", "project", "repo", "repository", "readme", "hack",
    "baitc", "hacks", "astana", "2026", "code", "codebase", "solution",
}
STOP_WORDS = list(ENGLISH_STOP_WORDS | CUSTOM_STOPWORDS)


def load_readmes() -> dict[str, str]:
    texts = {}
    for path in README_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8", errors="ignore").strip()
        if content:
            texts[path.stem] = content
    return texts


def extract_explicit_track(text: str) -> str | None:
    match = TRACK_PATTERN.search(text)
    if not match:
        return None
    label = match.group(2).strip().strip("*_ ")
    if 2 <= len(label) <= 80:
        return label
    return None


def cluster_remaining(remaining: dict[str, str]) -> dict[str, int]:
    if not remaining:
        return {}
    names = list(remaining.keys())
    docs = list(remaining.values())

    vectorizer = TfidfVectorizer(
        max_df=0.8,
        min_df=2,
        stop_words=STOP_WORDS,
        ngram_range=(1, 2),
        max_features=5000,
    )
    matrix = vectorizer.fit_transform(docs)

    k = min(N_CLUSTERS, len(names))
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(matrix)

    return dict(zip(names, labels)), vectorizer, km, matrix


def top_terms_per_cluster(vectorizer, km, n_terms: int = 6) -> dict[int, list[str]]:
    terms = vectorizer.get_feature_names_out()
    top = {}
    for i, center in enumerate(km.cluster_centers_):
        top_idx = center.argsort()[::-1][:n_terms]
        top[i] = [terms[j] for j in top_idx]
    return top


def main() -> None:
    readmes = load_readmes()
    print(f"Loaded {len(readmes)} README files")

    explicit: dict[str, str] = {}
    remaining: dict[str, str] = {}
    for name, text in readmes.items():
        track = extract_explicit_track(text)
        if track:
            explicit[name] = track
        else:
            remaining[name] = text

    print(f"Explicit track tag found in {len(explicit)} READMEs")
    print(f"Falling back to clustering for {len(remaining)} READMEs")

    cluster_result = cluster_remaining(remaining)
    if cluster_result:
        cluster_labels, vectorizer, km, matrix = cluster_result
        top_terms = top_terms_per_cluster(vectorizer, km)
    else:
        cluster_labels, top_terms = {}, {}

    rows = []
    for name, track in explicit.items():
        rows.append({"name": name, "track_source": "explicit", "track_label": track})
    for name, cluster_id in cluster_labels.items():
        label = "cluster: " + ", ".join(top_terms[cluster_id][:4])
        rows.append({
            "name": name,
            "track_source": f"kmeans_cluster_{cluster_id}",
            "track_label": label,
        })

    assignments = pd.DataFrame(rows)
    assignments.to_csv(ASSIGNMENTS_FILE, index=False)

    explicit_counts = Counter(explicit.values())
    summary_rows = []
    for label, count in explicit_counts.most_common():
        examples = [n for n, t in explicit.items() if t == label][:5]
        summary_rows.append({
            "track_label": label,
            "source": "explicit",
            "repo_count": count,
            "example_repos": ", ".join(examples),
        })
    for cluster_id, terms in top_terms.items():
        count = sum(1 for c in cluster_labels.values() if c == cluster_id)
        examples = [n for n, c in cluster_labels.items() if c == cluster_id][:5]
        summary_rows.append({
            "track_label": "cluster: " + ", ".join(terms[:4]),
            "source": f"kmeans_cluster_{cluster_id}",
            "repo_count": count,
            "example_repos": ", ".join(examples),
        })

    summary = pd.DataFrame(summary_rows).sort_values("repo_count", ascending=False)
    summary.to_csv(OUT_FILE, index=False)
    print(summary.to_string(index=False))
    print(f"Saved -> {OUT_FILE}")

    plot_top = summary.head(10).iloc[::-1]  # reverse for horizontal bar top-to-bottom
    labels = [
        (t[:35] + "…") if len(t) > 35 else t for t in plot_top["track_label"]
    ]
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = new_square_figure(
        "BAITC Hacks — Top Tracks",
        subtitle="Repo count per hackathon track/topic",
    )
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(plot_top))]
    ax.barh(labels, plot_top["repo_count"], color=colors)
    ax.set_xlabel("Repos")
    save(fig, str(CHART_FILE))


if __name__ == "__main__":
    main()
