"""Additional checks of the HackAlem AI repositories -> revision_numbers.json (aggregates only).

Separate code path from analysis/run_analysis.py. Each block first reproduces a published value (assert),
then computes the new quantity. Inputs are the private files in data/ and the clones.

    python revision_numbers.py <repository root>

Blocks
  window    end and start of the event window (team commits around 13:00 and 18:00, all repositories);
            sensitivity of the window-dependent measures when the start moves (end fixed at 18:00)
            and when the whole window shifts
  batch     the evening batch of 22 September; repositories created after registration closed
  levels    repeated team names
  traces    trace shares with and without the batch; Claude and Codex-specific overlap
  readme    READMEs changed by agent-signed commits; README length by agent trace
  collab    numbers for the human-agent paragraph that are already in facts_paper.json (re-read, not recomputed)
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(__file__).resolve().parent / "revision_numbers.json"
TZ = timezone(timedelta(hours=5))
T0 = datetime(2026, 9, 23, 13, 0, tzinfo=TZ).timestamp()
T1 = datetime(2026, 9, 23, 18, 0, tzinfo=TZ).timestamp()
FACTS = json.loads((ROOT / "analysis/facts_paper.json").read_text(encoding="utf-8"))


def rhu(x, places=1):
    return float(Decimal(str(x)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def pct(a, b):
    return rhu(100 * a / b, 1)


def wilson(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return {"n": int(k), "of": int(n), "pct": pct(k, n), "lo": rhu(100 * (c - h)), "hi": rhu(100 * (c + h))}


def med(x):
    """Median as printed in the paper: one decimal only when it ends in .5 (deviation 21)."""
    m = float(np.median(x))
    return int(m) if m == int(m) else rhu(m, 1)


def cliff(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return rhu(np.sign(a[:, None] - b[None, :]).mean(), 2)


R: dict = {}
commits = pd.read_csv(ROOT / "data/commits.csv")
repos = pd.read_csv(ROOT / "data/repo_table.csv")
meta = pd.read_csv(ROOT / "data/repos.csv").rename(columns={"name": "repo"})
repos = repos.merge(meta[["repo", "updated_at"]], on="repo")
created = pd.to_datetime(repos.created_at, utc=True).dt.tz_convert(TZ)
updated = pd.to_datetime(repos.updated_at, utc=True).dt.tz_convert(TZ)
repos["active"] = repos.window_commits > 0
repos["day"] = created.dt.strftime("%m-%d")
repos["batch"] = (repos.day == "09-22") & created.dt.hour.isin([18, 19])
repos["prearchived"] = updated < pd.Timestamp(datetime.fromtimestamp(T0, TZ))
ACTIVE = repos.loc[repos.active, "repo"]
assert len(repos) == 3649 and len(ACTIVE) == 1057 and len(commits) == 31955

# ------------------------------------------------------------------ trace flags (repository level, all team commits)
stack = pd.read_csv(ROOT / "data/stack.csv").set_index("repo")
crepo = pd.read_csv(ROOT / "data/commit_repo_features.csv").set_index("repo").reindex(stack.index)
agentish = (((commits.agent_trailer == 1) | (commits.agent_generated_marker == 1) | (commits.agent_account == 1))
            & (commits.agent_kind != "bot"))
sig = commits[agentish]


def has(kind):
    return stack.index.isin(set(sig.loc[sig.agent_kind == kind, "repo"]))


br = crepo.agent_branch_kinds.fillna("")
codex_spec = (crepo.codex_prefix_branches.fillna(0) > 0).values | has("codex")
codex_any = codex_spec | (stack.agents_md == 1).values
claude_any = (crepo.claude_prefix_branches.fillna(0) > 0).values | has("claude") | (stack.claude_md == 1).values
others = np.zeros(len(stack), bool)
for tool, col in (("cursor", "cursor_rules"), ("copilot", "copilot_instructions"), ("gemini", "gemini_md")):
    others |= (stack[col] == 1).values | br.str.contains(tool).values | has(tool)
any_tool = codex_any | claude_any | others
flags = pd.DataFrame({"codex_spec": codex_spec, "codex_any": codex_any, "claude": claude_any, "any": any_tool},
                     index=stack.index)
fa = flags.reindex(ACTIVE)
assert (fa.codex_spec.sum(), fa.codex_any.sum(), fa.claude.sum(), fa["any"].sum()) == (229, 444, 214, 543)


def window_measures(start, end):
    w = commits[(commits.ctime >= start) & (commits.ctime < end)]
    per = w.groupby("repo").size().rename("n").to_frame()
    per["last"] = w[w.ctime >= end - 3600].groupby("repo").size().reindex(per.index, fill_value=0)
    share = per["last"] / per["n"]
    f = flags.reindex(per.index)
    return {"active": int(len(per)), "window_commits": int(len(w)),
            "codex_specific_pct": pct(f.codex_spec.sum(), len(per)),
            "median_last_hour_share": rhu(100 * share.median()),
            "majority_last_hour_pct": pct((share > 0.5).sum(), len(per))}


# ------------------------------------------------------------------ window
day = commits.assign(t=pd.to_datetime(commits.ctime, unit="s") + pd.Timedelta(hours=5))
def count(a, b):
    return int(((day.t >= a) & (day.t < b)).sum())
W = {"hour_before_start": count("2026-09-23 12:00", "2026-09-23 13:00"),
     "first_hour": count("2026-09-23 13:00", "2026-09-23 14:00"),
     "last_hour": count("2026-09-23 17:00", "2026-09-23 18:00"),
     "hour_after_end": count("2026-09-23 18:00", "2026-09-23 19:00"),
     "ten_min_before_end": count("2026-09-23 17:50", "2026-09-23 18:00"),
     "ten_min_after_end": count("2026-09-23 18:00", "2026-09-23 18:10")}
base = window_measures(T0, T1)
assert base == {"active": 1057, "window_commits": 30418, "codex_specific_pct": 21.7,
                "median_last_hour_share": 30.8, "majority_last_hour_pct": 15.4}, base
W["start_moved_end_fixed"] = {f"{h:02d}:{m:02d}": window_measures(T0 + 60 * d, T1)
                              for d, h, m in ((-60, 12, 0), (-30, 12, 30), (0, 13, 0), (30, 13, 30), (60, 14, 0))}
W["whole_window_shifted"] = {f"{d:+d}": window_measures(T0 + 60 * d, T1 + 60 * d) for d in (-60, -30, 30, 60)}
spec = [v["codex_specific_pct"] for v in W["whole_window_shifted"].values()] + \
       [v["codex_specific_pct"] for v in W["start_moved_end_fixed"].values()]
W["codex_specific_range_all_shifts"] = [min(spec), max(spec)]
R["window"] = W

# ------------------------------------------------------------------ batch and registration
bt = repos[repos.batch]
bmin = created[repos.batch].dt.floor("min").value_counts()
organic = created[~repos.batch & (repos.day < "09-22")].dt.floor("min").value_counts()
names = repos.repo.str.replace(r"^hack-[0-9a-f]{8}-", "", regex=True)
earlier = set(names[~repos.batch & (created < pd.Timestamp("2026-09-22 18:00", tz=TZ))])
R["batch"] = {"n": int(len(bt)), "first": created[repos.batch].min().strftime("%H:%M"),
              "last": created[repos.batch].max().strftime("%H:%M"),
              "minutes_with_creations": int(len(bmin)), "median_per_minute": int(bmin.median()),
              "max_per_minute": int(bmin.max()), "organic_max_per_minute": int(organic.max()),
              "names_used_before": int(names[repos.batch].isin(earlier).sum()),
              "active": int(bt.active.sum()), "prearchived": int(bt.prearchived.sum())}
assert R["batch"]["n"] == 1040 and R["batch"]["active"] == 14
after = repos.day > "09-19"
R["registration"] = {"created_after_sep19": int(after.sum()), "created_after_sep19_not_batch": int((after & ~repos.batch).sum()),
                     "created_on_sep21": int((repos.day == "09-21").sum()),
                     "created_on_sep21_prearchived": int(((repos.day == "09-21") & repos.prearchived).sum())}

# ------------------------------------------------------------------ levels: repeated team names
g = repos.assign(name=names).groupby("name").agg(n=("repo", "size"), act=("active", "sum"))
multi = g[(g.n > 1) & (g.index != "team")]
R["levels"] = {"names_repeated": int(len(multi)), "repos_in_repeated": int(multi.n.sum()),
               "groups_exactly_one_active": int((multi.act == 1).sum()), "groups_none_active": int((multi.act == 0).sum()),
               "groups_several_active": int((multi.act > 1).sum()), "generic_team_repos": int(g.loc["team", "n"])}
assert R["levels"]["names_repeated"] == FACTS["rq1"]["repeated_names"]["groups_excl_generic"]

# ------------------------------------------------------------------ traces without the batch; overlap
nb = repos.loc[repos.active & ~repos.batch, "repo"]
fn = flags.reindex(nb)
R["traces"] = {"active_not_batch": int(len(nb)),
               "codex_specific_pct": pct(fn.codex_spec.sum(), len(nb)), "codex_any_pct": pct(fn.codex_any.sum(), len(nb)),
               "claude_pct": pct(fn.claude.sum(), len(nb)),
               "claude_and_codex_specific": wilson(int((fa.claude & fa.codex_spec).sum()), 1057)}

# ------------------------------------------------------------------ README: agent-signed changes and length
rf = pd.read_csv(ROOT / "data/readme_features.csv").set_index("repo").reindex(ACTIVE)
written = rf.language.isin(["russian", "english", "kazakh", "mixed"])
assert written.sum() == 1033
strict = commits[agentish & (commits.agent_name_only == 0)]
hit, hit_any, kinds = 0, 0, {}
for repo in written[written].index:
    out = subprocess.run(["git", f"--git-dir={ROOT / 'data/clones' / (repo + '.git')}", "log", "--all", "--format=%H",
                          "--", ":(icase)README.md"], capture_output=True, text=True).stdout.split()
    s = strict[(strict.repo == repo) & strict.sha.isin(out)]
    a = commits[agentish & (commits.repo == repo) & commits.sha.isin(out)]
    hit += len(s) > 0
    hit_any += len(a) > 0
    for k in s.agent_kind.unique():
        kinds[k] = kinds.get(k, 0) + 1
words_any = rf.loc[written & fa["any"].values, "words"]
words_none = rf.loc[written & ~fa["any"].values, "words"]
R["readme"] = {"changed_by_signed_commit": wilson(hit, 1033), "changed_by_signed_or_named": wilson(hit_any, 1033),
               "signed_by_kind": kinds,
               "words_any_trace": {"n": int(len(words_any)), "median": med(words_any)},
               "words_no_trace": {"n": int(len(words_none)), "median": med(words_none)},
               "words_delta": cliff(words_any, words_none),
               "words_p": float(stats.mannwhitneyu(words_any, words_none).pvalue)}

# second route: parse the commits that touched README.md on branches directly, with own patterns
import re
AG = r"(claude|codex|cursor|copilot|devin|gemini)"
TR = re.compile(r"^co-authored-by:[^\n]*" + AG, re.I | re.M)
GEN = re.compile(r"generated (with|by)[^\n]*" + AG, re.I)
ACC = re.compile(r"noreply@anthropic\.com|@openai\.com|cursoragent|" + AG + r"[^\s]*\[bot\]|\[bot\][^\n]*" + AG, re.I)
hit2 = 0
for repo in written[written].index:
    out = subprocess.run(["git", f"--git-dir={ROOT / 'data/clones' / (repo + '.git')}", "log", "--branches",
                          "--format=%x1e%an <%ae>%x1f%cn <%ce>%x1f%B", "--", ":(icase)README.md"],
                         capture_output=True, text=True, errors="replace").stdout
    for rec in out.split("\x1e")[1:]:
        a, c, body = (rec.split("\x1f") + ["", ""])[:3]
        if TR.search(body) or GEN.search(body) or ACC.search(a) or ACC.search(c):
            hit2 += 1
            break
assert hit2 == hit, (hit2, hit)
R["readme"]["second_route_count"] = hit2

# ------------------------------------------------------------------ collaboration numbers already published (re-read)
t = FACTS["rq2"]["traces"]
R["collab"] = {"signed_window_commits_pct": t["signed_commits"]["pct"], "pr_refs_with_codex_branch": t["pr_refs"]["with_codex_branch"],
               "agents_md_repos": t["codex"]["file"]["n"], "codex_named_readme": t["self_report"]["codex_strict"]["mention"]["n"],
               "specific_given_named": t["self_report"]["codex_strict"]["specific_given_mention"]}

OUT.write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(R, indent=1, ensure_ascii=False))
