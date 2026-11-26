"""Check of the LLM-coded approaches: blind coding sample.

Draws 5 repositories per track at random (fixed seed) from the 984 coded repositories, leaving out the
48 pilot repositories on which the codebook was tried, and writes
  - LLM_validation_sheet.xlsx  for the author: the same input the model saw (brief, cleaned README excerpt,
                               up to 40 file paths) and empty columns for core_method and llm_role;
                               the model's answers are NOT in this file;
  - data/llm_codebook/validation_key.csv  (private): item -> repository, track and the model's answers.

    python llm_validation_sample.py <repository root> <output folder for the sheet>
"""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUTDIR = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(ROOT / "src"))
import llm_codebook as lc  # noqa: E402  (same input builder and codebook as the coding run)

from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402
from openpyxl.worksheet.datavalidation import DataValidation  # noqa: E402

SEED, PER_TRACK = 20261126, 5
TRACK_NAMES = {"01": "Energy", "02": "Finance", "03": "Management", "04": "Telecom", "05": "Logistics",
               "06": "Creative industries", "07": "Education", "08": "Innovation", "09": "Communications",
               "10": "Trade", "11": "Special (structure)", "12": "Special (city)"}

coded = list(csv.DictReader((ROOT / "data/llm_codebook/all.csv").open(encoding="utf-8")))
coded = [r for r in coded if r["repo"]]
pilot = {r["repo"] for r in csv.DictReader((ROOT / "data/llm_codebook/sample.csv").open(encoding="utf-8"))}
answers = {}
for line in (ROOT / "data/llm_codebook/responses.jsonl").open(encoding="utf-8"):
    rec = json.loads(line)
    if rec["answer"].strip():
        answers[rec["repo"]] = json.loads(rec["answer"])  # last non-empty answer = the one used in the paper
assert len(coded) == 984 and all(r["repo"] in answers for r in coded)

rng = random.Random(SEED)
picked = []
for track in sorted({r["track"] for r in coded}):
    pool = sorted(r["repo"] for r in coded if r["track"] == track and r["repo"] not in pilot)
    picked += [(track, repo) for repo in rng.sample(pool, PER_TRACK)]
rng.shuffle(picked)  # mixed order, so that tracks do not come in blocks

brief = lc.briefs()
rows = []
for item, (track, repo) in enumerate(picked, start=1):
    readme, paths = lc.repo_input(repo)
    rows.append({"item": item, "track": track, "repo": repo, "brief": brief.get(track, ""),
                 "readme": readme, "paths": "\n".join(paths)})

# private key (data/ is not part of the public repository)
key = ROOT / "data/llm_codebook/validation_key.csv"
with key.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["item", "track", "repo", "model_core_method", "model_llm_role"])
    w.writeheader()
    for r in rows:
        a = answers[r["repo"]]
        w.writerow({"item": r["item"], "track": r["track"], "repo": r["repo"],
                    "model_core_method": a.get("core_method", ""), "model_llm_role": a.get("llm_role", "")})

# labelling sheet for the author
wb = Workbook()
ins = wb.active
ins.title = "Instructions"
text = [
    "Coding of team approaches (blind check of the LLM coding)",
    "",
    "For each row of the sheet 'Label', read the brief, the README excerpt and the file list, and choose:",
    "  core_method: how the main task of the brief is solved",
    "     llm_prompt  an LLM is called with a prompt and its output is the main result",
    "     llm_agent   an LLM plans or calls tools in several steps (agent, function calling, multi-agent)",
    "     ml_model    a trained or statistical model (regression, gradient boosting, clustering, forecasting)",
    "     algorithm   hand-written rules, heuristics, graph algorithms, optimisation or search",
    "     pretrained  a non-generative pretrained model does the main work (speech recognition, embeddings, OCR)",
    "     unclear     the README does not say",
    "  llm_role: none (no LLM) / core (the LLM produces the main result) /",
    "            support (the LLM explains, chats or summarises on top of another method) / unclear",
    "",
    "Rules (the same as for the model):",
    "  1. Use only what this sheet shows: the brief, the README excerpt (first 2,500 characters, code and links",
    "     removed) and the first 40 file paths. Do not open the repository on GitHub.",
    "  2. If the excerpt does not show it, choose 'unclear'.",
    "  3. Code each row on its own; the order is random. Use 'notes' for doubts (optional).",
    "  4. Do not open data/llm_codebook/validation_key.csv or responses.jsonl before you finish.",
    "",
    f"{len(rows)} rows, {PER_TRACK} per track, drawn at random (seed {SEED}) from the 984 coded repositories,",
    "excluding the 48 pilot repositories. When done, save this file and tell Claude.",
]
for i, line in enumerate(text, start=1):
    ins.cell(row=i, column=1, value=line).font = Font(bold=(i == 1), name="Calibri", size=11)
ins.column_dimensions["A"].width = 110

ws = wb.create_sheet("Label")
head = ["item", "track", "brief", "README excerpt (as given to the model)", "file paths (first 40)",
        "core_method", "llm_role", "notes"]
ws.append(head)
for c in ws[1]:
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor="DDEBF7")
for r in rows:
    ws.append([r["item"], f"T{int(r['track'])} {TRACK_NAMES[r['track']]}", r["brief"], r["readme"], r["paths"],
               None, None, None])
widths = {"A": 6, "B": 16, "C": 40, "D": 95, "E": 45, "F": 14, "G": 12, "H": 30}
for col, wdt in widths.items():
    ws.column_dimensions[col].width = wdt
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[row[0].row].height = 300
for col in ("F", "G"):
    for c in ws[col][1:]:
        c.fill = PatternFill("solid", fgColor="FFF2CC")
dv1 = DataValidation(type="list", formula1='"llm_prompt,llm_agent,ml_model,algorithm,pretrained,unclear"', allow_blank=True)
dv2 = DataValidation(type="list", formula1='"none,core,support,unclear"', allow_blank=True)
ws.add_data_validation(dv1)
ws.add_data_validation(dv2)
dv1.add(f"F2:F{len(rows) + 1}")
dv2.add(f"G2:G{len(rows) + 1}")
ws.freeze_panes = "C2"
OUTDIR.mkdir(parents=True, exist_ok=True)
out = OUTDIR / "LLM_validation_sheet.xlsx"
wb.save(out)
per_track = {t: sum(1 for r in rows if r["track"] == t) for t in sorted(TRACK_NAMES)}
print(f"sheet: {out} ({len(rows)} rows; per track {per_track})")
print(f"key (private): {key}")
print("empty README excerpts:", sum(1 for r in rows if not r["readme"].strip()))
