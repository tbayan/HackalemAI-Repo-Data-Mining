"""Phase M2c (check): Estimate how many provider-specific findings are placeholders.

For each non-generic finding, the matched line is read locally from the clone
and the candidate string is classified as a placeholder (contains xxxx, "your",
"example", "...", angle brackets, or has low character entropy) or as plausible.
Candidate values are held in memory only: nothing but the class is written, and
nothing is printed except counts. Keys are never tested against any service.
Output: data/secrets_private/precision.csv (finding index, rule, class).
"""
from __future__ import annotations

import csv
import math
import re
import subprocess
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FINDINGS = DATA_DIR / "secrets_private" / "findings.csv"
OUT = DATA_DIR / "secrets_private" / "precision.csv"

CANDIDATE = {
    "openai-api-key": re.compile(r"sk-[A-Za-z0-9_\-*.<>]{16,}"),
    "gcp-api-key": re.compile(r"AIza[0-9A-Za-z_\-*.<>]{20,}"),
    "telegram-bot-api-token": re.compile(r"\d{6,}:[A-Za-z0-9_\-*.<>]{20,}"),
    "stripe-access-token": re.compile(r"[rs]k_(live|test)_[A-Za-z0-9*.<>]{10,}"),
}
PLACEHOLDER = re.compile(r"x{4,}|X{4,}|your|example|dummy|placeholder|fake|sample|changeme|\.\.\.|<|>|\*{3,}", re.I)


def entropy(s: str) -> float:
    counts = Counter(s)
    return -sum(c / len(s) * math.log2(c / len(s)) for c in counts.values())


def classify(rule: str, line: str) -> str:
    pattern = CANDIDATE.get(rule)
    match = pattern.search(line) if pattern else None
    text = match.group(0) if match else line.strip()
    if PLACEHOLDER.search(text):
        return "placeholder"
    return "plausible" if entropy(text) >= 3.5 else "placeholder"


def main() -> None:
    rows, classes = [], Counter()
    with FINDINGS.open(encoding="utf-8") as f:
        for i, finding in enumerate(csv.DictReader(f)):
            if finding["rule_id"] == "generic-api-key":
                continue
            blob = subprocess.run(
                ["git", f"--git-dir={DATA_DIR / 'clones' / (finding['repo'] + '.git')}", "show",
                 f"{finding['commit']}:{finding['file']}"],
                capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines()
            line_no = int(finding["line"] or 0)
            line = blob[line_no - 1] if 0 < line_no <= len(blob) else ""
            label = classify(finding["rule_id"], line) if line else "unreadable"
            rows.append({"finding": i, "rule_id": finding["rule_id"], "class": label})
            classes[(finding["rule_id"], label)] += 1
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["finding", "rule_id", "class"])
        writer.writeheader()
        writer.writerows(rows)
    for (rule, label), n in sorted(classes.items()):
        print(f"{rule:24s} {label:12s} {n}")


if __name__ == "__main__":
    main()
