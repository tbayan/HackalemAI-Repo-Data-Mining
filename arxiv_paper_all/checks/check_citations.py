"""Fail if the paper cites anything that has not been verified.

Every entry in latex/references.bib must carry `verified = {yes}` (a custom
field BibTeX ignores) and a `doi` or `url`. Every \\cite key used in the .tex
files must exist in the .bib. Unused entries are reported as warnings.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
BIB = PAPER / "latex" / "references.bib"
TEX = [PAPER / "latex" / "main.tex", *sorted((PAPER / "latex" / "sections").glob("*.tex"))]

ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", re.DOTALL)
CITE = re.compile(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]*)\}")


def field(body: str, name: str) -> str | None:
    """Value of a braced or quoted field, anywhere on its line (Crossref writes one-line entries)."""
    m = re.search(rf"\b{name}\s*=\s*([{{\"])", body, re.IGNORECASE)
    if not m:
        return None
    i = m.end()
    if m.group(1) == '"':
        end = body.find('"', i)
        return body[i:end].strip() if end >= 0 else None
    depth = 1
    while i < len(body) and depth:
        depth += {"{": 1, "}": -1}.get(body[i], 0)
        i += 1
    return body[m.end():i - 1].strip() if depth == 0 else None


def main() -> int:
    entries = {}
    if BIB.exists():
        for kind, key, body in ENTRY.findall(BIB.read_text(encoding="utf-8")):
            entries[key] = body
    errors, warnings = [], []
    for key, body in entries.items():
        if (field(body, "verified") or "").lower() != "yes":
            errors.append(f"{key}: not marked verified = {{yes}}")
        if not (field(body, "doi") or field(body, "url")):
            errors.append(f"{key}: no doi or url")
    cited = set()
    for path in TEX:
        if path.exists():
            text = re.sub(r"(?<!\\)%.*$", "", path.read_text(encoding="utf-8"), flags=re.MULTILINE)
            for group in CITE.findall(text):
                cited.update(k.strip() for k in group.split(",") if k.strip())
    for key in sorted(cited - entries.keys()):
        errors.append(f"{key}: cited but missing from references.bib")
    for key in sorted(entries.keys() - cited):
        warnings.append(f"{key}: in references.bib but never cited")
    for e in errors:
        print("ERROR  ", e)
    for w in warnings:
        print("warning", w)
    print(f"citation check: {len(entries)} entries, {len(cited)} cited, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
