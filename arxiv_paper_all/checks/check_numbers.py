"""Fail if the paper's prose contains a number that is not generated or allowed.

Data numbers must come from macros in latex/numbers.tex. Literal numbers that
are not data (years, "12 tracks", event times) must be listed with a source in
writing/allowed_literals.txt. Table and figure files are generated, so only
latex/sections/*.tex and latex/main.tex are scanned.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
ALLOWED = PAPER / "writing" / "allowed_literals.txt"
FILES = [PAPER / "latex" / "main.tex", *sorted((PAPER / "latex" / "sections").glob("*.tex"))]

COMMENT = re.compile(r"(?<!\\)%.*$")
# Commands whose arguments are identifiers or layout, not claims.
SKIP_ARGS = re.compile(
    r"\\(?:cite[tp]?|ref|cref|Cref|label|url|href|input|include|includegraphics|"
    r"begin|end|hspace|vspace|setlength|documentclass|usepackage)(?:\[[^\]]*\])?\{[^}]*\}"
)
MACRO = re.compile(r"\\[A-Za-z]+")  # generated macros are letters only, e.g. \NReposTotal
# A number not glued to a letter on the left (so RQ1, C2, Fig. 3 labels are fine).
NUMBER = re.compile(r"(?<![A-Za-z0-9\\])\d+(?:[.,:]\d+)*")


def load_allowed() -> set[str]:
    allowed = set()
    for line in ALLOWED.read_text(encoding="utf-8").splitlines():
        token = line.split("#", 1)[0].strip()
        if token:
            allowed.add(token)
    return allowed


def main() -> int:
    allowed = load_allowed()
    problems = []
    for path in FILES:
        if not path.exists():
            continue
        in_skip_env = False
        for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = COMMENT.sub("", raw)
            if re.search(r"\\begin\{(figure|table|tikzpicture)\*?\}", line):
                in_skip_env = True
            if in_skip_env:
                if re.search(r"\\end\{(figure|table|tikzpicture)\*?\}", line):
                    in_skip_env = False
                # captions are prose: still check them
                captions = re.findall(r"\\caption\{(.*)\}", line)
                line = " ".join(captions)
            line = MACRO.sub(" ", SKIP_ARGS.sub(" ", line))
            for m in NUMBER.finditer(line):
                if m.group(0) not in allowed:
                    problems.append(f"{path.relative_to(PAPER)}:{n}: '{m.group(0)}'")
    for p in problems:
        print(p)
    print(f"number check: {len(problems)} unapproved literal number(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
