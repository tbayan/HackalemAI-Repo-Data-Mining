"""Fail if the paper uses any word or phrase from writing/banned_words.txt.

Scans latex/*.tex and latex/sections/*.tex, ignoring LaTeX comments and the
arguments of \\cite, \\ref, \\label and \\url. Exit code 1 lists every hit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
BANNED = PAPER / "writing" / "banned_words.txt"
TEX_GLOBS = ["latex/*.tex", "latex/sections/*.tex", "figures/*.tex"]
SKIP_FILES = {"numbers.tex"}

COMMENT = re.compile(r"(?<!\\)%.*$")
COMMAND_ARGS = re.compile(r"\\(?:cite[tp]?|ref|cref|Cref|label|url|href|input|include)\{[^}]*\}")
# TikZ/LaTeX option keys are code, not prose (e.g. "align=left").
OPTION_KEYS = re.compile(r"\balign\s*=\s*\w+")


def load_patterns() -> list[tuple[str, re.Pattern]]:
    patterns = []
    for line in BANNED.read_text(encoding="utf-8").splitlines():
        term = line.split("#", 1)[0].strip()
        if term:
            patterns.append((term, re.compile(rf"\b{term}\b", re.IGNORECASE)))
    return patterns


def main() -> int:
    patterns = load_patterns()
    hits = []
    for glob in TEX_GLOBS:
        for path in sorted(PAPER.glob(glob)):
            if path.name in SKIP_FILES:
                continue
            for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                line = OPTION_KEYS.sub(" ", COMMAND_ARGS.sub(" ", COMMENT.sub("", raw)))
                for term, pattern in patterns:
                    for m in pattern.finditer(line):
                        hits.append(f"{path.relative_to(PAPER)}:{n}: '{m.group(0)}' (rule: {term})")
    for hit in hits:
        print(hit)
    print(f"banned-word check: {len(hits)} hit(s) in {len(patterns)} rules")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
