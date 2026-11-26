"""Check of the LLM-coded approaches: companion file for the blind coding.

For each of the 60 sampled repositories, writes the full cleaned README (the same cleaning as the model's input,
but not cut at 2,500 characters), the brief and the full file list to one HTML page, ordered by item number.
The coder decides from the excerpt in the sheet first and opens this page only when the excerpt does not show
the method. The model's answers are not included. The output links items to README text and stays private.

    python llm_validation_full_readmes.py <repository root> <output folder>
"""
from __future__ import annotations

import csv
import html
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUTDIR = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(ROOT / "src"))
import llm_codebook as lc  # noqa: E402  (same cleaning as the coding run)

NAMES = {"01": "Energy", "02": "Finance", "03": "Management", "04": "Telecom", "05": "Logistics",
         "06": "Creative industries", "07": "Education", "08": "Innovation", "09": "Communications",
         "10": "Trade", "11": "Special (structure)", "12": "Special (city)"}

key = sorted(csv.DictReader((ROOT / "data/llm_codebook/validation_key.csv").open(encoding="utf-8")),
             key=lambda r: int(r["item"]))
brief = lc.briefs()
parts = ["<!doctype html><html><head><meta charset='utf-8'><title>Full READMEs for the 60 items</title>",
         "<style>body{font-family:system-ui,sans-serif;max-width:60rem;margin:auto;padding:1rem;line-height:1.45}"
         "pre{white-space:pre-wrap;background:#f6f6f6;padding:.8rem;border-radius:6px}"
         "h2{border-top:2px solid #ccc;padding-top:1rem}.b{color:#444}nav a{margin-right:.4rem}</style></head><body>",
         "<h1>Full READMEs for the 60 items (companion to the labelling sheet)</h1>",
         "<p>Same cleaning as the model's input (code blocks, links, images, e-mails and handles removed), but "
         "<b>not cut</b> at 2,500 characters, and the full file list. The model's answers are not here.</p><nav>"]
parts += [f"<a href='#i{r['item']}'>{r['item']}</a>" for r in key]
parts.append("</nav>")
cut = 0
for r in key:
    paths = [p for p in lc.git(r["repo"], "ls-tree", "-r", "--name-only", "HEAD").splitlines() if not lc.VENDORED.search(p)]
    readme = next((p for p in paths if re.fullmatch(r"(?i)readme(\.(md|markdown|txt|rst))?", p)), None)
    full = lc.clean_readme(lc.git(r["repo"], "show", f"HEAD:{readme}")) if readme else ""
    cut += len(full) > lc.README_CHARS
    parts.append(f"<h2 id='i{r['item']}'>Item {r['item']} · T{int(r['track'])} {NAMES[r['track']]}</h2>")
    parts.append(f"<p class='b'><b>Brief:</b> {html.escape(brief.get(r['track'], ''))}</p>")
    parts.append(f"<p><b>README</b> ({len(full):,} characters; the model saw the first {lc.README_CHARS:,})</p>"
                 f"<pre>{html.escape(full)}</pre>")
    parts.append(f"<details><summary><b>All files</b> ({len(paths)})</summary>"
                 f"<pre>{html.escape(chr(10).join(paths[:400]))}</pre></details>")
parts.append("</body></html>")
OUTDIR.mkdir(parents=True, exist_ok=True)
out = OUTDIR / "LLM_validation_full_READMEs.html"
out.write_text("".join(parts), encoding="utf-8")
print(f"written {out}; {cut} of {len(key)} READMEs are longer than the {lc.README_CHARS:,} characters the model saw")
