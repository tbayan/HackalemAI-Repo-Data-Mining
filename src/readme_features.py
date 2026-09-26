"""Phase M2d: README language and completeness at each repo's final state -> data/readme_features.csv

Reads the root README on the default-branch HEAD of every active repo. Code
blocks, inline code, URLs and HTML tags are removed before counting letters.

Language rule (validated by hand on a sample, see data/readme_lang_sample.csv):
- kazakh:  at least 3% of Cyrillic letters are Kazakh-specific (ә ғ қ ң ө ұ ү һ і)
- russian: Cyrillic letters are at least half of all letters (and not kazakh)
- english: Latin letters are at least 80% of all letters
- mixed:   anything else (e.g. Russian prose with long English passages)
Only features are stored; README text stays in the private clones.
"""
from __future__ import annotations

import csv
import random
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from tqdm import tqdm

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLONE_DIR = DATA_DIR / "clones"
TABLE = DATA_DIR / "repo_table.csv"
OUT_FILE = DATA_DIR / "readme_features.csv"
SAMPLE_FILE = DATA_DIR / "readme_lang_sample.csv"

KAZAKH = re.compile(r"[әғқңөұүһіӘҒҚҢӨҰҮҺІ]")
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
LATIN = re.compile(r"[A-Za-z]")
CODE_BLOCK = re.compile(r"```.*?```|~~~.*?~~~", re.S)
NOISE = re.compile(r"`[^`\n]*`|https?://\S+|<[^>]+>|!\[[^\]]*\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)")
INSTALL = re.compile(r"\b(install|setup|run|quick ?start|getting started)\b|установ|запуск|орнат|іске қос|"
                     r"npm (i|install|run)|pip install|docker(-| )compose|uvicorn|python3? \S+\.py", re.I)
DEPLOYED = re.compile(r"https?://[^\s)]*(vercel\.app|netlify\.app|onrender\.com|streamlit\.app|railway\.app|"
                      r"fly\.dev|pages\.dev|herokuapp\.com|github\.io|replit\.app|ngrok)", re.I)
DEMO_WORD = re.compile(r"\b(demo|live|deployed)\b|демо|жив", re.I)
VIDEO = re.compile(r"youtube\.com|youtu\.be|loom\.com|drive\.google\.com", re.I)
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)|<img\s", re.I)
AGENT_MENTION = re.compile(r"\bcodex\b|\bclaude\b|agents\.md|\bcopilot\b|\bcursor\b", re.I)


def git(git_dir: Path, *args: str) -> str:
    return subprocess.run(["git", f"--git-dir={git_dir}", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def language(prose: str) -> tuple[str, int, int, int]:
    kz, cy, la = len(KAZAKH.findall(prose)), len(CYRILLIC.findall(prose)), len(LATIN.findall(prose))
    cyr = kz + cy
    total = cyr + la
    if total < 20:
        return "too_short", kz, cy, la
    if cyr and kz / cyr >= 0.03:
        return "kazakh", kz, cy, la
    if cyr / total >= 0.5:
        return "russian", kz, cy, la
    if la / total >= 0.8:
        return "english", kz, cy, la
    return "mixed", kz, cy, la


def process(name: str) -> dict:
    git_dir = CLONE_DIR / f"{name}.git"
    root = git(git_dir, "ls-tree", "--name-only", "HEAD").split("\n")
    readme = next((p for p in root if re.fullmatch(r"readme(\.[a-z]+)?", p, re.I)), None)
    text = git(git_dir, "show", f"HEAD:{readme}") if readme else ""
    prose = NOISE.sub(r" \1 ", CODE_BLOCK.sub(" ", text))
    lang, kz, cy, la = language(prose) if text.strip() else ("no_readme", 0, 0, 0)
    template_only = bool(re.fullmatch(r"#\s*hack-[0-9a-f]{8}-\S+\s*\nHackathon team repository for[^\n]*\n?", text.strip() + "\n"))
    return {
        "repo": name, "readme": int(bool(readme)), "template_only": int(template_only),
        "language": "template" if template_only else lang,
        "kazakh_letters": kz, "cyrillic_letters": cy, "latin_letters": la,
        "words": len(prose.split()), "headings": len(re.findall(r"^#{1,6}\s", text, re.M)),
        "code_blocks": len(CODE_BLOCK.findall(text)),
        "install_instructions": int(bool(INSTALL.search(text))),
        "deployed_link": int(bool(DEPLOYED.search(text))),
        "demo_mention": int(bool(DEMO_WORD.search(text))),
        "video_link": int(bool(VIDEO.search(text))),
        "images": len(IMAGE.findall(text)),
        "mentions_agent_tool": int(bool(AGENT_MENTION.search(text))),
    }


def main() -> None:
    with TABLE.open(encoding="utf-8") as f:
        names = [r["repo"] for r in csv.DictReader(f) if int(r["team_commits"]) > 0]
    with ProcessPoolExecutor() as pool:
        rows = list(tqdm(pool.map(process, names, chunksize=16), total=len(names), desc="READMEs", unit="repo"))
    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    # Stratified validation sample for hand-labelling (private: excerpts can contain names).
    rng = random.Random(2026)
    by_lang: dict[str, list[dict]] = {}
    for r in rows:
        by_lang.setdefault(r["language"], []).append(r)
    quota = {"english": 35, "russian": 35, "mixed": 15, "kazakh": 15}
    sample = []
    for lang, k in quota.items():
        pool = by_lang.get(lang, [])
        sample += rng.sample(pool, min(k, len(pool)))
    with SAMPLE_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["repo", "auto_language", "excerpt", "human_language"])
        for r in sample:
            text = git(CLONE_DIR / f"{r['repo']}.git", "show", "HEAD:README.md")
            excerpt = " ".join(NOISE.sub(" ", CODE_BLOCK.sub(" ", text)).split())[:400]
            writer.writerow([r["repo"], r["language"], excerpt, ""])
    print(f"Wrote {len(rows)} repos -> {OUT_FILE}; {len(sample)}-row validation sample -> {SAMPLE_FILE}")


if __name__ == "__main__":
    main()
