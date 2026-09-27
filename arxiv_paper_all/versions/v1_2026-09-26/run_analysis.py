"""M3: every statistic in the paper, following analysis_plan.md -> facts_paper.json + tables/.

Inputs are the private files built by src/ (data/repo_table.csv, stack.csv, commits.csv,
commit_repo_features.csv, readme_features.csv, secrets_private/). Outputs contain only
aggregates. Percentages are rounded to one decimal, p-values formatted as strings.
Seeds are fixed, so a rerun reproduces every number.
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint
import statsmodels.api as sm

PAPER = Path(__file__).resolve().parent.parent
ROOT = PAPER.parent
DATA = ROOT / "data"
TABLES = PAPER / "tables"
OUT = PAPER / "analysis" / "facts_paper.json"
sys.path.insert(0, str(ROOT / "src"))
from plot_bilingual_charts import CASE_FIXES, CASES  # noqa: E402

TZ = timezone(timedelta(hours=5))
START = datetime(2026, 9, 23, 13, 0, tzinfo=TZ).timestamp()
END = datetime(2026, 9, 23, 18, 0, tzinfo=TZ).timestamp()
RNG = np.random.default_rng(2026)
F: dict = {}


class Fixed(float):
    """A rounded float that keeps its trailing zeros in facts_paper.json (1.170, not 1.17)."""

    def __new__(cls, value, places: int):
        obj = super().__new__(cls, round(float(value), places))
        obj.places = places
        return obj


def r3(value) -> Fixed:
    return Fixed(value, 3)


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
    return round(100 * part / whole, 1) if whole else 0.0


def wilson(part, whole) -> tuple[float, float]:
    lo, hi = proportion_confint(part, whole, method="wilson")
    return round(100 * lo, 1), round(100 * hi, 1)


def share(key: str, part: int, whole: int) -> None:
    """Store n, %, and Wilson 95% CI under a common key."""
    lo, hi = wilson(part, whole)
    F[key] = {"n": int(part), "pct": pct(part, whole), "lo": lo, "hi": hi}


def fmt_p(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"= {p:.3f}"


def boot_median(values, n=10_000) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    meds = np.median(RNG.choice(values, size=(n, len(values)), replace=True), axis=1)
    return float(np.median(values)), float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))


def cliffs_delta(a, b) -> float:
    a, b = np.asarray(a), np.asarray(b)
    greater = sum((x > b).sum() for x in a)
    less = sum((x < b).sum() for x in a)
    return r3((greater - less) / (len(a) * len(b)))


def cramers_v(table) -> float:
    chi2 = stats.chi2_contingency(table, correction=False)[0]
    n = table.values.sum()
    return r3(math.sqrt(chi2 / (n * (min(table.shape) - 1))))


# ------------------------------------------------------------------ load
repos = pd.read_csv(DATA / "repo_table.csv")
stack = pd.read_csv(DATA / "stack.csv")
crepo = pd.read_csv(DATA / "commit_repo_features.csv")
commits = pd.read_csv(DATA / "commits.csv")
readme = pd.read_csv(DATA / "readme_features.csv")
labels = pd.read_csv(DATA / "hackalem_repos_analysis.csv")[["repo", "case_guess"]]
labels["track"] = labels.case_guess.str.extract(r"^(\d{2})\b", expand=False)
for repo, (_, new) in CASE_FIXES.items():
    labels.loc[labels.repo == repo, "track"] = new

repos["any"] = repos.team_commits > 0
repos["active"] = repos.window_commits > 0
N = len(repos)
with_commits = repos[repos["any"]].repo
active = repos[repos.active].repo
NW, NA = len(with_commits), len(active)

# ------------------------------------------------------------------ RQ1 participation
F["repos_total"] = N
F["repos_with_commits"] = NW
F["repos_active"] = NA
F["repos_empty"] = int((~repos["any"]).sum())
F["repos_outside_only"] = int((repos["any"] & ~repos.active).sum())
F["pct_empty"] = pct(F["repos_empty"], N)
F["pct_with_commits"] = pct(NW, N)
F["pct_active"] = pct(NA, N)
act_labels = labels[labels.repo.isin(active)]
F["repos_matched_track"] = int(act_labels.track.notna().sum())
F["repos_track_unclear"] = int(act_labels.track.isna().sum())
F["pct_matched_of_active"] = pct(F["repos_matched_track"], NA)
F["label_fixes"] = len(CASE_FIXES)

created = pd.to_datetime(repos.created_at, utc=True).dt.tz_convert(TZ)
day = created.dt.date.astype(str)
groups = pd.cut(pd.to_datetime(day), bins=pd.to_datetime(["2000-01-01", "2026-09-01", "2026-09-15", "2026-09-22", "2026-09-23", "2026-09-24"]),
                right=False, labels=["before_sep01", "sep01_14", "sep15_21", "sep22", "sep23"])
repos["reg_group"] = groups
reg = repos.groupby("reg_group", observed=False).agg(n=("repo", "size"), active=("active", "sum"))
F["registration"] = {}
for g, row in reg.iterrows():
    lo, hi = wilson(row.active, row.n) if row.n else (0, 0)
    F["registration"][g] = {"n": int(row.n), "active": int(row.active), "pct": pct(row.active, row.n), "lo": lo, "hi": hi}
tab = pd.crosstab(repos.reg_group, repos.active)
chi2, p, dof, _ = stats.chi2_contingency(tab)
F["registration_chi2"] = {"chi2": round(chi2, 1), "df": int(dof), "p": fmt_p(p), "v": cramers_v(tab)}
days_before = (START - created.map(lambda t: t.timestamp())) / 86400
X = sm.add_constant((days_before / 7).clip(lower=0))
logit = sm.Logit(repos.active.astype(int), X).fit(disp=0)
ci = logit.conf_int().iloc[1]
F["registration_logit"] = {"or_per_week": r3(math.exp(logit.params.iloc[1])),
                           "lo": r3(math.exp(ci.iloc[0])), "hi": r3(math.exp(ci.iloc[1])),
                           "p": fmt_p(logit.pvalues.iloc[1])}
F["registered_day_before"] = int((day == "2026-09-22").sum())
# Repositories created in one burst on the evening before the event (organiser batch, not organic sign-ups).
hour = created.dt.hour
batch = (day == "2026-09-22") & hour.isin([18, 19])
per_min = created[batch].dt.floor("min").value_counts()
F["batch"] = {"n": int(batch.sum()), "active": int(repos.active[batch].sum()),
              "pct_active": pct(repos.active[batch].sum(), batch.sum()), "max_per_minute": int(per_min.max())}
organic = created[~batch & (day < "2026-09-22")]
F["organic_max_per_minute"] = int(organic.dt.floor("min").value_counts().max())
keep = ~batch & (day < "2026-09-22")
Xs = sm.add_constant((days_before[keep] / 7).clip(lower=0))
logit_s = sm.Logit(repos.active[keep].astype(int), Xs).fit(disp=0)
ci_s = logit_s.conf_int().iloc[1]
F["registration_logit_no_batch"] = {"n": int(keep.sum()), "or_per_week": r3(math.exp(logit_s.params.iloc[1])),
                                    "lo": r3(math.exp(ci_s.iloc[0])), "hi": r3(math.exp(ci_s.iloc[1])),
                                    "p": fmt_p(logit_s.pvalues.iloc[1])}

names = repos.repo.str.replace(r"^hack-[0-9a-f]{8}-", "", regex=True)
repos["team_name"] = names
dup = repos.groupby("team_name").agg(n=("repo", "size"), active=("active", "sum"))
dup_multi = dup[(dup.n > 1) & (dup.index != "team")]
F["names_on_multiple_repos"] = int((dup.n > 1).sum())
F["dup_groups_excl_generic"] = len(dup_multi)
F["dup_groups_one_active"] = int((dup_multi.active == 1).sum())
F["dup_repos_excl_generic"] = int(dup_multi.n.sum())

# ------------------------------------------------------------------ RQ2 work rhythm
wc = commits[(commits.ctime >= START) & (commits.ctime < END)].copy()
F["window_commits"] = len(wc)
F["team_commits_total"] = len(commits)
wc["hour"] = ((wc.ctime - START) // 3600).astype(int) + 13
hourly = wc.groupby("hour").size().reindex(range(13, 18), fill_value=0)
F["hourly_commits"] = {f"h{h}": int(v) for h, v in hourly.items()}
F["pct_last_hour"] = pct(hourly[17], len(wc))
bins10 = ((wc.ctime - START) // 600).astype(int)
per10 = bins10.value_counts().sort_index()
F["peak10_commits"] = int(per10.max())
peak_start = datetime.fromtimestamp(START + 600 * int(per10.idxmax()), TZ)
F["peak10_start"] = peak_start.strftime("%H:%M")
F["peak10_end"] = (peak_start + timedelta(minutes=10)).strftime("%H:%M")
day_start = datetime(2026, 9, 23, 11, 0, tzinfo=TZ).timestamp()
day_end = datetime(2026, 9, 23, 19, 0, tzinfo=TZ).timestamp()
timeline = commits[(commits.ctime >= day_start) & (commits.ctime < day_end)]
tl = ((timeline.ctime - day_start) // 600).astype(int).value_counts().reindex(range(48), fill_value=0).sort_index()
TABLES.mkdir(exist_ok=True)
pd.DataFrame({"minutes_after_11": tl.index * 10, "commits": tl.values}).to_csv(TABLES / "timeline_10min.csv", index=False)
post = commits[(commits.ctime >= END) & (commits.ctime < day_end)]
F["post_deadline_commits"] = len(post)
F["post_deadline_repos"] = int(post.repo.nunique())

per_team = wc.groupby("repo").agg(first=("ctime", "min"), last=("ctime", "max"), n=("ctime", "size"))
per_team["last_hour"] = wc[wc.hour == 17].groupby("repo").size().reindex(per_team.index, fill_value=0)
per_team["deadline_share"] = per_team.last_hour / per_team.n
m, lo, hi = boot_median((per_team["first"] - START) / 60)
F["first_commit_min"] = {"median": round(m), "lo": round(lo), "hi": round(hi)}
m, lo, hi = boot_median((END - per_team["last"]) / 60)
F["last_commit_min_before_deadline"] = {"median": round(m), "lo": round(lo), "hi": round(hi)}
m, lo, hi = boot_median(per_team.n)
F["window_commits_per_team"] = {"median": round(m), "lo": round(lo), "hi": round(hi),
                                "q1": int(per_team.n.quantile(0.25)), "q3": int(per_team.n.quantile(0.75))}
F["deadline_share_median_pct"] = round(100 * per_team.deadline_share.median(), 1)
share("teams_majority_last_hour", int((per_team.deadline_share > 0.5).sum()), len(per_team))
share("teams_commit_last_hour", int((per_team.last_hour > 0).sum()), len(per_team))
hours_dist = repos[repos.active].hours_active.value_counts().reindex(range(1, 6), fill_value=0)
F["hours_active"] = {f"h{k}": int(v) for k, v in hours_dist.items()}
share("teams_4plus_hours", int(hours_dist.loc[4:].sum()), NA)
share("teams_all_5_hours", int(hours_dist.loc[5]), NA)

profiles = wc.groupby(["repo", "hour"]).size().unstack(fill_value=0).reindex(columns=range(13, 18), fill_value=0)
shares = profiles.div(profiles.sum(axis=1), axis=0)
sil = {}
for k in range(2, 7):
    km = KMeans(n_clusters=k, n_init=20, random_state=42).fit(shares)
    sil[k] = silhouette_score(shares, km.labels_, random_state=42)
best = max(sil, key=sil.get)
km = KMeans(n_clusters=best, n_init=20, random_state=42).fit(shares)
F["rhythm_k"] = best
F["rhythm_silhouette"] = {str(k): r3(v) for k, v in sil.items()}
order = np.argsort([c @ np.arange(5) for c in km.cluster_centers_])  # early -> late centre of mass
cent = []
for rank, c in enumerate(order):
    size = int((km.labels_ == c).sum())
    cent.append({"cluster": rank + 1, "size": size, "pct": pct(size, len(shares)),
                 **{f"h{13 + i}": round(100 * km.cluster_centers_[c][i], 1) for i in range(5)}})
F["rhythm_clusters"] = cent
F["rhythm"] = {f"c{c['cluster']}": {k: v for k, v in c.items() if k != "cluster"} for c in cent}
pd.DataFrame(cent).to_csv(TABLES / "rhythm_clusters.csv", index=False)

# ------------------------------------------------------------------ RQ3 technology
s = stack[stack.repo.isin(with_commits)].copy()
F["stack_n"] = len(s)
prim = s.primary_language.fillna("none").value_counts()
F["primary_language"] = {lang.replace("+", "p").replace("#", "sharp"): {"n": int(v), "pct": pct(v, len(s))}
                         for lang, v in prim.head(6).items()}
for flag in ["dockerfile", "compose", "tests", "ci", "deploy_config"]:
    share(f"has_{flag}", int(s[flag].sum()), len(s))
sdk = s.llm_sdks.fillna("").str.split(";")
share("any_llm_sdk", int((s.llm_sdks.fillna("") != "").sum()), len(s))
prov = sdk.explode()
prov = prov[prov != ""].value_counts()
F["llm_providers"] = {p.replace(" ", ""): {"n": int(v), "pct": pct(v, len(s))} for p, v in prov.items()}
fw = s.frameworks.fillna("").str.split(";").explode()
fw = fw[fw != ""].value_counts()
fw_rows = [{"framework": k, "repos": int(v), "pct": pct(v, len(s))} for k, v in fw.items() if v >= 20]
pd.DataFrame(fw_rows).to_csv(TABLES / "frameworks.csv", index=False)
F["frameworks_top"] = {r["framework"].replace(".", "").replace(" ", "").replace("-", "").replace("(dep)", "dep"): {"n": r["repos"], "pct": r["pct"]}
                       for r in fw_rows[:12]}

tr = s.merge(labels[["repo", "track"]], on="repo").dropna(subset=["track"])
tr = tr[tr.repo.isin(active)]
tr["lang3"] = tr.primary_language.where(tr.primary_language.isin(["Python", "TypeScript", "JavaScript"]), "Other")
ct = pd.crosstab(tr.track, tr.lang3)
chi2, p, dof, _ = stats.chi2_contingency(ct)
F["lang_by_track"] = {"chi2": round(chi2, 1), "df": int(dof), "p": fmt_p(p), "v": cramers_v(ct), "n": int(ct.values.sum())}

# ------------------------------------------------------------------ RQ4 agent footprint
agent_cols = ["agents_md", "claude_md", "gemini_md", "cursor_rules", "copilot_instructions", "other_agent_rules"]
share("agents_md", int(s.agents_md.sum()), len(s))
share("claude_md", int(s.claude_md.sum()), len(s))
share("any_agent_file", int((s[agent_cols].sum(axis=1) > 0).sum()), len(s))
F["other_agent_files"] = int((s[["gemini_md", "cursor_rules", "copilot_instructions", "other_agent_rules"]].sum(axis=1) > 0).sum())
c = crepo[crepo.repo.isin(with_commits)]
share("repos_agent_signed", int((c.agent_signed_commits > 0).sum()), len(c))
share("repos_agent_branch", int((c.agent_branches > 0).sum()), len(c))
F["repos_codex_branch"] = int(c.agent_branch_kinds.fillna("").str.contains("codex").sum())
share("repos_pr_refs", int((c.pr_refs > 0).sum()), len(c))
sig = commits[(commits.agent_trailer == 1) | (commits.agent_generated_marker == 1) | (commits.agent_account == 1)]
F["agent_signed_commits"] = len(sig)
F["pct_agent_signed_commits"] = pct(len(sig), len(commits))
kinds = sig.agent_kind.fillna("").value_counts()
F["agent_signed_by_kind"] = {k if k else "unknown": int(v) for k, v in kinds.items()}
share("conventional_commits", int(commits.conventional.sum()), len(commits))
share("merge_commits", int(commits.is_merge.sum()), len(commits))

sa = s[s.repo.isin(active)].merge(repos[["repo", "window_commits", "hours_active"]], on="repo")
with_a, without_a = sa[sa.agents_md == 1], sa[sa.agents_md == 0]
tests_tab = pd.crosstab(sa.agents_md, sa.tests)
tests_chi = stats.chi2_contingency(tests_tab)
raw = [stats.mannwhitneyu(with_a.window_commits, without_a.window_commits).pvalue,
       stats.mannwhitneyu(with_a.hours_active, without_a.hours_active).pvalue,
       tests_chi[1]]
holm = multipletests(raw, method="holm")[1]
F["agents_md_assoc"] = {
    "n_with": len(with_a), "n_without": len(without_a),
    "commits_median_with": int(with_a.window_commits.median()), "commits_median_without": int(without_a.window_commits.median()),
    "commits_delta": cliffs_delta(with_a.window_commits, without_a.window_commits), "commits_p": fmt_p(holm[0]),
    "hours_median_with": int(with_a.hours_active.median()), "hours_median_without": int(without_a.hours_active.median()),
    "hours_delta": cliffs_delta(with_a.hours_active, without_a.hours_active), "hours_p": fmt_p(holm[1]),
    "tests_pct_with": pct(with_a.tests.sum(), len(with_a)), "tests_pct_without": pct(without_a.tests.sum(), len(without_a)),
    "tests_v": cramers_v(tests_tab), "tests_p": fmt_p(holm[2]),
}
nonmerge = commits[commits.is_merge == 0].copy()
nonmerge["lines"] = nonmerge.added + nonmerge.deleted
signed = (nonmerge.agent_trailer == 1) | (nonmerge.agent_generated_marker == 1) | (nonmerge.agent_account == 1)
F["commit_size"] = {"median_all": int(nonmerge.lines.median()), "q1_all": int(nonmerge.lines.quantile(0.25)),
                    "q3_all": int(nonmerge.lines.quantile(0.75)),
                    "median_signed": int(nonmerge[signed].lines.median()), "median_unsigned": int(nonmerge[~signed].lines.median())}

# ------------------------------------------------------------------ RQ5 documentation
r = readme[readme.repo.isin(with_commits)]
F["readme_n"] = len(r)
lang = r.language.value_counts()
F["readme_language_counts"] = {k.replace("_", ""): int(v) for k, v in lang.items()}
written = r[r.language.isin(["russian", "english", "kazakh", "mixed"])]
F["readme_written_n"] = len(written)
for lg in ["russian", "english", "kazakh", "mixed"]:
    share(f"readme_{lg}", int((written.language == lg).sum()), len(written))
share("readme_any_kazakh_letter", int((r.kazakh_letters > 0).sum()), len(r))
for flag in ["install_instructions", "deployed_link", "video_link", "mentions_agent_tool"]:
    share(f"readme_{flag}", int(r[flag].sum()), len(r))
share("readme_images", int((r.images > 0).sum()), len(r))
m, lo, hi = boot_median(written.words)
F["readme_words"] = {"median": round(m), "lo": round(lo), "hi": round(hi)}
F["readme_headings_median"] = int(written.headings.median())
scr = commits.script.value_counts()
for k in ["latin", "cyrillic", "kazakh"]:
    share(f"commit_script_{k}", int(scr.get(k, 0)), len(commits))

# ------------------------------------------------------------------ RQ6 security
fnd = pd.read_csv(DATA / "secrets_private" / "findings.csv").reset_index().rename(columns={"index": "finding"})
prec = pd.read_csv(DATA / "secrets_private" / "precision.csv")
fnd = fnd[fnd.repo.isin(with_commits)]
generic = fnd[fnd.rule_id == "generic-api-key"]
F["generic_findings"] = len(generic)
F["generic_repos"] = int(generic.repo.nunique())
F["generic_in_data_files_pct"] = pct(generic.file_ext.isin([".json", ".jsonl", ".txt", ".csv"]).sum(), len(generic))
prov_f = fnd.merge(prec, on=["finding", "rule_id"])
prov_all = prov_f.copy()
prov_f = prov_f[prov_f["class"] == "plausible"]
F["provider_findings"] = len(prov_all)
F["provider_placeholder"] = int((prov_all["class"] == "placeholder").sum())
share("repos_provider_secret", int(prov_f.repo.nunique()), NW)
share("repos_provider_secret_final", int(prov_f[prov_f.in_head == 1].repo.nunique()), NW)
oa = prov_f[prov_f.rule_id == "openai-api-key"]
F["openai_findings"] = len(oa)
share("repos_openai_key", int(oa.repo.nunique()), NW)
share("repos_openai_key_final", int(oa[oa.in_head == 1].repo.nunique()), NW)
F["openai_key_files"] = {"env_example": int(oa.file.str.contains(r"\.env\.example$|\.example$").sum()),
                         "env": int(oa.file.str.contains(r"(?:^|/)\.env$").sum()),
                         "other": int((~oa.file.str.contains(r"\.env")).sum())}
F["openai_key_files"]["env_other"] = len(oa) - sum(F["openai_key_files"].values())
kdates = pd.to_datetime(oa.date, utc=True).map(lambda t: t.timestamp())
F["openai_keys_in_window_pct"] = pct(((kdates >= START) & (kdates < END)).sum(), len(oa))
F["provider_rules_repos"] = {k.replace("-", ""): int(v) for k, v in prov_f.groupby("rule_id").repo.nunique().items()}
F["provider_rules_final"] = {k.replace("-", ""): int(v) for k, v in prov_f[prov_f.in_head == 1].groupby("rule_id").repo.nunique().items()}
for flag in ["env_file_committed", "env_example", "gitignore_covers_env", "node_modules_committed",
             "virtualenv_committed", "pycache_committed"]:
    share(flag, int(s[flag].sum()), len(s))
s["openai_key"] = s.repo.isin(oa.repo).astype(int)
tab = pd.crosstab(s.gitignore_covers_env, s.openai_key)
chi = stats.chi2_contingency(tab)
F["key_vs_gitignore"] = {"pct_with_ignore": pct(s[s.gitignore_covers_env == 1].openai_key.sum(), (s.gitignore_covers_env == 1).sum()),
                         "pct_without_ignore": pct(s[s.gitignore_covers_env == 0].openai_key.sum(), (s.gitignore_covers_env == 0).sum()),
                         "p": fmt_p(chi[1]), "v": cramers_v(tab)}

# ------------------------------------------------------------------ RQ7 tracks
t = act_labels.dropna(subset=["track"]).merge(repos[["repo", "window_commits"]], on="repo") \
    .merge(s[["repo", "tests", "primary_language"]], on="repo", how="left") \
    .merge(r[["repo", "deployed_link", "language"]], on="repo", how="left")
rows = []
for code, *meta in CASES:
    sub = t[t.track == code]
    rows.append({"track": code, "sector_en": meta[1], "partner_en": meta[3], "bar_en": meta[5], "repos": len(sub),
                 "median_window_commits": int(sub.window_commits.median()) if len(sub) else 0,
                 "tests_pct": pct(sub.tests.sum(), len(sub)), "python_pct": pct((sub.primary_language == "Python").sum(), len(sub)),
                 "russian_readme_pct": pct((sub.language == "russian").sum(), len(sub))})
pd.DataFrame(rows).to_csv(TABLES / "tracks.csv", index=False)
F["tracks"] = {f"t{r_['track']}": {"n": r_["repos"], "commits": r_["median_window_commits"], "tests": r_["tests_pct"],
                                   "python": r_["python_pct"]} for r_ in rows}
kw = stats.kruskal(*[t[t.track == c].window_commits for c, *_ in CASES])
F["track_commits_kruskal"] = {"h": round(kw.statistic, 1), "p": fmt_p(kw.pvalue)}

# ------------------------------------------------------------------ validation facts
import subprocess  # noqa: E402

api_counts = pd.read_csv(DATA / "commit_counts.csv").set_index("name").commit_count
clone_counts = {n: int(subprocess.run(["git", f"--git-dir={DATA / 'clones' / (n + '.git')}", "rev-list", "--count", "HEAD"],
                                      capture_output=True, text=True).stdout.strip() or -1) for n in repos.repo}
agree = sum(clone_counts[n] == api_counts[n] for n in repos.repo)
old = pd.read_csv(DATA / "hackalem_repos_analysis.csv")
fixed16 = set(json.loads((DATA / "verification" / "template_counted.json").read_text()))
old.loc[old.repo.isin(fixed16), "participant_commits"] -= 1
cmp_ = repos.merge(old, on="repo")
meta = pd.read_csv(DATA / "repos.csv")
upd = pd.to_datetime(meta.updated_at, utc=True).dt.tz_convert(TZ)
wave = upd[(upd >= datetime(2026, 9, 23, 18, 0, tzinfo=TZ)) & (upd < datetime(2026, 9, 23, 19, 0, tzinfo=TZ))]
F["validation"] = {"clone_api_agree": int(agree), "template_found": int(repos.template_found.sum()),
                   "history_rewritten": int(N - repos.template_found.sum()),
                   "template_fixes": len(fixed16), "openai_marker": len(oa),
                   "same_team_commits": int((cmp_.team_commits == cmp_.participant_commits).sum()),
                   "same_window_commits": int((cmp_.window_commits == cmp_.commits_13_18_local).sum()),
                   "same_hours": int((cmp_.hours_active == cmp_.hours_with_commits_of_5).sum()),
                   "pr_only_repos": int((repos.pr_only_commits > 0).sum()),
                   "readmes_saved": 3644, "readmes_absent": 4, "readmes_empty": 1}
F["checks"] = {"readme_sample_n": len(pd.read_csv(DATA / "readme_lang_sample.csv")), "live_spot_check_n": 25,
               "searches_logged": len(pd.read_csv(PAPER / "literature" / "search_log.csv")),
               "references_screened": len(pd.read_csv(PAPER / "literature" / "screening.csv"))}
F["tracks_count"] = len(CASES)
F["template_audit_n"] = len(json.loads((DATA / "verification" / "template_check.json").read_text()))
F["archive"] = {"n": len(wave), "first": wave.min().strftime("%H:%M"), "last": wave.max().strftime("%H:%M"),
                "all_archived": int(pd.Series(meta.archived).astype(str).str.lower().eq("true").sum())}

OUT.write_text(to_json(F), encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)} ({len(json.dumps(F))} bytes)")
