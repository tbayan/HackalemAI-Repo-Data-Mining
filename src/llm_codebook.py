"""Code how each team solved its brief with a fixed codebook and an LLM (exploratory) -> data/llm_codebook/

Input per repository: the track's brief, the README (code, links, images, e-mails and handles removed; first
README_CHARS characters) and up to MAX_PATHS file paths. Nothing else is sent: no .env files, no secrets, no
author names. Every response is cached with the model name, time and token usage, so results can be recomputed
from the cache when the hosted model changes. A cost cap (priced at peak rates) stops the run.

    python src/llm_codebook.py sample              # stratified pilot sample (PER_TRACK per track)
    python src/llm_codebook.py run --limit 1       # one call, to see the cost per call
    python src/llm_codebook.py run --budget 0.05   # the rest of the sample, stopping at $0.05
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CLONES = DATA / "clones"
OUT = DATA / "llm_codebook"
SAMPLE = OUT / "sample.csv"
ALL = OUT / "all.csv"
CACHE = OUT / "responses.jsonl"

MODEL = "deepseek-flash"
URL = "https://api.deepseek.com/chat/completions"
PRICE = {"hit": 0.006, "miss": 0.30, "out": 1.20}   # USD per 1M tokens, peak (worst case), read 2026-09-28
PEAK_UTC = [(1, 4), (6, 10)]                        # Monday-Friday
README_CHARS, MAX_PATHS, PER_TRACK, SEED = 2500, 40, 4, 20260928
VENDORED = re.compile(r"(^|/)(node_modules|\.venv|venv|env|site-packages|__pycache__|dist|build|\.next|vendor)/")

CODEBOOK = """You code hackathon repositories for a research study. Each team had five hours to build a prototype for
one brief. From the brief, the README and the file list, answer with a JSON object with exactly these keys:

"core_method": how the main task of the brief is solved. One of:
  "llm_prompt"   an LLM is called with a prompt and its output is the main result
  "llm_agent"    an LLM plans or calls tools in several steps (agent, function calling, multi-agent)
  "ml_model"     a trained or statistical model (regression, gradient boosting, clustering, forecasting)
  "algorithm"    hand-written rules, heuristics, graph algorithms, optimisation or search
  "pretrained"   a non-generative pretrained model does the main work (speech recognition, embeddings, OCR)
  "unclear"      the README does not say
"secondary_method": the second most important method from the same list, or "none".
"llm_role": "none" (no LLM), "core" (the LLM produces the main result), "support" (the LLM explains, chats or
  summarises on top of another method), or "unclear".
"interface": "web_app", "chat_bot" (Telegram or similar), "api_only", "script_or_notebook", or "unclear".
"evaluation": true if the README reports a measured result of the solution (a metric, a score on data, a
  test pass rate), else false.
"provided_data": true if the solution uses data given with the brief (the README names the dataset or files
  from the organisers or partner), else false.
"approach": the approach in at most 12 English words, without names of people or teams.

Use only what the README and file list show. If they do not show it, answer "unclear" or false.
Output only the JSON object."""


def api_key() -> str:
    names = ("DEEPSEEK_API_KEY", "Deepseel_API")  # the second is the name used in this project's .env
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        name, _, value = line.strip().removeprefix("export ").partition("=")
        if name.strip() in names and value.strip():
            return value.strip().strip("'\"")
    sys.exit("DeepSeek API key not found in .env")


def git(repo: str, *args: str) -> str:
    import subprocess
    return subprocess.run(["git", f"--git-dir={CLONES / (repo + '.git')}", *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def clean_readme(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>|!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+|\S+@\S+\.\S+|(?<!\w)@\w+", " ", text)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", text)).strip()


def repo_input(repo: str) -> tuple[str, list[str]]:
    paths = [p for p in git(repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines() if not VENDORED.search(p)]
    readme = next((p for p in paths if re.fullmatch(r"(?i)readme(\.(md|markdown|txt|rst))?", p)), None)
    text = clean_readme(git(repo, "show", f"HEAD:{readme}")) if readme else ""
    return text[:README_CHARS], paths[:MAX_PATHS]


def briefs() -> dict[str, str]:
    with (DATA / "official_tracks.csv").open(encoding="utf-8") as f:
        return {r["track"][:2]: r["task"] for r in csv.DictReader(f)}


def cmd_sample(args: argparse.Namespace) -> None:
    with (DATA / "repo_table.csv").open(encoding="utf-8") as f:
        active = {r["repo"] for r in csv.DictReader(f) if int(r["window_commits"]) > 0}
    with (DATA / "hackalem_repos_analysis.csv").open(encoding="utf-8") as f:
        labels = {r["repo"]: r["case_guess"][:2] for r in csv.DictReader(f) if r["case_guess"][:2].isdigit()}
    if args.all:  # every active repository with a track, with the paper's label corrections
        sys.path.insert(0, str(ROOT / "src"))
        from plot_bilingual_charts import CASE_FIXES
        labels |= {r: new for r, (_, new) in CASE_FIXES.items()}
        rows = [{"item": i + 1, "repo": r, "track": labels[r]} for i, r in enumerate(sorted(x for x in labels if x in active))]
        with ALL.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["item", "repo", "track"])
            w.writeheader()
            w.writerows(rows)
        print(f"all: {len(rows)} repositories -> {ALL}")
        return
    rng = random.Random(SEED)
    rows = []
    for track in sorted(set(labels.values())):
        pool = sorted(r for r, t in labels.items() if t == track and r in active)
        rng.shuffle(pool)
        picked = [r for r in pool if len(repo_input(r)[0]) >= 300][:PER_TRACK]
        rows += [{"item": len(rows) + i + 1, "repo": r, "track": track} for i, r in enumerate(picked)]
    OUT.mkdir(parents=True, exist_ok=True)
    with SAMPLE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item", "repo", "track"])
        w.writeheader()
        w.writerows(rows)
    print(f"sample: {len(rows)} repositories -> {SAMPLE}")


def cost(usage: dict) -> float:
    hit = usage.get("prompt_cache_hit_tokens", 0)
    miss = usage.get("prompt_cache_miss_tokens", usage.get("prompt_tokens", 0) - hit)
    return (hit * PRICE["hit"] + miss * PRICE["miss"] + usage.get("completion_tokens", 0) * PRICE["out"]) / 1e6


def call(key: str, messages: list[dict]) -> dict:
    body = json.dumps({"model": MODEL, "messages": messages, "temperature": 0, "max_tokens": 300,
                       "thinking": {"type": "disabled"}, "response_format": {"type": "json_object"}}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Authorization": f"Bearer {key}",
                                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def cmd_run(args: argparse.Namespace) -> None:
    now = dt.datetime.now(dt.timezone.utc)
    if now.weekday() < 5 and any(a <= now.hour < b for a, b in PEAK_UTC) and not args.force:
        sys.exit(f"peak hours now ({now:%H:%M} UTC); prices double. Run later or pass --force.")
    cached = [json.loads(l) for l in CACHE.open(encoding="utf-8")] if CACHE.exists() else []
    done = {r["repo"] for r in cached if r["answer"].strip()}  # an empty answer is retried; its cost still counts
    spent = sum(r.get("cost_usd", 0) for r in cached)
    with (ALL if args.all else SAMPLE).open(encoding="utf-8") as f:
        todo = [r for r in csv.DictReader(f) if r["repo"] not in done][: args.limit]
    key, brief = api_key(), briefs()
    for row in todo:
        if spent >= args.budget:
            print(f"budget reached: ${spent:.4f} of ${args.budget}")
            break
        readme, paths = repo_input(row["repo"])
        user = (f"Brief: {brief.get(row['track'], '')}\n\nREADME:\n{readme}\n\nFiles:\n" + "\n".join(paths))
        try:
            resp = call(key, [{"role": "system", "content": CODEBOOK}, {"role": "user", "content": user}])
        except Exception as err:  # noqa: BLE001 - network errors: keep what is cached and stop
            print(f"{row['item']}: request failed ({type(err).__name__}); stopping")
            break
        usage = resp.get("usage", {})
        c = cost(usage)
        spent += c
        rec = {"repo": row["repo"], "item": row["item"], "track": row["track"], "model": resp.get("model", MODEL),
               "time_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "usage": usage,
               "cost_usd": round(c, 6), "answer": resp["choices"][0]["message"]["content"]}
        with CACHE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"{row['item']:>3} track {row['track']}  tokens in {usage.get('prompt_tokens')} "
              f"(cached {usage.get('prompt_cache_hit_tokens', 0)}) out {usage.get('completion_tokens')}  "
              f"${c:.5f}  total ${spent:.4f}")
        time.sleep(0.3)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("sample")
    sp.add_argument("--all", action="store_true", help="all active repositories with a track")
    sp.set_defaults(func=cmd_sample)
    r = sub.add_parser("run")
    r.add_argument("--all", action="store_true", help="code all.csv instead of the pilot sample")
    r.add_argument("--limit", type=int, default=None)
    r.add_argument("--budget", type=float, default=0.05, help="stop when the estimated cost reaches this (USD)")
    r.add_argument("--force", action="store_true", help="run during peak hours")
    r.set_defaults(func=cmd_run)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
