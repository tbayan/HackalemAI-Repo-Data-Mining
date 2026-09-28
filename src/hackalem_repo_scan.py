#!/usr/bin/env python3
"""Commit and README statistics for every repository in a GitHub organisation.

Written for the HackAlem AI hackathon (org BAITC-Hacks, 23 September 2026). The
organisation, the platform bot, and the event window are constants below.

The work runs in three resumable steps:

    python hackalem_repo_scan.py list   --out data/repos.json
    python hackalem_repo_scan.py scan   --repos data/repos.json --cache data/cache
    python hackalem_repo_scan.py report --repos data/repos.json --cache data/cache \
                                        --csv hackalem_repos_analysis.csv

`list` reads the organisation's repository list. With a GITHUB_TOKEN it uses the
REST API (5,000 requests/hour); without one it reads the JSON embedded in the public
listing pages, because the anonymous API limit is only 60 requests/hour.

`scan` makes a blob-less bare clone of each repository (commits and trees, no file
contents), reads the full commit log and the root README, writes one JSON file per
repository, and deletes the clone. Finished repositories are skipped on a rerun.

`report` computes per-repository statistics, assigns each active repository to a
hackathon case with keyword rules, prints a summary, and writes the CSV. No author
names or e-mails go into the CSV.

Requirements: Python 3.10+, git 2.19+ (partial clone). Standard library only.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import json
import logging
import os
import re
import statistics
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from email.message import Message
from pathlib import Path

log = logging.getLogger("hackalem")

# ---------------------------------------------------------------- event constants
ORG = "BAITC-Hacks"
# Accounts that are not participants: the platform bot that made each repo's "Initial commit",
# and the organiser account that created early test repos and later removed files.
NON_PARTICIPANTS = {"decentra-hackathon[bot]", "BAITC"}
EVENT_TZ = dt.timezone(dt.timedelta(hours=5))    # Astana time
EVENT_DAY = dt.date(2026, 9, 23)
WINDOW_HOURS = (13, 18)                          # local time, [start, end)

FIELD_SEP = "\x1f"                               # ASCII unit separator, safe inside names and subjects
README_RE = re.compile(r"(?i)^readme(\.(md|markdown|txt|rst))?$")
EMBEDDED_JSON_RE = re.compile(
    r'<script type="application/json" data-target="react-app.embeddedData">(.*?)</script>', re.S
)
USER_AGENT = "hackalem-repo-scan/1.0"
BUCKETS = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25), (26, 30),
           (31, 40), (41, 50), (51, 75), (76, 100), (101, None)]


# ---------------------------------------------------------------- step 1: list
def http_get(url: str, token: str | None = None, retries: int = 6) -> tuple[bytes, Message]:
    """GET with exponential backoff on rate limits and transient server errors."""
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers |= {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as resp:
                return resp.read(), resp.headers
        except urllib.error.HTTPError as err:
            if err.code not in (403, 429, 500, 502, 503, 504) or attempt == retries - 1:
                raise
        except urllib.error.URLError:
            if attempt == retries - 1:
                raise
        wait = 5 * 2 ** attempt
        log.warning("GET %s failed, retry in %ss", url, wait)
        time.sleep(wait)
    raise RuntimeError("unreachable")


def list_repos_api(org: str, token: str) -> list[dict]:
    repos: list[dict] = []
    url: str | None = f"https://api.github.com/orgs/{org}/repos?type=all&per_page=100"
    while url:
        body, headers = http_get(url, token)
        repos += [{"name": r["name"], "description": r["description"],
                   "language": r["language"], "pushed_at": r["pushed_at"]} for r in json.loads(body)]
        nxt = re.search(r'<([^>]+)>;\s*rel="next"', headers.get("Link", ""))
        url = nxt.group(1) if nxt else None
    return repos


def _listing_page(org: str, page: int) -> dict:
    body, _ = http_get(f"https://github.com/orgs/{org}/repositories?type=all&page={page}")
    match = EMBEDDED_JSON_RE.search(body.decode("utf-8"))
    if not match:
        raise ValueError(f"page {page}: embedded JSON not found; GitHub may have changed the page")
    return json.loads(match.group(1))["payload"]["orgReposPageRoute"]


def list_repos_html(org: str, workers: int = 4) -> list[dict]:
    first = _listing_page(org, 1)
    with cf.ThreadPoolExecutor(workers) as pool:
        rest = list(pool.map(lambda p: _listing_page(org, p), range(2, first["pageCount"] + 1)))
    repos = [{"name": r["name"], "description": r["description"],
              "language": (r["primaryLanguage"] or {}).get("name"),
              "pushed_at": r["lastUpdated"]["timestamp"]}
             for page in [first, *rest] for r in page["repositories"]]
    if len(repos) != first["repositoryCount"]:
        log.warning("listed %d repos but the page reports %d", len(repos), first["repositoryCount"])
    return repos


def cmd_list(args: argparse.Namespace) -> None:
    repos = list_repos_api(args.org, args.token) if args.token else list_repos_html(args.org)
    unique = sorted({r["name"]: r for r in repos}.values(), key=lambda r: r["name"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(unique, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("wrote %d repositories to %s", len(unique), args.out)


# ---------------------------------------------------------------- step 2: scan
def git(*args: str, cwd: Path | None = None, timeout: int = 180) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, encoding="utf-8", errors="replace",
        timeout=timeout, check=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    ).stdout


def scan_repo(org: str, name: str, cache: Path) -> str:
    target = cache / f"{name}.json"
    if target.exists():
        return "cached"
    record: dict = {"name": name}
    with tempfile.TemporaryDirectory(prefix="scan-") as tmp:
        repo = Path(tmp) / "repo.git"
        try:
            git("clone", "--quiet", "--bare", "--filter=blob:none",
                f"https://github.com/{org}/{name}.git", str(repo))
            fmt = FIELD_SEP.join(["%H", "%aI", "%cI", "%an", "%ae", "%s"])
            record["log"] = git("log", "--all", f"--format={fmt}", cwd=repo).splitlines()
            files = git("ls-tree", "--name-only", "HEAD", cwd=repo).splitlines()
            record["root_files"] = files
            readmes = sorted((f for f in files if README_RE.match(f)),
                             key=lambda f: (f.lower() != "readme.md", f))
            if readmes:  # fetches this one blob lazily from the promisor remote
                record["readme_name"] = readmes[0]
                record["readme"] = git("show", f"HEAD:{readmes[0]}", cwd=repo)[:60_000]
        except subprocess.CalledProcessError as err:
            log.warning("%s: %s", name, (err.stderr or "").strip()[-200:])
            return "error"                     # nothing cached, so a rerun retries it
        except subprocess.TimeoutExpired:
            log.warning("%s: timeout", name)
            return "error"
    tmp_target = target.with_suffix(".part")
    tmp_target.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    tmp_target.replace(target)                 # atomic rename: no half-written cache files
    return "ok"


def cmd_scan(args: argparse.Namespace) -> None:
    names = [r["name"] for r in json.loads(args.repos.read_text(encoding="utf-8"))][: args.limit]
    args.cache.mkdir(parents=True, exist_ok=True)
    status: Counter[str] = Counter()
    with cf.ThreadPoolExecutor(args.workers) as pool:
        futures = [pool.submit(scan_repo, args.org, n, args.cache) for n in names]
        for i, fut in enumerate(cf.as_completed(futures), 1):
            status[fut.result()] += 1
            if i % 250 == 0 or i == len(futures):
                log.info("%d/%d %s", i, len(futures), dict(status))
    if status["error"]:
        log.warning("%d repositories failed; run scan again to retry them", status["error"])


# ---------------------------------------------------------------- step 3: classify
@dataclass(frozen=True)
class CaseRule:
    """Each keyword match adds 1 point; an anchor phrase unique to the case adds ANCHOR_WEIGHT."""
    label: str
    keywords: re.Pattern[str]
    anchor: re.Pattern[str] | None = None


def rule(label: str, keywords: str, anchor: str | None = None) -> CaseRule:
    return CaseRule(label, re.compile(keywords, re.I), re.compile(anchor, re.I) if anchor else None)


ANCHOR_WEIGHT = 30
MIN_SCORE = 2              # below this the repo is "Unclear"
README_CHARS = 20_000      # only the start of long READMEs is scored

# Order matters only for exact ties: the earlier rule wins.
CASE_RULES = [
    rule("01 Energy",
         r"ВЭС|ветров|ветрогенер|ветроэлектр|турбин|wind[ _-]?(farm|power|turbine|speed|actual|forecast)|turbine",
         r"ВЭС"),
    rule("02 Finance", r"Граф денег|Money ?Graph|\bAML\b|отмыв|транзакционн|Freedom",
         r"Граф денег|Money ?Graph"),
    rule("03 Management", r"Career ?Quest|карьер|развити[ея] сотрудник|\bIDP\b|\bИПР\b|компетенц",
         r"Career ?Quest"),
    rule("04 Telecom", r"ARPU|Beeline|Билайн|тариф|абонент", r"Beeline|Билайн|ARPU"),
    rule("05 Logistics", r"пополнени[ея] склад|заказ[а-я]* поставщик|закуп|stockout|replenish|supplier order",
         r"пополнени[ея] склад|заказ[а-я]* поставщик"),
    rule("06 Creative", r"Firebird|подрядчик|contractor|#79", r"Firebird|#79-lite"),
    rule("07 Education",
         r"AI ?Sana|Sana ?Challenge|студенческ|уточняющ[а-я]* вопрос|бриф\b|\bbrief\b|черновик задач|бизнес-задач",
         r"AI ?Sana"),
    rule("08 Innovation", r"протокол[а-я]* (совещ|встреч)|совещани|Хаттама|\bmeeting|транскри|whisper",
         r"Хаттама|Совещание №"),
    rule("09 Communications", r"Voice ?Router|голосов|звонк|\bIVR\b|контакт-центр|call ?cent|страхов",
         r"Voice ?Router"),
    rule("10 Trade", r"ekt\.kz|\bEKT\b|электротехн|электротовар|корзин|консультант", r"консультант"),
    rule("11 Kazakhtelecom", r"реорганизац|организационн|оргструктур|Казахтелеком|Казактелеком|Kazakhtelecom",
         r"Казахтелеком|Казактелеком|Kazakhtelecom"),
    rule("12 Akim5h", r"Аким на 5|Akim for 5|акимат|Quality of Life|\bаким|Моя Астана|бюджет[а-я]* город",
         r"Аким на 5|Akim for 5"),
]


def classify(readme: str) -> str:
    text = readme[:README_CHARS]
    scores = {r.label: len(r.keywords.findall(text)) + (ANCHOR_WEIGHT if r.anchor and r.anchor.search(text) else 0)
              for r in CASE_RULES}
    best = max(scores, key=scores.get)         # first maximum wins on ties
    return best if scores[best] >= MIN_SCORE else "Unclear"


# ---------------------------------------------------------------- step 3: report
@dataclass(frozen=True)
class RepoStats:
    name: str
    participant_commits: int
    window_commits: int
    hours_active: int          # how many of the event hours had at least one commit
    authors: int               # distinct author names, case-insensitive
    case: str


def repo_stats(record: dict) -> RepoStats:
    rows = [line.split(FIELD_SEP) for line in record["log"]]
    people = [r for r in rows if r[3] not in NON_PARTICIPANTS]
    # committer time converted to Astana time; it comes from each participant's own clock
    local = [dt.datetime.fromisoformat(r[2]).astimezone(EVENT_TZ) for r in people]
    in_window = [t for t in local if t.date() == EVENT_DAY and WINDOW_HOURS[0] <= t.hour < WINDOW_HOURS[1]]
    if not people:
        case = "no participant commits"
    elif not in_window:
        case = "commits only outside event window"
    else:
        case = classify(record.get("readme") or "")
    return RepoStats(record["name"], len(people), len(in_window), len({t.hour for t in in_window}),
                     len({r[3].lower() for r in people}), case)


def bucket_label(lo: int, hi: int | None) -> str:
    return f"{lo}+" if hi is None else f"{lo}-{hi}"


def print_summary(stats: list[RepoStats]) -> None:
    active = [s for s in stats if s.window_commits > 0]
    n, k = len(stats), len(active)
    untouched = sum(s.participant_commits == 0 for s in stats)
    print(f"repositories: {n}")
    print(f"no participant commit: {untouched} ({100 * untouched / n:.1f}%)")
    print(f"commits in event window: {k} ({100 * k / n:.1f}%)\n")

    commits = sorted(s.participant_commits for s in active)
    q = statistics.quantiles(commits, n=4)
    print(f"commits per active repo: median {statistics.median(commits):g}, "
          f"quartiles {q[0]:g}-{q[2]:g}, max {commits[-1]}")
    for lo, hi in BUCKETS:
        c = sum(lo <= x and (hi is None or x <= hi) for x in commits)
        print(f"  {bucket_label(lo, hi):>7}: {c:4d}  {100 * c / k:5.1f}%")

    print("\nevent hours with a commit:", dict(sorted(Counter(s.hours_active for s in active).items())))
    print("distinct authors:", dict(sorted(Counter(min(s.authors, 5) for s in active).items())), "(5 = 5+)\n")

    by_case: dict[str, list[RepoStats]] = defaultdict(list)
    for s in active:
        by_case[s.case].append(s)
    print(f"{'case':20} {'repos':>5} {'share':>6} {'median':>6} {'all 5h':>6}")
    for case in sorted(by_case):
        v = by_case[case]
        print(f"{case:20} {len(v):5d} {100 * len(v) / k:5.1f}% "
              f"{statistics.median(s.participant_commits for s in v):6g} "
              f"{100 * sum(s.hours_active == 5 for s in v) / len(v):5.0f}%")


def cmd_report(args: argparse.Namespace) -> None:
    names = [r["name"] for r in json.loads(args.repos.read_text(encoding="utf-8"))]
    missing = [n for n in names if not (args.cache / f"{n}.json").exists()]
    if missing:
        raise SystemExit(f"{len(missing)} repositories not scanned yet, e.g. {missing[:3]}; run scan first")
    stats = [repo_stats(json.loads((args.cache / f"{n}.json").read_text(encoding="utf-8"))) for n in names]
    print_summary(stats)
    with args.csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["repo", "url", "participant_commits", "commits_13_18_local",
                         "hours_with_commits_of_5", "distinct_authors", "case_guess"])
        for s in sorted(stats, key=lambda s: (-s.participant_commits, s.name)):
            writer.writerow([s.name, f"https://github.com/{args.org}/{s.name}", s.participant_commits,
                             s.window_commits, s.hours_active, s.authors, s.case])
    log.info("wrote %s", args.csv)


# ---------------------------------------------------------------- CLI
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--org", default=ORG)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="list repositories of the organisation")
    p.add_argument("--out", type=Path, default=Path("data/repos.json"))
    p.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("scan", help="clone history + README of each repository")
    p.add_argument("--repos", type=Path, default=Path("data/repos.json"))
    p.add_argument("--cache", type=Path, default=Path("data/cache"))
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--limit", type=int, default=None, help="scan only the first N (for testing)")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("report", help="print summary and write the CSV")
    p.add_argument("--repos", type=Path, default=Path("data/repos.json"))
    p.add_argument("--cache", type=Path, default=Path("data/cache"))
    p.add_argument("--csv", type=Path, default=Path("hackalem_repos_analysis.csv"))
    p.set_defaults(func=cmd_report)

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args.func(args)


if __name__ == "__main__":
    main()
