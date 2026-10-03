"""Every statistic in the paper (v2, after review) -> analysis/facts_paper.json + tables/.

Organised by the four research questions of the revised paper:
  RQ1 population  (all 3,649 organiser-created repositories; stages, creation date, batch)
  RQ2 process     (active repositories: work over the window, traces of coding agents)
  RQ3 product     (active repositories: stack, artefacts, documentation, tracks)
  RQ4 risk        (active repositories: credential strings in public history, hygiene)
plus validation and sensitivity checks.

Denominators: RQ2-RQ4 use the active repositories (at least one team commit in the event
window) unless a key says otherwise. Inputs are the private files built by src/; outputs
contain only aggregates. Percentages have one decimal; odds ratios and effect sizes two;
p-values are strings. Seeds are fixed, so a rerun reproduces every number.
Deviations from analysis_plan.md are listed in analysis/deviations.md.
"""
from __future__ import annotations

import json
import math
from decimal import ROUND_HALF_UP, Decimal
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import cohen_kappa_score, silhouette_score
from statsmodels.stats.contingency_tables import StratifiedTable
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

PAPER = Path(__file__).resolve().parent.parent
ROOT = PAPER.parent
DATA = ROOT / "data"
TABLES = PAPER / "tables"
OUT = PAPER / "analysis" / "facts_paper.json"
sys.path.insert(0, str(ROOT / "src"))
from plot_bilingual_charts import CASE_FIXES, CASES  # noqa: E402
import solution_similarity as ss  # noqa: E402

TZ = timezone(timedelta(hours=5))
START = datetime(2026, 9, 23, 13, 0, tzinfo=TZ).timestamp()
LAST_HOUR = datetime(2026, 9, 23, 17, 0, tzinfo=TZ).timestamp()
END = datetime(2026, 9, 23, 18, 0, tzinfo=TZ).timestamp()
DAY_START = datetime(2026, 9, 23, 11, 0, tzinfo=TZ).timestamp()
DAY_END = datetime(2026, 9, 23, 19, 0, tzinfo=TZ).timestamp()
RNG = np.random.default_rng(2026)
F: dict = {}


# ------------------------------------------------------------------ helpers
def rhu(value, places: int = 1):
    """Round half up (86.25 -> 86.3); Python's round() rounds half to even."""
    q = Decimal(str(float(value))).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    return int(q) if places == 0 else float(q)


def num(value):
    """A median that can end in .5: an int when whole, else one decimal."""
    v = rhu(value, 1)
    return int(v) if v == int(v) else v


class Fixed(float):
    """A rounded float that keeps its trailing zeros in facts_paper.json (1.10, not 1.1)."""

    def __new__(cls, value, places: int):
        obj = super().__new__(cls, rhu(value, places))
        obj.places = places
        return obj


def r2(value) -> Fixed:
    return Fixed(value, 2)


def to_json(obj) -> str:
    def mark(v):
        if isinstance(v, Fixed):
            return f"@fixed:{v:.{v.places}f}@"
        if isinstance(v, dict):
            return {k: mark(x) for k, x in v.items()}
        if isinstance(v, list):
            return [mark(x) for x in v]
        return v
    return re.sub(r'"@fixed:(-?[0-9.]+)@"', r"\1", json.dumps(mark(obj), indent=2, ensure_ascii=False))


def pct(part, whole) -> float:
    return rhu(100 * part / whole, 1) if whole else 0.0


def prop(part, whole) -> dict:
    """n, %, Wilson 95% CI and the denominator."""
    part, whole = int(part), int(whole)
    lo, hi = proportion_confint(part, whole, method="wilson") if whole else (0, 0)
    return {"n": part, "of": whole, "pct": pct(part, whole), "lo": rhu(100 * lo, 1), "hi": rhu(100 * hi, 1)}


def fmt_p(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"= {p:.3f}"


def med_iqr(values) -> dict:
    v = pd.Series(values, dtype=float)
    return {"median": rhu(v.median(), 0), "q1": rhu(v.quantile(0.25), 0), "q3": rhu(v.quantile(0.75), 0)}


def cliffs_delta(a, b) -> Fixed:
    a, b = np.asarray(a), np.asarray(b)
    greater = sum((x > b).sum() for x in a)
    less = sum((x < b).sum() for x in a)
    return r2((greater - less) / (len(a) * len(b)))


def chi2_test(table) -> dict:
    chi2, p, dof, expected = stats.chi2_contingency(table, correction=False)
    v = math.sqrt(chi2 / (table.values.sum() * (min(table.shape) - 1)))
    return {"chi2": rhu(chi2, 1), "df": int(dof), "p": fmt_p(p), "v": r2(v), "n": int(table.values.sum()),
            "cells_expected_below5": int((expected < 5).sum()), "cells": int(expected.size)}


def logit_or(y, X, term: str) -> dict:
    fit = sm.Logit(y.astype(int), sm.add_constant(X.astype(float))).fit(disp=0)
    lo, hi = fit.conf_int().loc[term]
    return {"or": r2(math.exp(fit.params[term])), "lo": r2(math.exp(lo)), "hi": r2(math.exp(hi)),
            "p": fmt_p(fit.pvalues[term]), "n": int(len(y))}


def hhmm(ts) -> str:
    return datetime.fromtimestamp(ts, TZ).strftime("%H:%M")


# ------------------------------------------------------------------ load
repos = pd.read_csv(DATA / "repo_table.csv")
meta = pd.read_csv(DATA / "repos.csv").rename(columns={"name": "repo"})
stack = pd.read_csv(DATA / "stack.csv")
crepo = pd.read_csv(DATA / "commit_repo_features.csv")
commits = pd.read_csv(DATA / "commits.csv")
readme = pd.read_csv(DATA / "readme_features.csv")
labels = pd.read_csv(DATA / "hackalem_repos_analysis.csv")[["repo", "case_guess"]]
labels["raw_track"] = labels.case_guess.str.extract(r"^(\d{2})\b", expand=False)
labels["track"] = labels.raw_track
for repo, (_, new) in CASE_FIXES.items():
    labels.loc[labels.repo == repo, "track"] = new

repos = repos.merge(meta[["repo", "updated_at"]], on="repo")
created = pd.to_datetime(repos.created_at, utc=True).dt.tz_convert(TZ)
updated = pd.to_datetime(repos.updated_at, utc=True).dt.tz_convert(TZ)
repos["created_ts"] = created.map(lambda t: t.timestamp())
repos["updated_ts"] = updated.map(lambda t: t.timestamp())
repos["any"] = repos.team_commits > 0
repos["active"] = repos.window_commits > 0
repos["prearchived"] = repos.updated_ts < START
day = created.dt.strftime("%Y-%m-%d")
repos["batch"] = (day == "2026-09-22") & created.dt.hour.isin([18, 19])
repos = repos.merge(labels[["repo", "raw_track", "track"]], on="repo", how="left")
N = len(repos)
ACTIVE = set(repos.loc[repos.active, "repo"])
NA = len(ACTIVE)
TABLES.mkdir(exist_ok=True)

# ------------------------------------------------------------------ RQ1 population
P: dict = {"total": N}
pre = repos[repos.prearchived]
pre_days = updated[repos.prearchived].dt.strftime("%m-%d")
clusters = {}
for d, n in pre_days.value_counts().items():
    if n >= 50:
        ts = updated[repos.prearchived & (updated.dt.strftime("%m-%d") == d)]
        clusters[f"sep{d[-2:]}"] = {"n": int(n), "first": ts.min().strftime("%H:%M"), "last": ts.max().strftime("%H:%M"),
                                    "max_per_minute": int(ts.dt.floor("min").value_counts().max())}
P["prearchived"] = {"n": len(pre), "pct": pct(len(pre), N), "clusters": clusters,
                    "other": int(len(pre) - sum(c["n"] for c in clusters.values())),
                    "active": int(pre.active.sum()), "with_commits": int(pre["any"].sum()),
                    "created_sep15_21": int(((day >= "2026-09-15") & (day <= "2026-09-21") & repos.prearchived).sum()),
                    "in_batch": int((repos.prearchived & repos.batch).sum())}
open_ = repos[~repos.prearchived]
P["open"] = {"n": len(open_), "with_commits": int(open_["any"].sum()), "active": int(open_.active.sum()),
             "active_pct": pct(open_.active.sum(), len(open_))}
P["with_commits"] = prop(repos["any"].sum(), N)
P["empty"] = prop((~repos["any"]).sum(), N)
P["active"] = prop(NA, N)
P["active_of_open"] = prop(NA, len(open_))
onb = open_[~open_.batch]
P["active_of_open_nonbatch"] = prop(onb.active.sum(), len(onb))
outside = repos.loc[repos["any"] & ~repos.active, "repo"]
last_ct = commits.groupby("repo").ctime.max()
P["outside_only"] = {"n": len(outside), "all_before_event": int((last_ct.reindex(outside) < START).sum()),
                     "prearchived": int((repos["any"] & ~repos.active & repos.prearchived).sum())}
first_ct = commits.groupby("repo").ctime.min()
early = repos.repo.map(first_ct).lt(START)
P["pre_event_commits"] = {"prearchived": prop(early[repos.prearchived].sum(), repos.prearchived.sum()),
                          "open": prop(early[~repos.prearchived].sum(), (~repos.prearchived).sum())}
act = repos[repos.active]
P["matched_track"] = prop(act.track.notna().sum(), NA)
P["track_unclear"] = int(act.track.isna().sum())
P["label_fixes"] = len(CASE_FIXES)

bt = repos[repos.batch]
per_min = created[repos.batch].dt.floor("min").value_counts()
organic = created[~repos.batch & (day < "2026-09-22")]
P["batch"] = {"n": len(bt), "active": prop(bt.active.sum(), len(bt)),
              "max_per_minute": int(per_min.max()), "organic_max_per_minute": int(organic.dt.floor("min").value_counts().max())}

bins = ["2000-01-01", "2026-09-01", "2026-09-15", "2026-09-22", "2026-09-23", "2026-09-24"]
grp = pd.cut(pd.to_datetime(day), bins=pd.to_datetime(bins), right=False,
             labels=["before_sep01", "sep01_14", "sep15_21", "sep22", "sep23"]).astype(str)
repos["cgroup"] = np.where(repos.batch, "batch", grp)
P["creation"] = {}
for g in ["before_sep01", "sep01_14", "sep15_21", "sep22", "sep23", "batch"]:
    sub = repos[repos.cgroup == g]
    so = sub[~sub.prearchived]
    P["creation"][g] = {"n": len(sub), "prearchived": int(sub.prearchived.sum()),
                        "open": prop(so.active.sum(), len(so)), "all": prop(sub.active.sum(), len(sub))}
cg = open_.assign(cgroup=repos.loc[open_.index, "cgroup"])
cg = cg[cg.cgroup.isin(["before_sep01", "sep01_14", "sep15_21", "sep22"])]
P["creation_chi2_open_nonbatch"] = chi2_test(pd.crosstab(cg.cgroup, cg.active))
# The naive view: every repository as a registered team, groups as in the first draft (batch inside 22 Sep).
naive = repos.assign(g=grp)
naive = naive[naive.g != "sep23"]
P["creation_chi2_all"] = chi2_test(pd.crosstab(naive.g, naive.active))
P["active_gap_pp"] = rhu(P["active_of_open_nonbatch"]["pct"] - P["active"]["pct"], 1)

team_name = repos.repo.str.replace(r"^hack-[0-9a-f]{8}-", "", regex=True)
dup = repos.assign(team_name=team_name).groupby("team_name").agg(n=("repo", "size"), active=("active", "sum"))
dup_multi = dup[(dup.n > 1) & (dup.index != "team")]
P["repeated_names"] = {"names": int((dup.n > 1).sum()), "groups_excl_generic": len(dup_multi),
                       "repos_excl_generic": int(dup_multi.n.sum()), "groups_one_active": int((dup_multi.active == 1).sum()),
                       "generic_team_repos": int(dup.loc["team", "n"]) if "team" in dup.index else 0}

wc_all = commits[(commits.ctime >= START) & (commits.ctime < END)]
authors = wc_all[(wc_all.author_bot == 0) & wc_all.repo.isin(ACTIVE)].groupby("repo").author_key.nunique()
inactive = repos[~repos.active]
P["inactive"] = {"n": len(inactive), "organiser": prop((inactive.prearchived | inactive.batch).sum(), len(inactive))}
P["authors"] = {"sum": int(authors.sum()), "median": num(authors.median()),
                "one": int((authors == 1).sum()), "two": int((authors == 2).sum()), "three": int((authors == 3).sum()),
                "four_plus": int((authors >= 4).sum())}
F["rq1"] = P

# ------------------------------------------------------------------ RQ2 process
Q: dict = {}
wc = wc_all[wc_all.repo.isin(ACTIVE)].copy()
wc["hour"] = ((wc.ctime - START) // 3600).astype(int) + 13
Q["team_commits_total"] = len(commits)
Q["window_commits"] = len(wc)
hourly = wc.groupby("hour").size().reindex(range(13, 18), fill_value=0)
Q["hourly"] = {f"h{h}": int(v) for h, v in hourly.items()}
Q["last_hour_share_pooled"] = pct(hourly[17], len(wc))
per10 = ((wc.ctime - START) // 600).astype(int).value_counts().sort_index()
Q["peak10"] = {"commits": int(per10.max()), "start": hhmm(START + 600 * int(per10.idxmax())),
               "end": hhmm(START + 600 * (int(per10.idxmax()) + 1))}
tl = commits[(commits.ctime >= DAY_START) & (commits.ctime < DAY_END)]
tl = ((tl.ctime - DAY_START) // 600).astype(int).value_counts().reindex(range(48), fill_value=0).sort_index()
pd.DataFrame({"minutes_after_11": tl.index * 10, "commits": tl.values}).to_csv(TABLES / "timeline_10min.csv", index=False)

team = wc.groupby("repo").agg(first=("ctime", "min"), last=("ctime", "max"), n=("ctime", "size"))
team["last_hour"] = wc[wc.hour == 17].groupby("repo").size().reindex(team.index, fill_value=0)
team["share"] = team.last_hour / team.n
pd.DataFrame({"last_hour_share": np.sort(team.share.values).round(4)}).to_csv(TABLES / "last_hour_share.csv", index=False)
Q["team_share"] = {"median": pct(team.share.median(), 1), "q1": pct(team.share.quantile(0.25), 1),
                   "q3": pct(team.share.quantile(0.75), 1)}
Q["teams_majority_last_hour"] = prop((team.share > 0.5).sum(), NA)
Q["teams_any_last_hour"] = prop((team.last_hour > 0).sum(), NA)
Q["teams_all_last_hour"] = prop((team.share == 1).sum(), NA)
Q["first_commit_min"] = med_iqr((team["first"] - START) / 60)
Q["last_commit_min_before_deadline"] = med_iqr((END - team["last"]) / 60)
Q["commits_per_team"] = med_iqr(team.n)
hours = act.hours_active.value_counts().reindex(range(1, 6), fill_value=0)
Q["hours"] = {f"h{k}": int(v) for k, v in hours.items()}
Q["teams_4plus_hours"] = prop(hours.loc[4:].sum(), NA)
Q["teams_all_5_hours"] = prop(hours.loc[5], NA)
pre_c = commits[(commits.ctime < START) & commits.repo.isin(ACTIVE)]
pre_lines = pre_c.assign(lines=pre_c.added + pre_c.deleted).groupby("repo").lines.sum()
post = commits[(commits.ctime >= END) & commits.repo.isin(ACTIVE)]
Q["pre_event"] = {"repos": int(pre_c.repo.nunique()), "commits": len(pre_c), "repos_over_1000_lines": int((pre_lines > 1000).sum())}
Q["post_deadline"] = {"repos": int(post.repo.nunique()), "commits": len(post),
                      "commits_before_19": int((post.ctime < DAY_END).sum())}

# Exploratory: k-means on hourly shares, compared with a null model without team structure.
profiles = wc.groupby(["repo", "hour"]).size().unstack(fill_value=0).reindex(columns=range(13, 18), fill_value=0)
shares = profiles.div(profiles.sum(axis=1), axis=0)
km = KMeans(n_clusters=2, n_init=20, random_state=42).fit(shares)
sil = silhouette_score(shares, km.labels_, random_state=42)
pooled = profiles.sum().values / profiles.values.sum()
null = []
for _ in range(20):
    sim = np.array([RNG.multinomial(n, pooled) for n in profiles.sum(axis=1)]) / profiles.sum(axis=1).values[:, None]
    null.append(silhouette_score(sim, KMeans(n_clusters=2, n_init=10, random_state=42).fit(sim).labels_, random_state=42))
late = int(np.argmax(km.cluster_centers_[:, 4]))
Q["clusters_exploratory"] = {"silhouette": r2(sil), "null_mean": r2(np.mean(null)), "null_p95": r2(np.percentile(null, 95)),
                             "late_n": int((km.labels_ == late).sum()), "late_centroid_h17": pct(km.cluster_centers_[late][4], 1)}

# Agent traces by tool (active repositories). Four repository traces per tool: a context file, a branch whose
# name starts with the tool's name, a commit signature (co-author trailer, "generated with" line or agent service
# account) and an author or committer named exactly after the tool. AGENTS.md is read by Codex and by other
# agents (and is often present with Claude Code traces), so for Codex it is reported apart from the specific traces.
s = stack[stack.repo.isin(ACTIVE)].set_index("repo")
c = crepo[crepo.repo.isin(ACTIVE)].set_index("repo").reindex(s.index)
agentish = (((commits.agent_trailer == 1) | (commits.agent_generated_marker == 1) | (commits.agent_account == 1))
            & (commits.agent_kind != "bot"))
sig = commits[agentish]
strict_sig = commits[agentish & (commits.agent_name_only == 0)]
named = commits[agentish & (commits.agent_name_only == 1)]


def repos_of(df, kind):
    return set(df[(df.agent_kind == kind) & df.repo.isin(ACTIVE)].repo)


files = {"codex": "agents_md", "claude": "claude_md", "cursor": "cursor_rules", "copilot": "copilot_instructions",
         "gemini": "gemini_md"}
branch_kinds = c.agent_branch_kinds.fillna("")
prefix = {"codex": (c.codex_prefix_branches.fillna(0) > 0).values, "claude": (c.claude_prefix_branches.fillna(0) > 0).values}
T: dict = {}
chan: dict = {}
rows = []
any_tool = np.zeros(len(s), dtype=bool)
for tool, fcol in files.items():
    f_ = (s[fcol] == 1).values
    b_ = prefix[tool] if tool in prefix else branch_kinds.str.contains(tool).values
    g_ = s.index.isin(repos_of(strict_sig, tool))
    n_ = s.index.isin(repos_of(named, tool))
    specific = b_ | g_ | n_ | (f_ if tool != "codex" else np.zeros(len(s), dtype=bool))
    a_ = f_ | b_ | g_ | n_
    any_tool |= a_
    chan[tool] = {"file": f_, "branch": b_, "signature": g_, "name": n_, "specific": specific, "any": a_}
    T[tool] = {k: prop(v.sum(), NA) for k, v in chan[tool].items()}
    rows.append({"tool": tool, **{k: int(v.sum()) for k, v in chan[tool].items()}})
pd.DataFrame(rows).to_csv(TABLES / "tool_traces.csv", index=False)
cx, cl = chan["codex"], chan["claude"]
pd.DataFrame({"agents_md": cx["file"], "branch": cx["branch"], "signature": cx["signature"], "name": cx["name"]}) \
    .value_counts().rename("repos").reset_index().to_csv(TABLES / "codex_trace_combinations.csv", index=False)
codex_any, claude_any = cx["any"], cl["any"]
T["codex_file_only"] = prop((cx["file"] & ~cx["specific"]).sum(), NA)
# Context files that Next.js wrote, or that sit in vendored folders, are not counted (src/extract_stack.py).
# Report how many there were and what the shares would have been with them.
agents_any_path, claude_any_path = (s.agents_md_any_path == 1).values, (s.claude_md_any_path == 1).values
T["context_excluded"] = {
    "nextjs": prop((s.nextjs_agent_files == 1).sum(), NA),
    "agents_any_path": prop(agents_any_path.sum(), NA), "claude_any_path": prop(claude_any_path.sum(), NA),
    "agents_dropped": int((agents_any_path & ~cx["file"]).sum()), "claude_dropped": int((claude_any_path & ~cl["file"]).sum()),
    "codex_any_with_them": prop((cx["specific"] | agents_any_path).sum(), NA),
    "claude_any_with_them": prop((cl["any"] | claude_any_path).sum(), NA),
}
T["agents_md_with_claude"] = prop((cx["file"] & claude_any).sum(), claude_any.sum())
T["agents_md_without_claude"] = prop((cx["file"] & ~claude_any).sum(), (~claude_any).sum())
T["any_tool"] = prop(any_tool.sum(), NA)
T["no_trace"] = prop((~any_tool).sum(), NA)
T["codex_and_claude"] = prop((codex_any & claude_any).sum(), NA)
T["claude_not_codex"] = prop((claude_any & ~codex_any).sum(), NA)
T["codex_not_claude"] = prop((codex_any & ~claude_any).sum(), NA)
T["neither_codex_nor_claude"] = prop((~codex_any & ~claude_any).sum(), NA)
T["claude_not_codex_specific"] = prop((claude_any & ~cx["specific"]).sum(), NA)
T["other_rule_files"] = int((s.other_agent_rules == 1).sum())
pr = (c.pr_refs.fillna(0) > 0).values
T["pr_refs"] = {**prop(pr.sum(), NA), "with_codex_branch": int((pr & cx["branch"]).sum())}
wsig = sig[(sig.ctime >= START) & (sig.ctime < END) & sig.repo.isin(ACTIVE)]
T["signed_commits"] = {**prop(len(wsig), len(wc)), "by_kind": {k: int(v) for k, v in wsig.agent_kind.value_counts().items()},
                       "claude_share": pct((wsig.agent_kind == "claude").sum(), len(wsig)),
                       "codex_named_only": int(((wsig.agent_kind == "codex") & (wsig.agent_name_only == 1)).sum())}
bots = commits[(commits.agent_kind == "bot")]
T["other_bot_commits"] = {"commits": len(bots), "repos": int(bots.repo.nunique())}
wn = wc[wc.is_merge == 0]
ws = wn.index.isin(sig.index)
T["conventional"] = {"all": prop(wn.conventional.sum(), len(wn)), "signed": prop(wn[ws].conventional.sum(), ws.sum()),
                     "unsigned": prop(wn[~ws].conventional.sum(), (~ws).sum())}

# Association of AGENTS.md with activity and tests (planned; observational; Holm across three tests).
sa = s[["agents_md", "tests"]].join(act.set_index("repo")[["window_commits", "hours_active"]])
w, wo = sa[sa.agents_md == 1], sa[sa.agents_md == 0]
tab = pd.crosstab(sa.agents_md, sa.tests)
raw = [stats.mannwhitneyu(w.window_commits, wo.window_commits).pvalue,
       stats.mannwhitneyu(w.hours_active, wo.hours_active).pvalue,
       stats.chi2_contingency(tab, correction=False)[1]]
holm = multipletests(raw, method="holm")[1]
T["agents_md_assoc"] = {
    "n_with": len(w), "n_without": len(wo),
    "commits_with": num(w.window_commits.median()), "commits_without": num(wo.window_commits.median()),
    "commits_delta": cliffs_delta(w.window_commits, wo.window_commits), "commits_p": fmt_p(holm[0]),
    "hours_with": num(w.hours_active.median()), "hours_without": num(wo.hours_active.median()),
    "hours_delta": cliffs_delta(w.hours_active, wo.hours_active), "hours_p": fmt_p(holm[1]),
    "tests_with": pct(w.tests.sum(), len(w)), "tests_without": pct(wo.tests.sum(), len(wo)), "tests_p": fmt_p(holm[2]),
    "tests_v": chi2_test(tab)["v"],
    "tests_adjusted": logit_or(sa.tests, pd.DataFrame({"agents_md": sa.agents_md, "log_commits": np.log1p(sa.window_commits)}), "agents_md"),
}
# README naming of a tool (exploratory, added after review). Strict: the tool named in README prose, not as part
# of a file or model name; broad: the word anywhere in the raw README. Not independent of the traces: agents
# can write READMEs, so the association between naming and traces is reported, and the shares are conditional
# detection rates among teams that name the tool, not recall.
rdm = readme.set_index("repo").reindex(s.index)
written_mask = rdm.language.isin(["russian", "english", "kazakh", "mixed"]).values
SR: dict = {}
for tool, strict_col, broad_col in (("codex", "names_codex", "mentions_codex"), ("claude", "names_claude_code", "mentions_claude")):
    for variant, col in (("strict", strict_col), ("broad", broad_col)):
        said = rdm[col].fillna(0).astype(int).values == 1
        spec, anyt = chan[tool]["specific"], chan[tool]["any"]
        d = {"mention": prop(said.sum(), written_mask.sum()),
             "specific_given_mention": prop((said & spec).sum(), said.sum()),
             "any_given_mention": prop((said & anyt).sum(), said.sum()),
             "specific_or_mention": prop((said | spec).sum(), NA), "any_or_mention": prop((said | anyt).sum(), NA)}
        for k in ("file", "branch", "signature", "name"):
            d[f"{k}_given_mention"] = prop((said & chan[tool][k]).sum(), said.sum())
        a1, b1 = (said & anyt).sum() + 0.5, (said & ~anyt).sum() + 0.5
        c1, d1 = (~said & anyt).sum() + 0.5, (~said & ~anyt).sum() + 0.5
        lor, se = math.log(a1 * d1 / (b1 * c1)), math.sqrt(1 / a1 + 1 / b1 + 1 / c1 + 1 / d1)
        d["assoc"] = {"or": r2(math.exp(lor)), "lo": r2(math.exp(lor - 1.96 * se)), "hi": r2(math.exp(lor + 1.96 * se))}
        SR[f"{tool}_{variant}"] = d
T["self_report"] = SR

# Size of agent-signed vs other commits in the same repository (planned as exploratory; window commits of active
# repositories; lines outside lock, data and generated files; per-repository medians; Wilcoxon signed-rank).
nmc = wc[wc.is_merge == 0].copy()
nmc["signed"] = nmc.index.isin(sig.index)


def size_test(df) -> dict:
    per = df.groupby(["repo", "signed"]).code_lines.median().unstack().dropna()
    diff = per[True] - per[False]
    return {"repos": len(per), "median_signed": num(per[True].median()),
            "median_unsigned": num(per[False].median()), "signed_larger": prop((diff > 0).sum(), len(per)),
            "p": fmt_p(stats.wilcoxon(per[True], per[False]).pvalue)}


n_signed = nmc[nmc.signed].groupby("repo").size()
T["commit_size"] = {"all": size_test(nmc), "min3": size_test(nmc[nmc.repo.isin(n_signed[n_signed >= 3].index)]),
                    "claude": size_test(nmc[~nmc.signed | (nmc.agent_kind == "claude")]),
                    }
# pooled over the commits of the repositories that have both kinds (the set of the Wilcoxon test)
both = nmc.groupby("repo").signed.agg(["any", "all"])
both = nmc[nmc.repo.isin(both[both["any"] & ~both["all"]].index)]
T["commit_size"]["pooled_repos"] = int(both.repo.nunique())
T["commit_size"]["pooled_signed"] = num(both[both.signed].code_lines.median())
T["commit_size"]["pooled_unsigned"] = num(both[~both.signed].code_lines.median())
Q["traces"] = T
F["rq2"] = Q

# ------------------------------------------------------------------ RQ3 product
R: dict = {"n": NA}
prim = s.primary_language.fillna("none").value_counts()
R["primary_language"] = {k.replace("+", "p").replace("#", "sharp"): prop(v, NA) for k, v in prim.head(6).items()}
fw = s.frameworks.fillna("").str.split(";").explode()
fw = fw[fw != ""].value_counts()
pd.DataFrame([{"framework": k, "repos": int(v), "pct": pct(v, NA)} for k, v in fw.items() if v >= 20]).to_csv(TABLES / "frameworks.csv", index=False)
R["frameworks"] = {re.sub(r"[^A-Za-z0-9]", "", k): prop(v, NA) for k, v in fw.head(12).items()}
sdk = s.llm_sdks.fillna("")
R["any_llm"] = prop((sdk != "").sum(), NA)
provs = sdk.str.split(";").explode()
R["llm_providers"] = {re.sub(r"[^A-Za-z0-9]", "", k): prop(v, NA) for k, v in provs[provs != ""].value_counts().items()}
for flag in ["tests", "test_functions", "dockerfile", "compose", "ci", "deploy_config"]:
    R[flag] = prop(s[flag].sum(), NA)
clean = set(act.repo) - set(pre_c.repo) - set(post.repo)
sc = s.loc[s.index.isin(clean)]
R["sensitivity_no_pre_post"] = {"n": len(sc), "tests": pct(sc.tests.sum(), len(sc)), "dockerfile": pct(sc.dockerfile.sum(), len(sc)),
                                "agents_md": pct(sc.agents_md.sum(), len(sc)), "any_llm": pct((sc.llm_sdks.fillna("") != "").sum(), len(sc))}

rd = readme[readme.repo.isin(ACTIVE)].set_index("repo")
R["readme_status"] = {k.replace("_", ""): int(v) for k, v in rd.language.value_counts().items()}
written = rd[rd.language.isin(["russian", "english", "kazakh", "mixed"])]
NWR = len(written)
R["readme_written"] = NWR
for lg in ["russian", "english", "kazakh", "mixed"]:
    R[f"readme_{lg}"] = prop((written.language == lg).sum(), NWR)
R["readme_any_kazakh_letter"] = prop((written.kazakh_letters > 0).sum(), NWR)
R["readme_words"] = med_iqr(written.words)
R["readme_headings"] = med_iqr(written.headings)
R["readme_run_instructions"] = prop(written.install_instructions.sum(), NWR)
R["readme_images"] = prop((written.images > 0).sum(), NWR)
R["readme_deployed_link"] = prop(written.deployed_link.sum(), NWR)
R["readme_mentions_agent"] = prop(written.mentions_agent_tool.sum(), NWR)
subj = wc[wc.is_merge == 0].subject_script.value_counts()
R["subject_script"] = {k: prop(subj.get(k, 0), subj.sum()) for k in ["latin", "cyrillic", "kazakh", "none"]}

tr = act.dropna(subset=["track"]).set_index("repo")
tr = tr.join(s[["tests", "primary_language"]]).join(rd[["language"]])
rows = []
for code, *m_ in CASES:
    sub = tr[tr.track == code]
    wr = sub[sub.language.isin(["russian", "english", "kazakh", "mixed"])]
    rows.append({"track": code, "sector_en": m_[1], "partner_en": m_[3], "repos": len(sub),
                 "median_window_commits": num(sub.window_commits.median()),
                 "tests_pct": pct(sub.tests.sum(), len(sub)), "python_pct": pct((sub.primary_language == "Python").sum(), len(sub)),
                 "readme_russian_pct": pct((wr.language == "russian").sum(), len(wr)),
                 "readme_kazakh_pct": pct((wr.language == "kazakh").sum(), len(wr)), "readme_written": len(wr)})
pd.DataFrame(rows).to_csv(TABLES / "tracks.csv", index=False)
R["tracks"] = {f"t{r_['track']}": {"n": r_["repos"], "commits": r_["median_window_commits"], "tests": r_["tests_pct"],
                                   "python": r_["python_pct"], "kazakh": r_["readme_kazakh_pct"]} for r_ in rows}
lang3 = tr.primary_language.where(tr.primary_language.isin(["Python", "TypeScript", "JavaScript"]), "Other")
R["language_by_track"] = chi2_test(pd.crosstab(tr.track, lang3))
kw = stats.kruskal(*[tr[tr.track == code].window_commits for code, *_ in CASES])
k_, n_ = len(CASES), len(tr)
R["commits_by_track"] = {"h": rhu(kw.statistic, 1), "df": k_ - 1, "p": fmt_p(kw.pvalue),
                         "eps2": r2(kw.statistic / (n_ - 1)), "n": n_,
                         "median_min": min(r_["median_window_commits"] for r_ in rows),
                         "median_max": max(r_["median_window_commits"] for r_ in rows)}

# How similar are solutions to the same brief? Exploratory, added after the plan (analysis/solution_similarity.py;
# features from src/extract_solutions.py). Pairs of track-labelled active repositories; Jaccard index per kind of item.
SOL_RUNS = 999
rng_sol = np.random.default_rng(20260923)
sol = pd.read_json(DATA / "solutions_private.jsonl", lines=True).set_index("repo").reindex(tr.index)
groups = tr.track.values
traced = pd.Series(any_tool, index=s.index).reindex(tr.index).fillna(False).values.astype(bool)
S_: dict = {"n": len(tr), "pairs_within": int(sum(k * (k - 1) // 2 for k in pd.Series(groups).value_counts())),
            "traced": prop(traced.sum(), len(tr))}
for kind in ("deps", "paths", "headings", "blobs"):
    sets = [set(v) if isinstance(v, list) else set() for v in sol[kind]]
    j = ss.jaccard_matrix(sets)
    w_, a_ = ss.within_across(j, groups)
    ex = ss.excess_by_status(j, groups, traced)
    S_[kind] = {"within": Fixed(w_, 3), "across": Fixed(a_, 3), "ratio": r2(w_ / a_),
                "p": fmt_p(ss.permutation_p(j, groups, SOL_RUNS, rng_sol)),
                "median_items": num(np.median([len(x) for x in sets])),
                **{f"{k}_{m}": Fixed(v[m], 3) for k, v in ex.items() for m in ("within", "across", "excess")},
                "status_p": fmt_p(ss.status_permutation_p(j, groups, traced, SOL_RUNS, rng_sol))}
blob_sets = [set(v) if isinstance(v, list) else set() for v in sol.blobs]
same_track, other_track = np.zeros(len(tr), dtype=bool), np.zeros(len(tr), dtype=bool)
for i, (b_i, g_i) in enumerate(zip(blob_sets, groups)):
    if b_i:
        same_track[i] = any(b_i & b_k for k, (b_k, g_k) in enumerate(zip(blob_sets, groups)) if k != i and g_k == g_i)
        other_track[i] = any(b_i & b_k for b_k, g_k in zip(blob_sets, groups) if g_k != g_i)
where_blob: dict = {}
for b_i, g_i in zip(blob_sets, groups):
    for oid in b_i:
        where_blob.setdefault(oid, []).append(g_i)
shared = [set(v) for v in where_blob.values() if len(v) > 1]
S_["shared_files"] = {"one_track": sum(len(v) == 1 for v in shared), "several_tracks": sum(len(v) > 1 for v in shared)}
S_["identical_code_same_track"] = prop(same_track.sum(), len(tr))
S_["identical_code_other_track"] = prop(other_track.sum(), len(tr))
dep_sets = [set(v) if isinstance(v, list) else set() for v in sol.deps]
ss.distinctive_items(dep_sets, groups, 0.25, 2.0, 6).round(3).to_csv(TABLES / "solution_distinctive_deps.csv", index=False)
R["solutions"] = S_

# How each team solved its brief, coded from README and file list with a fixed codebook by an LLM (exploratory;
# src/llm_codebook.py; cached answers in data/llm_codebook/responses.jsonl, last valid answer per repository).
answers = {}
for line in (DATA / "llm_codebook" / "responses.jsonl").open(encoding="utf-8"):
    rec = json.loads(line)
    if rec["answer"].strip():
        answers[rec["repo"]] = {**json.loads(rec["answer"]), "model": rec["model"], "time": rec["time_utc"]}
ap = pd.DataFrame.from_dict(answers, orient="index").reindex(tr.index)
NAP = int(ap.core_method.notna().sum())
ap["pattern"] = np.select([ap.core_method.isin(["algorithm", "ml_model"]) & (ap.llm_role == "support"),
                           ap.llm_role == "core", ap.llm_role == "none"], ["explains", "llm_task", "no_llm"], "other")
ct = pd.crosstab(tr.track, ap.core_method)
top_share = ct.max(axis=1) / ct.sum(axis=1)
sdk_ = (s.llm_sdks.fillna("") != "").reindex(tr.index)
uses_llm = ap.llm_role.isin(["core", "support"])
A_ = {"n": NAP, "model": ap.model.dropna().iloc[0], "first": ap.time.min()[:10], "last": ap.time.max()[:10],
      "core": {k: prop((ap.core_method == k).sum(), NAP) for k in ["algorithm", "llm_prompt", "llm_agent", "ml_model",
                                                                     "pretrained", "unclear"]},
      "pattern": {k: prop((ap.pattern == k).sum(), NAP) for k in ["explains", "llm_task", "no_llm", "other"]},
      "web_app": prop((ap.interface == "web_app").sum(), NAP),
      "evaluation": prop((ap.evaluation == True).sum(), NAP),  # noqa: E712
      "by_track": chi2_test(ct),
      "briefs_top75": int((top_share >= 0.75).sum()),
      "sdk_given_llm": prop((uses_llm & sdk_).sum(), uses_llm.sum()),
      "sdk_kappa": r2(cohen_kappa_score(uses_llm[ap.llm_role != "unclear"], sdk_[ap.llm_role != "unclear"])),
      "small_cells_rare": int((stats.chi2_contingency(ct)[3][:, [ct.columns.get_loc(c) for c in ("pretrained", "unclear")]] < 5).sum()),
      "no_sdk_given_no_llm": prop(((ap.llm_role == "none") & ~sdk_).sum(), (ap.llm_role == "none").sum())}
labels_m = {"algorithm": "rules or algorithm", "llm_prompt": "LLM prompt", "llm_agent": "LLM agent",
            "ml_model": "trained model", "pretrained": "pretrained model"}
dist = pd.read_csv(TABLES / "solution_distinctive_deps.csv", dtype={"group": str})
rows_ap = []
for code, *_ in CASES:
    row = ct.loc[code]
    eff = float(np.exp(stats.entropy(row[row > 0])))
    libs = dist[dist.group == code].sort_values("lift", ascending=False).head(2)
    rows_ap.append({"track": code, "n": int(row.sum()), "top_method": labels_m.get(row.idxmax(), row.idxmax()),
                    "top_share": pct(row.max(), row.sum()), "effective_methods": rhu(eff, 1),
                    "llm_task_pct": pct((ap.loc[tr.track == code, "llm_role"] == "core").sum(), row.sum()),
                    "libraries": "; ".join(f"{i} ({pct(sh * 100, 100):.0f}%)" for i, sh in zip(libs.item, libs.share_in)) or "--"})
pd.DataFrame(rows_ap).to_csv(TABLES / "solution_approaches.csv", index=False)
A_["tracks"] = {f"t{r_['track']}": {k: v for k, v in r_.items() if k != "track"} for r_ in rows_ap}
R["approach"] = A_
F["rq3"] = R

# ------------------------------------------------------------------ RQ4 risk
K: dict = {}
fnd = pd.read_csv(DATA / "secrets_private" / "findings.csv").reset_index().rename(columns={"index": "finding"})
prec = pd.read_csv(DATA / "secrets_private" / "precision.csv")
K["scanned_repos"] = int(repos["any"].sum())
generic = fnd[fnd.rule_id == "generic-api-key"]
K["generic"] = {"findings": len(generic), "repos": int(generic.repo.nunique()),
                "data_files_pct": pct(generic.file_ext.isin([".json", ".jsonl", ".txt", ".csv"]).sum(), len(generic))}
pv = fnd.merge(prec, on=["finding", "rule_id"])
K["provider"] = {"findings": len(pv), "placeholder": int((pv["class"] == "placeholder").sum()),
                 "plausible": int((pv["class"] == "plausible").sum())}
pl = pv[pv["class"] == "plausible"]
K["provider"]["repos_not_active"] = int((~pl.repo.isin(ACTIVE)).groupby(pl.repo).any().sum())
pla = pl[pl.repo.isin(ACTIVE)]
K["repos_provider"] = prop(pla.repo.nunique(), NA)
K["repos_provider_final"] = prop(pla[pla.in_head == 1].repo.nunique(), NA)
K["provider_rules"] = {re.sub(r"[^a-z]", "", k): {"repos": int(g.repo.nunique()), "final": int(g[g.in_head == 1].repo.nunique())}
                       for k, g in pla.groupby("rule_id")}
oa = pla[pla.rule_id == "openai-api-key"]
K["openai"] = {"findings": len(oa), **{k: v for k, v in prop(oa.repo.nunique(), NA).items()},
               "final": prop(oa[oa.in_head == 1].repo.nunique(), NA)}
K["openai_files"] = {"env_example": int(oa.file.str.contains(r"\.env\.example$|\.example$").sum()),
                     "env": int(oa.file.str.contains(r"(?:^|/)\.env$").sum()),
                     "source_or_text": int((~oa.file.str.contains(r"\.env")).sum())}
K["openai_files"]["env_other"] = len(oa) - sum(K["openai_files"].values())
kd = pd.to_datetime(oa.date, utc=True).map(lambda t: t.timestamp())
K["openai_in_window"] = prop(((kd >= START) & (kd < END)).sum(), len(oa))
# Were the commits that added key strings agent-signed? Compared with all window commits of the same repositories.
kc = oa.merge(commits[["repo", "sha", "agent_kind", "agent_trailer", "agent_generated_marker", "agent_account"]],
              left_on=["repo", "commit"], right_on=["repo", "sha"], how="left")
kc_signed = ((kc.agent_trailer == 1) | (kc.agent_generated_marker == 1) | (kc.agent_account == 1)) & (kc.agent_kind != "bot")
same = wc[wc.repo.isin(oa.repo)]
same_signed = same.index.isin(sig.index)
K["key_commits"] = {"matched": int(kc.sha.notna().sum()), "findings": len(kc), "signed": prop(kc_signed.sum(), kc.sha.notna().sum()),
                    "signed_by_kind": {k: int(v) for k, v in kc[kc_signed].agent_kind.value_counts().items()},
                    "baseline_signed_same_repos": prop(same_signed.sum(), len(same))}
for flag in ["env_file_committed", "env_example", "gitignore_covers_env", "node_modules_committed",
             "virtualenv_committed", "pycache_committed"]:
    K[flag] = prop(s[flag].sum(), NA)
h = s[["gitignore_covers_env", "env_example"]].copy()
h["key"] = h.index.isin(oa.repo).astype(int)
h["llm"] = (s.llm_sdks.fillna("") != "").astype(int)
crude = pd.crosstab(h.gitignore_covers_env, h.key)
K["gitignore_assoc"] = {"with_ignore": pct(h[h.gitignore_covers_env == 1].key.sum(), (h.gitignore_covers_env == 1).sum()),
                        "without_ignore": pct(h[h.gitignore_covers_env == 0].key.sum(), (h.gitignore_covers_env == 0).sum()),
                        **{k: v for k, v in chi2_test(crude).items() if k in ("p", "v")},
                        "ignore_among_llm": pct(h[h.llm == 1].gitignore_covers_env.sum(), (h.llm == 1).sum()),
                        "ignore_among_no_llm": pct(h[h.llm == 0].gitignore_covers_env.sum(), (h.llm == 0).sum()),
                        "example_among_ignore": pct(h[h.gitignore_covers_env == 1].env_example.sum(), (h.gitignore_covers_env == 1).sum()),
                        "example_among_no_ignore": pct(h[h.gitignore_covers_env == 0].env_example.sum(), (h.gitignore_covers_env == 0).sum())}
strata = [pd.crosstab(g.gitignore_covers_env, g.key).reindex(index=[1, 0], columns=[1, 0], fill_value=0).values
          for _, g in h.groupby("llm")]
st = StratifiedTable(strata)
lo, hi = st.oddsratio_pooled_confint()
K["gitignore_assoc"]["mh"] = {"or": r2(st.oddsratio_pooled), "lo": r2(lo), "hi": r2(hi), "p": fmt_p(st.test_null_odds().pvalue)}
K["key_by_example"] = {"with_example": pct(h[h.env_example == 1].key.sum(), (h.env_example == 1).sum()),
                       "without_example": pct(h[h.env_example == 0].key.sum(), (h.env_example == 0).sum())}
F["rq4"] = K

# ------------------------------------------------------------------ validation and sensitivity
import subprocess  # noqa: E402

api = pd.read_csv(DATA / "commit_counts.csv").set_index("name").commit_count
clone = {n: int(subprocess.run(["git", f"--git-dir={DATA / 'clones' / (n + '.git')}", "rev-list", "--count", "HEAD"],
                               capture_output=True, text=True).stdout.strip() or -1) for n in repos.repo}
old = pd.read_csv(DATA / "hackalem_repos_analysis.csv")
fixed16 = set(json.loads((DATA / "verification" / "template_counted.json").read_text()))
old.loc[old.repo.isin(fixed16), "participant_commits"] -= 1
cmp_ = repos.merge(old, on="repo")
recount = json.loads((PAPER / "checks" / "recompute_core_result.json").read_text())
V: dict = {"clone_api_agree": int(sum(clone[n] == api[n] for n in repos.repo)),
           "template_found": int(repos.template_found.sum()), "history_rewritten": int(N - repos.template_found.sum()),
           "template_audit_n": len(json.loads((DATA / "verification" / "template_check.json").read_text())),
           "template_fixes": len(fixed16),
           "pr_only_repos": int((repos.pr_only_commits > 0).sum()), "pr_only_commits": int(repos.pr_only_commits.sum()),
           "earlier_same_team": int((cmp_.team_commits == cmp_.participant_commits).sum()),
           "earlier_same_window": int((cmp_.window_commits == cmp_.commits_13_18_local).sum()),
           "earlier_same_hours": int((cmp_.hours_active == cmp_.hours_with_commits_of_5).sum()),
           "recount_team": recount["team_commits_agree"], "recount_window": recount["window_commits_agree"],
           "recount_hours": recount["hours_active_agree"]}
V["author_time_active"] = int((repos.window_commits_author_time > 0).sum())
V["author_time_window_commits"] = int(repos.window_commits_author_time.sum())
for shift in (-60, -30, 30, 60):
    lo_, hi_ = START + 60 * shift, END + 60 * shift
    V[f"shift_{'m' if shift < 0 else 'p'}{abs(shift)}_active"] = int(commits[(commits.ctime >= lo_) & (commits.ctime < hi_)].repo.nunique())
kwl = pd.read_csv(DATA / "verification" / "kw_labels.csv")
kwa = kwl[kwl.repo.isin(ACTIVE)].merge(labels[["repo", "raw_track"]], on="repo")
kwa["kw_track"] = kwa.kw.str.extract(r"^(\d{2})\b", expand=False)
dec = kwa.dropna(subset=["raw_track", "kw_track"])
V["tracks_kw"] = {"decisive": len(dec), "agree": int((dec.raw_track == dec.kw_track).sum()),
                  "agree_pct": pct((dec.raw_track == dec.kw_track).sum(), len(dec)),
                  "kappa": r2(cohen_kappa_score(dec.raw_track, dec.kw_track)),
                  "labelled_no_readme_text": int((kwa.raw_track.notna() & kwa.kw.isin(["boilerplate/none"])).sum()),
                  "unclear_with_kw": int((kwa.raw_track.isna() & kwa.kw_track.notna()).sum())}
sample = pd.read_csv(DATA / "readme_lang_sample.csv")
xlsx = DATA / "readme_lang_sample.xlsx"
if xlsx.exists():
    lab_x = pd.read_excel(xlsx, sheet_name="label").rename(columns={"human_language": "human_x"})[["item", "human_x"]]
    sample = sample.merge(lab_x, on="item", how="left")
    sample["human_language"] = sample.human_x.where(sample.human_x.notna(), sample.human_language)
key = pd.read_csv(DATA / "readme_lang_sample_key.csv")
lab = sample.merge(key, on=["item", "repo"])
lab = lab[lab.human_language.fillna("").str.strip() != ""]
V["readme_sample"] = {"n": len(sample), "labelled": len(lab)}
if len(lab):
    lab["human_language"] = lab.human_language.str.strip().str.lower()
    V["readme_sample"]["agree"] = int((lab.human_language == lab.auto_language).sum())
    V["readme_sample"]["kappa"] = r2(cohen_kappa_score(lab.human_language, lab.auto_language))
    V["readme_sample"]["agree_pct"] = pct(V["readme_sample"]["agree"], len(lab))
    # The sample was stratified by the automatic label; weight each stratum's agreement by its share of the
    # written READMEs of repositories with team commits (the population the sample was drawn from).
    pop = readme[readme.language.isin(["russian", "english", "kazakh", "mixed"])].language.value_counts()
    acc = lab.assign(ok=lab.human_language == lab.auto_language).groupby("auto_language").ok.mean()
    V["readme_sample"]["weighted_acc"] = rhu(100 * sum(pop[k] * acc.get(k, 0) for k in pop.index) / pop.sum(), 0)
    for k in ["russian", "english", "kazakh", "mixed"]:
        sub = lab[lab.auto_language == k]
        V["readme_sample"][f"agree_{k}"] = {"n": int((sub.human_language == k).sum()), "of": len(sub)}
upd_wave = updated[(updated >= datetime(2026, 9, 23, 18, 0, tzinfo=TZ)) & (updated < datetime(2026, 9, 23, 19, 0, tzinfo=TZ))]
late = updated[(updated >= datetime(2026, 9, 23, 19, 0, tzinfo=TZ)) & (updated < datetime(2026, 9, 24, 0, 0, tzinfo=TZ))]
V["archive_later"] = {"n": len(late), "times": ", ".join(sorted(late.dt.strftime("%H:%M")))}
V["archive_wave"] = {"n": len(upd_wave), "first": upd_wave.min().strftime("%H:%M"), "last": upd_wave.max().strftime("%H:%M"),
                     "all_archived": int(meta.archived.astype(str).str.lower().eq("true").sum())}
F["validation"] = V
F["tracks_count"] = len(CASES)
F["literature"] = {"searches": len(pd.read_csv(PAPER / "literature" / "search_log.csv")),
                   "screened": len(pd.read_csv(PAPER / "literature" / "screening.csv"))}

OUT.write_text(to_json(F), encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)} ({len(json.dumps(F))} bytes)")
