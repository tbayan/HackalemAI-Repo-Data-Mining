# Reviewer 1: methods, validity, data-to-claim and citation audit

**Manuscript:** "Five Hours, 3,649 Repositories: An Empirical Study of an Agent-Assisted Mass Hackathon" (`latex/main.tex`, 329 lines, 12 pages)
**Reviewed version:** `main.tex` last modified 26 Sep 2026 21:12. `main.pdf` was rebuilt at 27 Sep 01:44 while I was reviewing, because `references.bib` was being updated by the separate DOI audit. The body text is the same in both builds. Only the reference list changed, and the citation audit below uses the current bibliography.
**Reviewer profile:** empirical SE / MSR (EMSE, JSS, IST, TSE, TOSEM, MSR, BDCC).
**How I checked:** I read every script in `src/` and `analysis/`. I recomputed the numbers independently from `data/*.csv` and, for spot checks, from the mirror clones (counts only). I opened nothing under `data/secrets_private/` and no `.env` file, and I name no team repository here. My recomputation scripts are in the session scratchpad (`.../scratchpad/r1/*.py`).

---

## 1. Summary of the submission

The paper studies HackAlem AI, a five-hour, in-person hackathon held in Astana on 23 September 2026. The organisers created one public GitHub repository per registration in the BAITC-Hacks organisation, 3,649 in total, and required teams to use OpenAI Codex. The author mirrored every repository and rebuilt all measures from git. Seven RQs are answered: the participation funnel and how it relates to repository creation date (RQ1), the hourly work rhythm with k-means archetypes (RQ2), technology stack and LLM SDKs (RQ3), agent traces such as context files, commit trailers, branch names and PR refs, plus an association between AGENTS.md and activity (RQ4), README and commit-message language (RQ5), credential strings found by Gitleaks (RQ6) and the distribution over tracks (RQ7). The headline results are that 29.0% of repositories were active in the event window, 28.8% of window commits fell in the last hour, and a "late-surge" cluster holds 30.6% of teams. Test files appear in 76.9% of repositories with commits, AGENTS.md in 28.7% and Claude signatures in far more commits than Codex signatures. READMEs are 87.0% Russian and 2.9% Kazakh, and strings shaped like OpenAI keys appear in 61 repositories. Every number is generated as a macro from `facts_paper.json`. The paper promises a derived dataset with hashed identifiers and a reproducible pipeline.

## 2. Recommendation

**(a) arXiv preprint: not ready. Major revision, though most items take small or moderate effort.** The engineering is careful, and I reproduced every number I could recompute from the derived CSVs. The problems are elsewhere:
- Two headline sentences are false: the conclusion's "most active teams worked through all five hours" (the true share is 44.5%), and the abstract's claim that the late-surge cluster "made most of their commits" in the last hour (only half of that cluster did).
- 446 repositories (12.2%) were archived *before* the event started. This undermines the RQ1 framing and the statement that the repositories were "archived after the deadline".
- One validation row is true by construction (OpenAI marker, 77 of 77). Figure 1(c) claims code that does not exist ("All reported numbers recomputed by separate code").
- The paper says the dataset is released, but `public_data_generated/` is empty.
- The README language rule classifies mostly-English READMEs as Kazakh.
- Responsible disclosure of the key strings is still marked `pending`. Anyone can reproduce the RQ6 finding by running Gitleaks over a public organisation, so disclosure (and, ideally, confirmed key revocation) must happen before posting.

These can all be fixed in one to two weeks. None of them requires new data collection.

**(b) Q1 SE journal (EMSE / JSS / IST / TOSEM): major revision. In its current form I would lean towards reject-and-resubmit at EMSE and major revision at JSS/IST.** The paper is a careful single-event descriptive census, but it has no comparison baseline and no validated measurement instruments (README language and track labels are pending or single-coder). Several of its "measures" (tests present, agent traces, credential "placeholder" filter) are proxies whose validity is not established. The inferential parts (logit, clustering, associations) are fragile or confounded. For a journal version I would expect all of the following:
1. The fixes listed below.
2. Validated instruments with reported agreement.
3. A baseline, for example commit-timing and artefact prevalence in comparable pre-agent hackathons from HackRep.
4. Treatment of the planned jury-outcome linkage as a pre-specified analysis.
5. Explicit threats-to-validity and open-science sections following the ACM SIGSOFT Empirical Standards for repository mining.

## 3. Strengths

1. **A rare population design.** Because the organiser created every repository, empty repositories are observable. This is a real advance over listing-based hackathon datasets (HackRep, Devpost), and the paper says so clearly (l. 89).
2. **Unusually careful data engineering.**
   - The mirror clones keep all branches and PR refs.
   - The template commit is identified by a rule that does not depend on the author account.
   - Default-branch counts agree with the GitHub API for 3,649 of 3,649 repositories (I re-ran this check and got the same result).
   - Author e-mails are counted only in memory, never written out.
3. **Every prose number is a generated macro.** I recomputed about 45 numbers from the derived CSVs and all matched `facts_paper.json` exactly (§7).
4. **The main counts are robust to the definition of the event window.** Moving the window by ±30–60 minutes changes the active count only from 1,057 to 1,061. Using author time instead of committer time gives 1,057 active repositories again, with 30,420 window commits instead of 30,418. The paper does not report this, but it is a strength.
5. **Honest measurement lessons.** The paper reports the organiser second-account template commits and the tool-dependent signature bias (l. 173, 288, 297). These are useful to the MSR community.
6. **Careful ethics posture on secrets.** Output is redacted, nothing is tested against a service, and only aggregates are reported.
7. **The writing is plain, short and mostly hedged.** Associations are called associations (l. 248, 306).

## 4. Major issues

### M1. 446 repositories were archived *before* the event, which changes RQ1 (l. 57, 125, 130, 164, 207–209, 282, 324; Fig. 2)
- **Problem:** The paper says the organisers "archived the repositories after the deadline" (l. 57, Table 1 l. 125) and reports only the 3,201 archive operations between 18:01 and 18:51 (l. 130). In `repos.csv`, however, 446 repositories have `updated_at` *before* 13:00 on 23 September, and none has `pushed_at` later than `updated_at`. Archiving updates `updated_at`, and all 3,649 are archived now, so these 446 were almost certainly read-only during the event.
- **Evidence (my recomputation):**
  - Archive dates of the 446: 126 on 15 Sep, 56 on 17 Sep, 242 on 22 Sep, 19 between July and 7 Sep, 2 on 19 Sep and 1 on the morning of 23 Sep.
  - 426 of them were created 15–21 Sep and 17 before 1 Sep.
  - None of the 446 became active.
  - They include 289 of the 2,395 "empty" repositories.
  - They include **157 of the 197 "outside-only" repositories** (l. 207), holding 670 pre-event commits that are counted in the 31,955 team commits (l. 222).
  - Excluding them changes RQ1 materially:
    - Active share among repositories open during the event: 33.0% (1,057/3,203).
    - Among open, non-batch repositories: **48.2%** (1,043/2,163).
    - The 15–21 Sep group rises from 34.3% to 45.3%.
    - The before-1-Sep group rises from 32.8% to 46.3%.
- **Fix:**
  - Report the archive-time distribution in full, not only the 18:01–18:51 wave.
  - Treat "archived before the event" as its own stage in the funnel (Fig. 2a).
  - Rerun the χ² test and logit on repositories that were open during the event.
  - Correct l. 57 and Table 1.
  - Ask the organisers what the pre-event archiving meant (for example duplicates, withdrawn teams or a selection step) and report the answer or its absence.
- **Effort:** S–M.

### M2. "Complete population of registrations" is asserted, not established (l. 48, 57, 71, 164, 209, 282, 324)
- **Problem:** The core claim is that the organisation "contains every registration" (l. 57) and that this is "the first repository-level study of a complete hackathon population" (l. 71). The paper's own findings contradict or weaken this:
  - (i) The 1,040-repository evening batch is read "as a batch created by the organisers, not as individual registrations" (l. 209). Yet l. 164 says each repository "corresponds to one registration", and l. 324 says "Of 3,649 registrations, 1,057 produced code".
  - (ii) Nothing reconciles 3,649 repositories with 6,586 applications and 2,500 seats (l. 57). Were applications per person and repositories per team? Did every applicant get a repository?
  - (iii) Repository creation time is used as a proxy for registration time without saying so. The analysis plan lists this caveat, but the paper omits it.
  - (iv) See M1.
- **Evidence:**
  - Non-batch repositories: 2,609.
  - The sum of distinct author e-mails in active repositories is 2,795 (upper bound; includes agent/bot addresses and people using more than one e-mail). The Astana Times reports "more than 2,500 participants from 21 countries", so a triangulation is possible, but the paper does not attempt it.
  - Duplicate team names are weak evidence of re-registration: the median gap between same-name repositories is 98 h, only 4.3% are within one hour, and 24 of the 224 names have ≤3 characters.
- **Fix:**
  - Define the population as *organiser-created repositories*.
  - State that the mapping repository → registration → team is an assumption.
  - Add a reconciliation paragraph (applications, seats, attendees, repositories, active repositories, distinct non-bot author e-mails).
  - Replace "registrations" with "repositories" in l. 324 and the abstract.
  - Add creation date as a registration proxy to Threats (l. 306).
  - Soften "complete population" in l. 71.
- **Effort:** M.

### M3. Headline sentences that the data contradict (l. 48, 224, 324)

| Where | Paper says | Data |
|---|---|---|
| Conclusion l. 324 | "Most active teams worked through all five hours" | 470/1,057 = **44.5%** committed in all five hours (79.3% in ≥4). **False.** |
| Abstract l. 48 | "a cluster of 30.6% of teams made most of their commits then" | Only **163 of the 323** cluster members (50.5%) made >50% of window commits in 17:00–18:00. That is 15.4% of active teams (`teams_majority_last_hour`, computed but not reported). **False at team level.** |
| l. 224 | late-surge group "made 58.3% of its commits in the last hour" | 58.3% is the centroid, i.e. the mean of per-team shares. The pooled share of the cluster's commits is **52.6%**. Misdescribed. |
| l. 324 | "a third of them concentrated their work at the end" | Overstated for the same reason (15.4% by the direct measure). |

- **Fix:**
  - Use "at least four of five hours (79.3%)".
  - Report the per-team deadline share directly: median 30.8%, and 15.4% of teams with a majority of commits in the last hour.
  - Describe the cluster as having "on average 58% of each team's commits in the last hour".
- **Effort:** S.

### M4. The rhythm clustering is weakly supported and replaces the pre-planned descriptive measure (l. 197, 224, 229, 285; Fig. 3b)
- **Problem:** A silhouette of 0.304 is in the "weak, possibly artificial structure" range. My checks:
  - A null model with the same team sizes and multinomial draws from the pooled hourly profile gives a silhouette of 0.18 at k = 2. There is some structure beyond noise, but not much.
  - The k = 2 solution is almost exactly a threshold on the last-hour share: the cluster's 10th percentile is 0.43, and 324 teams have a share above 0.4 against 323 in the cluster. So the "archetypes" are a cut through a continuum.
  - A Gaussian mixture on the same profiles prefers k = 3 by BIC (−10,160 vs −9,947 for k = 2).
  - The late-surge cluster is made up of smaller teams (median 12 window commits vs 23). 38 of its 323 teams have ≤3 commits, and such profiles are degenerate.
  - The assignment itself is stable (bootstrap ARI median 0.94, 5th percentile 0.81), which the paper could report.
  - The analysis plan said to report the *distribution* of each team's deadline share (`analysis_plan.md`, RQ2). That distribution was computed (median 30.8%; 15.4% majority) and left out of the paper, while the cluster framing went into the abstract. This is selective reporting.
- **Fix:**
  - Lead with the per-team deadline-share distribution: histogram or ECDF, median and share above 50%.
  - Present clustering as exploratory.
  - Restrict it to teams with ≥5 or ≥10 window commits.
  - Use a log-ratio (CLR) transform for compositional shares or a mixture model.
  - Report silhouette against a null reference and bootstrap stability.
  - Cite Rousseeuw (1987) for interpreting the silhouette.
- **Effort:** S–M.

### M5. RQ1 inference is fragile and partly misspecified; inference on a census is not motivated (l. 197, 209; Fig. 2b)
- **χ²(4) = 609.2:**
  - The five groups in the test (before 1 Sep; 1–14; 15–21; all of 22 Sep; **23 Sep, n = 2**) differ from the five groups in Fig. 2b, which splits 22 Sep into batch and other and drops 23 Sep.
  - The 23-Sep row has an expected count of 0.58, and two cells are below 5, which breaks Cochran's rule.
  - The statistic is dominated by the batch.
  - Without the batch (three groups up to 21 Sep), χ²(2) = 84.6, V = 0.181. This is the number the paper should report.
- **Logistic regression:**
  - The plan specified log(days before the event). The code uses linear weeks clipped at 0, which is an undisclosed deviation.
  - Activity is **non-monotonic** in creation date: 32.8% before 1 Sep, 53.7% for 1–14, 34.3% for 15–21, 43.2% for 22 Sep outside the batch.
  - The no-batch estimate is driven by 58 early repositories created in June to August (up to 12.5 weeks before; 17 of them archived before the event, and 16 of them the organiser test repositories of l. 173).
  - My sensitivity runs of the paper's own model, OR per week (95% CI):

    | Sample | OR per week (95% CI) | n |
    |---|---|---|
    | Paper, without batch | 1.170 (1.08–1.27) | 2,570 |
    | Also excluding repos created before 1 Sep | **1.872** (1.66–2.12) | 2,512 |
    | Excluding pre-archived repos | 1.264 (1.13–1.42) | 2,124 |
    | Excluding both | 1.368 (1.20–1.56) | 2,083 |

  - The main estimate in the text (1.878, "with the batch included") mixes in a group the author says is not registrations.
- **Census inference:** Wilson CIs, p-values and "Holm correction within each question" are applied to a complete population without saying what the inferential target is (a superpopulation or a data-generating process). See Baltes & Ralph (2022) on sampling. Also:
  - Holm was applied only to the three AGENTS.md tests.
  - The RQ1 χ² and logits, the RQ3 χ², the RQ6 χ² and the RQ7 Kruskal–Wallis were not corrected.
  - Kruskal–Wallis is not listed in the Statistics paragraph (l. 197) and has no effect size (ε² = 0.019 by my computation).
- **Fix:**
  - Model creation date categorically (or with a spline) on open, non-test, non-batch repositories.
  - Report the batch as a separate stratum.
  - Drop the "with the batch" odds ratio as the headline.
  - State the superpopulation interpretation or present the tests as descriptive.
  - List every test with its correction family.
- **Effort:** S.

### M6. The README language rule labels mostly-English READMEs as Kazakh, is not yet validated, and denominators are mixed (l. 48, 167, 191, 252, 291, 306; Fig. 5)
- **Problem:** The rule tests "Kazakh" first, as ≥3% of *Cyrillic* letters, without looking at Latin letters (`readme_features.py:56`). A mostly-English README with a single Kazakh sentence is therefore labelled Kazakh.
- **Evidence:**
  - Of the 34 "Kazakh" READMEs, **11 have ≥50% Latin letters**. The upper quartile of their Latin share is 0.97.
  - The abstract's "2.9% were in Kazakh" is therefore inflated; the true figure is closer to 23/1,185 ≈ 1.9% for predominantly Cyrillic-Kazakh READMEs.
  - The rule misses the opposite case too: Kazakh typed with Russian look-alike letters (қ → к and so on).
  - The validation sample has **0 of 90** hand labels filled.
  - The sample is stratified 35/35/15/5 by the automatic label, so accuracy must be reweighted.
  - Labellers see only a 400-character excerpt, taken from `HEAD:README.md` regardless of the file's actual name.
  - `readme_features.py:6` already says the rule was "validated by hand".
  - **Denominators:** "Kazakh-specific letters appear somewhere in 12.0% of READMEs", 92.2% install instructions, 17.8% images and 6.8% deployed link are all computed over **1,254 repositories** (including 63 template-only READMEs and 6 with no README or too little text). The same paragraph says "of the 1,185 READMEs". Over 1,185 the figures are 12.6%, 97.5%, 18.8% and 7.2%. The word-count median, by contrast, uses 1,185.
  - The INSTALL regex matches any `\brun\b`, `setup` or `install`, so "run or installation instructions" is very broad.
- **Fix:**
  - Apply "Kazakh" only when Cyrillic letters are the majority of all letters; otherwise use "mixed / English with Kazakh".
  - Complete two-rater hand labelling on full READMEs, not excerpts, and report per-class precision and recall with κ.
  - Use one denominator throughout the paragraph and state it.
  - Tighten or rename the "instructions" feature.
- **Effort:** S–M.

### M7. Some validation claims are circular or unsupported (l. 81, 173, 183–191, 200; Fig. 1c)
- **Problem and evidence:**
  - **Table 3, "OpenAI-pattern findings with the structural marker: 77 of 77".** Gitleaks 8.30.1's `openai-api-key` regex *requires* the `T3BlbkFJ` marker (confirmed in the bundled binary). `run_analysis.py:405` simply sets `openai_marker = len(oa)`. The row is true by construction and should not be presented as a check.
  - **Fig. 1(c), "All reported numbers recomputed by separate code".** There is no such code. `checks/check_numbers.py` only lints for literal numbers typed into the prose. My own recomputation reproduced every CSV-derived number, but that is my check, not the paper's.
  - **"Earlier per-repository table".** It is the author's own earlier output, its generating script is lost (`validation_m1.md`), and the comparison adjusts it by −1 for the 16 fixed repositories before comparing (without the adjustment, 3,625 of 3,649 agree). It is a consistency check, not an independent source, yet Fig. 1(c) and l. 81 call these "independent sources".
  - l. 173: PR-only commits "we report separately". They are not reported anywhere in the paper (117 repositories in `facts_paper.json`).
  - The "live check of 25 sampled repositories" is hard-coded (`run_analysis.py:411`) with no stored artefact.
  - How the 402 repositories were chosen for the template audit is not explained.
  - l. 200: "the checks ... were designed to catch errors in AI-produced analysis, and they did". The checks were themselves produced with the same AI agent, and only one error class was caught.
- **Fix:**
  - Delete or reword the marker row, for example "all OpenAI findings match the vendor key format by construction of the rule".
  - Remove "recomputed by separate code" or actually add an independent re-implementation of the core counts (I can confirm that it is feasible).
  - Call the earlier table a consistency check.
  - Store the 25-repository live check and the 402-repository selection rule.
  - Report the PR-only commits.
- **Effort:** S.

### M8. The credential analysis has an unvalidated filter, a confounded association and an incomplete disclosure (l. 167, 263–265, 294, 317)
- **Placeholder filter** (`secrets_precision.py`):
  - The method (regex for x's/"your"/"example"/"…", or Shannon entropy < 3.5) is not described in the paper and was never validated against hand labels.
  - For rules without a candidate pattern (curl-auth-header, curl-auth-user, jwt), the whole *line* is scored. Almost any line has entropy ≥ 3.5, and any line containing "example" (for instance `api.example.com`) becomes a placeholder.
  - A class "unreadable" exists but is not reported. "127 findings, 10 placeholders, the remaining ... in 73 repositories" is correct only if that class is empty. I could not verify this without opening private files.
- **Recall:** The Gitleaks OpenAI rule fixes key lengths and the marker. Key formats outside it, and other providers' keys the organisers may have issued, are missed. There is no recall statement.
- **`in_head`** matches on (rule, file), not on the string. A key replaced by a different key in the same file still counts as "still present".
- **Timing basis:** "all were committed during the event window" uses Gitleaks' `Date` field, while the window elsewhere is defined on committer time. State which timestamp Gitleaks reports.
- **l. 167:** "kept only the rule, file and time of each finding" is inaccurate. `scan_secrets.py` also stores commit SHA, line number and entropy, which together locate every secret in public history. This matters for the privacy statement (l. 317). It also covers only the 1,254 clones with team commits, not "every clone".
- **.gitignore–key association (l. 265) is confounded:**
  - Repositories using the OpenAI SDK have a `.gitignore` covering `.env` in **91.1%** of cases, against **46.0%** for other repositories.
  - Repositories whose `.gitignore` covers `.env` have a `.env.example` in **83.3%** of cases, against 13.6%.
  - A repository without an LLM key cannot leak one. "This matches the association we observe" reads causally.
  - The plan labelled this test *exploratory*; the paper does not.
- **Disclosure:** l. 317 is `pending`. By my count 30 repositories still contain such strings at HEAD and 61 in history, all in an organisation anyone can list.
- **Fix:**
  - Describe the classifier and hand-check all 127 provider findings privately, reporting confirmed / placeholder / unclear counts only.
  - Report the class breakdown.
  - Stratify the .gitignore association by OpenAI-SDK use and `.env.example` presence (Mantel–Haenszel or logit), privately, reporting aggregates.
  - State the recall limits.
  - **Complete disclosure to the organisers, and ideally key revocation, before posting.**
- **Effort:** M.

### M9. Agent-trace constructs and their interpretation (l. 167, 246, 248, 285, 288; Fig. 4)
- **PR refs are counted as an agent trace** ((iv) at l. 167; "Agent footprint" colour in Fig. 4). Any team workflow creates PR refs. They are associated with Codex branches (143 of 200 Codex-branch repositories have PR refs), but 251 repositories have PR refs without Codex branches.
- **"Agent signature" includes non-agent identities.**
  - `extract_commits.py` flags any `[bot]` account and any author or committer name containing tokens such as `devin`, `jules`, `cursor` or `gemini`. Some of these are common first names.
  - The 26 "bot" commits include **16 feature commits in 3 active repositories authored under the organiser's GitHub-app identity**, which could be Codex cloud pushing via an organisation app, or something else. There are also 7 commits by another bot.
  - The 7 "devin" commits need a manual check.
  - The kind of a "Generated with" commit is taken from the *first* agent token in the whole body (l. 103). A message that mentions "openai" before "Generated with Claude" is labelled Codex.
- **Definitional drift:**
  - "CLAUDE.md in 12.2% (153)" includes 11 repositories that have only a `.claude/` directory (142 have the file).
  - "AGENTS.md (by that exact name)" is matched case-insensitively at any depth: 318 at the root with exact case, 3 at the root in another case, 39 nested only.
  - "Agent-signed commits 20.7% (260)" in Fig. 4 is a share of *repositories*, not commits.
- **Interpretation (l. 246, 288):** "We therefore treat commit signatures as evidence of each tool's default disclosure behaviour, not as a measure of use" does not follow. A missing signature is not evidence of non-use, but a present Claude Code signature is evidence of use. Claude-signed commits occur in **199 repositories** and Codex-signed in 48. That is a lower bound on non-Codex tool use under a Codex-only rule, and the paper should say so, carefully and in aggregate. It is also not mentioned that `AGENTS.md` is the file Codex's own `/init` creates, so it is itself a Codex trace.
- **AGENTS.md association (l. 248):**
  - The alternative explanation offered ("experience or preparation") omits the most direct one: agent-driven workflows produce both AGENTS.md and test files.
  - The association survives adjustment for activity (logit of tests on AGENTS.md plus log window commits: OR 3.5, 95% CI 2.0–6.2), which is worth reporting, but it remains an association.
  - Features are measured at the final HEAD. That state includes pre-event code (173 active repositories committed before 13:00; 33 changed more than 1,000 lines before the start) and post-deadline commits (74 repositories).
- **Fix:**
  - Separate "agent traces" (context files, trailers, agent branches) from "workflow traces" (PR refs).
  - Build a per-tool trace table covering Codex and Claude Code with overlaps (for example: CLAUDE.md with Claude signature 66; file only 87; signature only 133).
  - Manually review all non-trailer account hits.
  - Measure features at the last window commit (the state at 18:00) as a sensitivity check.
  - Discuss pre-event code, citing Imam et al. (MSR 2021).
- **Effort:** M.

### M10. "We wrote the analysis plan before running any test" is misleading, deviations are undisclosed, and nothing is labelled exploratory (l. 197)
- **Problem:**
  - `analysis_plan.md` says itself that descriptive numbers were inspected first. It was saved at 19:44 on 24 Sep, *after* all feature files (19:36–19:43), and after a public bilingual report built on the same data (git commit 02dee68).
  - It is untracked in git, so it has no verifiable timestamp.
  - It promises "Anything added later is marked *exploratory* in the paper". The word does not appear anywhere in `main.tex`.
- **Undisclosed deviations:**
  - Logit on log-days → linear weeks.
  - RQ3 prevalence "among active repositories" → among the 1,254.
  - Timeline "main branches" → all branches.
  - Post-deadline window "18:00 to archive time" → 18:00–19:00.
  - Word count "median, IQR" → median with bootstrap CI.
  - RQ7 "descriptive only" → Kruskal–Wallis added.
  - Batch analysis and no-batch logit added.
  - Deadline-share distribution planned, then omitted.
  - Commit size and the .gitignore test were planned as *exploratory*, but the paper does not label them so.
- **Fix:**
  - Reword l. 197 to: "We fixed the list of inferential tests after descriptive exploration and before running them."
  - Publish the plan in the repository.
  - Add a deviations table (supplement).
  - Label exploratory analyses in the text.
- **Effort:** S.

### M11. The data and reproducibility claims are not met (l. 48, 75, 81, 197, 312, 319)
- **Problem:**
  - `public_data_generated/` is empty, and `arxiv_paper_all/` (analysis, figures, plan) is untracked, so it is not in the public repository.
  - `data/` is git-ignored.
  - `run_analysis.py` cannot be rerun by a third party:
    - It reads `data/secrets_private/*` and the 3,649 clones (for validation).
    - It reads `hackalem_repos_analysis.csv`, whose generating script is lost and which supplies **all track labels**.
    - It hard-codes constants such as `readmes_saved: 3644` and `live_spot_check_n: 25`.
  - The track keyword classifier lives in `data/verification/kwclassify.py` with hard-coded absolute and scratchpad paths.
  - `requirements.txt` is unpinned and omits scipy.
  - Git and Gitleaks versions are not recorded in a lock file.
  - **"Hashed identifiers" give no protection.** The organisation's 3,649 names are public, so an unsalted hash is reversible by hashing the list.
- **Seriousness:** For arXiv, the sentence "we release..." (l. 48, 75, 319) is currently false and must either be made true or changed to "will be released". For EMSE/JSS, open data is expected, and the missing track-label provenance makes RQ7 and Table 2 non-reproducible.
- **What the release must contain:**
  1. A per-repository table with a stable pseudonymous ID: created and archived timestamps, archived-before-event flag, batch flag, commit and window counts (committer and author time), hours, branches, PR refs, PR-only commits, stack, agent and hygiene flags, README features and language, and track label with a provenance code (original / corrected / keyword / unclear).
  2. A commit-level table: pseudonymous repo ID, both timestamps, merge flag, lines, conventional flag, subject script and agent-signature flags. No messages and no e-mails.
  3. RQ6 as aggregates only. **Never a per-repository secret flag**, even hashed.
  4. The full pipeline including `run_analysis.py`, split into a *public* stage (runs on the released tables and reproduces every macro except RQ6) and a *private* stage.
  5. The analysis plan with its deviations, the README hand labels, the track classifier and its agreement, and the template-audit data.
  6. Pinned environment (`pip freeze` or lockfile), Git and Gitleaks versions with checksum.
  7. A Zenodo DOI, plus a Software Heritage snapshot or a list of (repo, HEAD SHA) pairs so that others can re-collect the data if repositories disappear.
  8. For privacy, a statement that pseudonymisation is not anonymisation, because the source repositories are public.
- **Effort:** M.

### M12. Track labels: provenance, validity and the track table (l. 134, 169–170, 189, 276; Table 2)
- **Problem:**
  - `case_guess` comes from an undocumented table.
  - The keyword check was run, but its results are not reported. My recomputation for active repositories:
    - Agreement is 933 of 946 decisive cases (98.6%, κ = 0.985).
    - **19 labelled active repositories have only the template README or none**, so their labels cannot have come from README text and were not checked.
    - 19 more are keyword ties.
    - **34 of the 73 "unclear" repositories have a decisive keyword label.**
  - One person read the disagreements, and no inter-rater agreement is reported.
  - The track number → partner mapping is inferred. The claim ledger (#7) says "partner names confirmed in team READMEs ... Trade = 10 by elimination".
  - Table 2 task descriptions are "our summaries of the teams' READMEs", not official briefs.
  - `hackalem.ai` does not list tracks. The press gives ten sector directions but no partners.
- **Fix:**
  - Report the agreement statistics and the unchecked subsets.
  - Double-code a sample.
  - Say in the caption that partners and tasks are inferred.
  - Source them from organiser material if possible.
  - Consider assigning the 34 decisive "unclear" repositories.
- **Effort:** M.

## 5. Minor issues

1. **l. 32 and elsewhere:** "Agent-Assisted Mass Hackathon". "Mass" is informal; consider "Large-Scale".
2. **l. 48:** "Only 1,057 repositories" is evaluative. Also, "README files were mostly in Russian (87.0%)" hides the denominator (1,185 READMEs with written content), which should be stated.
3. **l. 55:** "Controlled experiments and field studies report faster task completion" is supported only by Peng et al. (see citation table). "Observational work" should not cover the Liang survey.
4. **l. 55:** "qualitative and small". Chen et al. is mixed-methods with standardised project evaluations.
5. **l. 57:** The five-hour window is attributed to the organiser site, which does not state it. Cite Ulys, Astana Times or Kazinform instead.
6. **l. 57:** "every team worked under the same deadline and tooling rule". True of the rule, but see M9 on compliance.
7. **l. 59 and Fig. 1 caption:** "checked the result against the GitHub API". Only default-branch commit counts were checked this way.
8. **Fig. 1(e) vs l. 164:** Fig. 1 says "RQ3–RQ7: 1,254", while l. 164 says RQ7 uses the 1,057 active repositories (actually the 984 matched). RQ3's language-by-track test also uses the 984, and RQ4's association uses the 1,057.
9. **l. 117 (Table 1):** The coding-window row cites [19, 38], but neither source gives 13:00–18:00. Split the row into "five hours [press]" and "13:00–18:00, inferred by this study".
10. **l. 121:** Astana Times also gives "more than 2,500 participants" and "129 universities". Worth adding for the M2 reconciliation.
11. **l. 124:** The site also lists a Demo Day on 29 Sep. Relevant if jury linkage is planned.
12. **l. 130 vs l. 164:** "added a one-line README" vs "changes one file by two added lines". The template README has a heading line plus one line of text; make the two consistent.
13. **l. 164:** The template rule in the code also requires 0 deletions and an exact subject match. State this.
14. **l. 164 and l. 197:** Say that the window is defined on the **committer** timestamp. Report the author-time sensitivity (1,057 active, 30,420 commits) and the window-shift sensitivity (1,057–1,061).
15. **l. 167:** LLM detection also uses URL patterns (`api.openai.com`, `localhost:11434`), not only imports. "OpenAI SDK" (l. 235, Fig. 4) therefore means "OpenAI SDK or API endpoint".
16. **l. 167:** The README rule also has a "too short" class (fewer than 20 letters; 1 README) and a "no README" class (5). Mention both, since 1,185 + 63 + 6 = 1,254.
17. **l. 170:** "checked against README text with keyword rules". The keyword code is not in the released pipeline (see M12).
18. **l. 191, l. 306:** Remove `\pending{}` markers before posting, or remove the row and the claim.
19. **l. 200:** "author to name any other AI tools" is pending. The Acknowledgments requirement in the style guide (MDPI) is not met.
20. **l. 207:** "almost all before the event". Confirmed (194 of 197), but 157 of them were archived before the event (M1).
21. **l. 209:** Report the 22-Sep non-batch group (n = 37, 43.2%) and the before-1-Sep group (n = 58, 32.8%) in the text; they show the relationship is non-monotonic.
22. **l. 209:** Odds ratios are given to three decimals (1.878), which is spurious precision; use two.
23. **l. 211:** The repeated-name inference is weak (M2). Report the creation-time gaps.
24. **l. 222:** "made its first commit 61 minutes after the start" means the first *window* commit; 173 active repositories committed earlier. "Teams made 31,955 team commits" also includes the 1,254 − 1,057 non-active repositories and pre-event commits.
25. **l. 222 vs l. 252:** Median with bootstrap CI (first/last commit, words) sits next to median with IQR (commits per team, lines) and bare medians (headings, AGENTS.md comparisons, Table 2). Choose one convention: median [IQR] for description, plus a CI only where inference is intended.
26. **l. 222, 229:** Fig. 3a counts commits on all branches over 11:00–19:00, while the text's peak and 28.8% use window commits only. Fine, but say so in the caption.
27. **l. 235:** "The most common frameworks were React, FastAPI, Vite and Next.js". Tailwind (18.5%) is more common than Next.js (14.3%), and Uvicorn, pytest and Pydantic are also above Next.js in `frameworks.csv`. Say "web frameworks" and define the category.
28. **l. 235:** The RQ3 paragraph mixes the 1,254 denominator with Table 2 percentages among matched active repositories ("95.7% of Telecom repositories").
29. **l. 235:** The 12×4 χ² has 8 of 48 cells with expected counts below 5 (minimum 1.71). This is acceptable by Cochran's rule but should be reported, or a Monte-Carlo p-value given.
30. **l. 240, Fig. 4:** "Agent-signed commits 20.7% (260)" should read "Repositories with agent-signed commits". The figure uses one-decimal percentages, while Fig. 3b uses whole numbers (69%, 31%); the style guide asks for whole numbers in figures.
31. **l. 246:** "and 31.4% have pull-request references" sits in the Codex sentence and implies Codex. Split it.
32. **l. 248:** Lines changed are added + deleted from `numstat` and include lockfiles, datasets and generated files; binaries count as 0. Exclude lockfiles and data files, or say so.
33. **l. 248:** "36.6% of commit subjects follow the conventional-commit format" counts 5,184 merge commits in the denominator; among non-merge commits the figure is 43.0%.
34. **l. 252:** "Commit messages are mostly in Latin script (89.4%)" is computed on the full body, including agent trailers and "Generated with" lines, and including merge commits. On non-merge *subjects* the figure is 87.5% Latin, 12.1% Cyrillic. Also, "Kazakh-specific letters occur in 23 of 31,955 commits" is actually "Cyrillic-majority messages containing a Kazakh letter". Commit *subjects* containing any Kazakh letter number 18 of 26,754 non-merge commits.
35. **l. 252:** Headings are counted on raw text, including `#` comment lines inside code blocks (288 READMEs are affected). The median is unchanged at 15, but fix the method.
36. **l. 252:** "READMEs are long for a five-hour event" has no baseline. Either give one or drop "for a five-hour event".
37. **l. 257, Fig. 5:** The commit bar omits the 0.3% "none" category, so it does not reach 100%. The legend "Russian / Cyrillic" merges a language with a script.
38. **l. 263:** "93.5% of them in data files" is defined by the extensions .json, .jsonl, .txt and .csv. Say so. "such as the datasets provided with the tasks" is an inference.
39. **l. 263:** "occurrences" means Gitleaks findings (commit × file × line); the same key can be counted several times. Say so.
40. **l. 265:** Committed `.env` 2.7% (34) vs `.env` occurrences of OpenAI keys (27). Check that the files differ ("other .env variants" and templates).
41. **l. 276:** Give an effect size for Kruskal–Wallis (ε² ≈ 0.02) and list the test in l. 197.
42. **l. 285:** "Tests, Docker files and long READMEs were common". Docker 28.6% and Compose 26.3% are not "common" in the usual sense.
43. **l. 291:** Mention that `.cursor/`, `.claude/` and `.github/prompts/` folders may include settings rather than context.
44. **l. 297:** Add "repositories archived before the event" (M1) as a fourth mining lesson.
45. **l. 303–312:** Threats are thin for a journal. Missing items:
    - Client-set commit clocks and rebase effects.
    - Pre-event archiving.
    - Creation date as a registration proxy.
    - Final-state features including pre-event and post-deadline code.
    - The README rule's Latin blind spot and Kazakh typed in Russian letters.
    - Regex-based LLM detection (commented-out imports, documentation).
    - Primary language by bytes (data and generated files).
    - Placeholder-classifier validity and Gitleaks recall.
    - Census vs inference.
    - Single-coder labels.
    - AI-agent-produced analysis code without an independent re-implementation.

    Organise them following Wohlin et al. or the Empirical Standards.
46. **l. 317:** No statement on ethics review or exemption. For a journal, say whether one was sought, or argue why public-repository mining is exempt at your institution. Also consider timing: publishing before the 1 October awards an aggregate showing Claude signatures in about 200 repositories under a Codex-only rule could affect judging. Discuss this with the organisers when you disclose the keys.
47. **l. 319:** The repository URL points to a repository that does not yet contain the paper's pipeline (M11).
48. **Terminology:** The paper uses registration / repository / team / team repository interchangeably (l. 164, 207, 222, 224, 324), as well as "event-time commits" (l. 48, 222) vs "event-window commits" (l. 134, 248, 276), "agent context files" vs "agent rule files" vs "agent configuration files" (style guide), "credential hygiene" (RQ6) vs "security hygiene" (Fig. 1) vs "secret leakage" (keywords), and "traces" vs "footprint". Adopt the style-guide glossary (*team repository*, *active repository*, *event window*) and apply it throughout.
49. **Reporting order:** count(%) at l. 207 but %(count) at l. 246, and CIs sometimes unlabelled after the first ("(1.082–1.265, n = 2,570)", "(8–10)"). Unify.
50. **`references.bib`:** `prana2019readme` gives year 2018 (online first), but EMSE 24(3) is the 2019 issue. The key and the rendered year disagree.

## 6. Data-to-claim audit (macro → `facts_paper.json` → `run_analysis.py` → CSV → my recomputation)

"PASS" means the number reproduces exactly from `data/*.csv` or the clones. "FAIL-desc" means the number reproduces but the sentence describes a different statistic or denominator. "FAIL" means the claim is contradicted. "n/v" means not verifiable under the privacy rule.

| # | Claim (line) | Paper | Mine | Result | Note |
|---|---|---|---|---|---|
| 1 | Total repositories (l. 32, 207) | 3,649 | 3,649 | PASS | repo_table.csv |
| 2 | With team commits (l. 207) | 1,254 (34.4%) | 1,254 (34.4%) | PASS | |
| 3 | Active (l. 48, 207) | 1,057 (29.0%) | 1,057 (29.0%) | PASS | committer time. Author time also gives 1,057 |
| 4 | Empty (l. 48, 207) | 2,395 (65.6%) | 2,395 (65.6%) | PASS | 289 of them archived before the event (M1) |
| 5 | Outside-only, "almost all before the event" (l. 207) | 197 | 197 (194 before, 3 after) | PASS | 157 archived before the event |
| 6 | Matched to a track (l. 207) | 984 (93.1%) | 984 | PASS | Table 2 sums to 984 |
| 7 | "archived the repositories after the deadline" (l. 57, 125) | all | 3,203 after 18:00; **446 before 13:00** | **FAIL** | M1 |
| 8 | Archive wave (l. 130) | 3,201, 18:01–18:51 | 3,201, 18:01:57–18:51:22 | PASS | omits the 446 |
| 9 | χ²(4) creation date × active (l. 209) | 609.2, V = 0.409 | 609.2, V = 0.409 | PASS (number) | groups differ from Fig. 2b; one n = 2 cell with expected 0.58; without batch χ²(2) = 84.6, V = 0.181 |
| 10 | 1–14 Sep vs 15–21 Sep (l. 209) | 53.7% / 34.3% | 53.7% / 34.3% | PASS | 45.3% for 15–21 if pre-archived excluded |
| 11 | Batch (l. 209) | 1,040; 15/min; 14 active (1.3%) | same | PASS | |
| 12 | Organic max per minute (l. 209) | 8 | 8 | PASS | 72 organic minutes with ≥3 repositories |
| 13 | OR/week with batch (l. 209) | 1.878 (1.714–2.058) | 1.878 | PASS (number) | misspecified (M5) |
| 14 | OR/week without batch (l. 209) | 1.170 (1.082–1.265), n = 2,570 | 1.170 (1.082–1.265) | PASS (number), **fragile** | 1.872 excluding pre-Sep; 1.264 excluding pre-archived |
| 15 | Duplicate names (l. 211) | 225; 224 cover 480; 146 one active | 225; 224; 480; 146 | PASS | "team" covers 104 repositories; 75 groups with 0 active |
| 16 | Team commits and window commits (l. 222) | 31,955 / 30,418 | 31,955 / 30,418 | PASS | includes 670 commits in pre-archived repositories |
| 17 | Last-hour share (l. 48, 222) | 28.8% | 28.8% (8,755/30,418) | PASS | |
| 18 | Peak 10 minutes (l. 222) | 17:40–17:50, 1,649 | bin 28 (17:40), 1,649 | PASS | |
| 19 | First commit median (l. 222) | 61 min (59–64) | 60.8 min | PASS / FAIL-desc | first *window* commit |
| 20 | Last commit before deadline (l. 222) | 9 min (8–10) | 9.0 | PASS | |
| 21 | Window commits per team (l. 222) | 19 (IQR 10–35) | 19 (10–35) | PASS | |
| 22 | ≥4 hours / 5 hours / last hour (l. 224) | 79.3 / 44.5 / 96.3% | 79.3 / 44.5 / 96.3% | PASS | |
| 23 | "Most active teams worked through all five hours" (l. 324) | "most" | 44.5% | **FAIL** | M3 |
| 24 | Silhouette k = 2 (l. 224) | 0.304 | 0.304 | PASS | null reference 0.18; GMM prefers k = 3 |
| 25 | Cluster sizes (l. 224) | 734 (69.4%) / 323 (30.6%) | same | PASS | |
| 26 | Late-surge "made 58.3% of its commits in the last hour" (l. 224) | 58.3% | centroid 58.3%; pooled 52.6% | **FAIL-desc** | mean of shares |
| 27 | "a cluster of 30.6% of teams made most of their commits then" (l. 48) | 30.6% | 163 of 323 in cluster; 15.4% of active teams | **FAIL** | M3 |
| 28 | Post-deadline commits (l. 224) | 235 from 74 repositories | 235 / 74 | PASS | |
| 29 | Primary language (l. 235) | Py 58.2, TS 19.1, JS 12.2% | 730 / 239 / 153 → same | PASS | "none" 71 (5.7%) not mentioned |
| 30 | Frameworks (l. 235) | React 40.2, FastAPI 37.2, Vite 28.2, Next.js 14.3% | same | PASS / FAIL-desc | Tailwind 18.5% omitted |
| 31 | LLM SDK / OpenAI (l. 235) | 63.7 / 60.0% | 799 / 752 → same | PASS | "SDK" includes endpoint regex |
| 32 | Anthropic / Ollama / Google (l. 235) | 2.6 / 2.3 / 2.2% | 33 / 29 / 28 → same | PASS | |
| 33 | Tests (l. 48, 235) | 76.9% (74.5–79.1), 964 | 964 | PASS | 931 have test *code* files; 2 match only non-code files |
| 34 | Dockerfile / Compose / CI / deploy (l. 235) | 28.6 / 26.3 / 12.4 / 5.3% | same | PASS | |
| 35 | Language × track χ²(33) (l. 235) | 201.1, V = 0.261 | 201.1 | PASS | n = 984 active, not 1,254; 8/48 cells with expected < 5 |
| 36 | Any agent file / AGENTS.md / CLAUDE.md (l. 246) | 31.0 / 28.7 (360) / 12.2 (153) | 389 / 360 / 153 | PASS / FAIL-desc | CLAUDE.md count includes 11 `.claude/`-only; AGENTS.md includes 39 nested-only |
| 37 | Other agent rule files (l. 246) | 36 | 36 | PASS | |
| 38 | Agent-signed commits (l. 246) | 3,979 (12.5%) in 260 | 3,979; 260 | PASS | 284 account-only hits; 26 "bot", 16 of them organiser-app identity |
| 39 | Claude / Codex signatures (l. 246) | 3,502 / 333 | 3,502 / 333 | PASS | 199 vs 48 repositories |
| 40 | Codex branches / PR refs (l. 246) | 200 / 31.4% | 200 / 394 (31.4%) | PASS | |
| 41 | AGENTS.md association (l. 248) | 28 vs 16, δ = 0.356; 5 vs 4, δ = 0.260; 95.7 vs 82.7%, V = 0.183; all p < 0.001 | identical; Holm p = 9.5e-21, 2.5e-13, 4.8e-9 | PASS | adjusted OR (tests) 3.5 [2.0–6.2] |
| 42 | Lines per commit (l. 248) | 134 (21–561); 126 / 135 | same | PASS | includes lockfiles and data files |
| 43 | Conventional commits (l. 248) | 36.6% | 36.6% (43.0% of non-merge) | PASS / FAIL-desc | merges in the denominator |
| 44 | README language (l. 48, 252) | Ru 87.0, En 9.7, Kk 2.9, mixed 0.4% of 1,185 | same | PASS (number), **construct fails** | 11 of 34 "Kazakh" READMEs are majority-Latin |
| 45 | Template-only READMEs (l. 252) | 63 | 63 | PASS | plus 5 no-README and 1 too-short, not mentioned |
| 46 | "Kazakh letters in 12.0% of READMEs" (l. 252) | 12.0% | 150/1,254 = 12.0%; of 1,185 = 12.6% | **FAIL-desc** | denominator |
| 47 | Commit script Latin (l. 252) | 89.4% | 89.4% (full body incl. merges); 87.5% non-merge subjects | PASS / FAIL-desc | |
| 48 | Kazakh letters in 23 of 31,955 commits (l. 252) | 23 | 23 (category requires Cyrillic majority) | FAIL-desc | 18 non-merge subjects contain any Kazakh letter |
| 49 | README words / headings (l. 252) | 1,477 (1,395–1,568) / 15 | 1,477 / 15 | PASS | headings include `#` lines in code blocks (median unchanged) |
| 50 | Install / images / deployed (l. 252) | 92.2 / 17.8 / 6.8% | same over 1,254; 97.5 / 18.8 / 7.2% over 1,185 | **FAIL-desc** | denominator stated as READMEs |
| 51 | Generic findings (l. 263) | 4,597 in 131; 93.5% data files | n/v | n/v | private file |
| 52 | Provider findings / placeholders / repositories (l. 263) | 127 / 10 / 73 (5.8%) / 36 final | 73/1,254 = 5.8%; Fig. 6 repo-rule pairs sum to 80 → 73 unique | internally consistent; n/v | "unreadable" class unreported |
| 53 | OpenAI keys (l. 48, 263) | 77 in 61 (4.9%); 30 final | 61/1,254 = 4.9%, 30/1,254 = 2.4% | consistent; n/v | |
| 54 | "All ... have the structural marker" (l. 190, 263) | 77 of 77 | true by construction of the Gitleaks rule; code sets it to `len(oa)` | **FAIL (not a check)** | M7 |
| 55 | Key files (l. 265) | .env.example 32, .env 27 | Fig. 6b sums to 77 | consistent | |
| 56 | Keys vs .gitignore (l. 265) | 5.9 vs 2.1%, V = 0.079, p = 0.008 | 916 vs 338 repositories → about 54 + 7 = 61, consistent | consistent; confounded | OpenAI-SDK repositories: .gitignore covers .env in 91.1% vs 46.0% |
| 57 | Hygiene flags (l. 265) | .env 2.7, pycache 3.7, node_modules 0.6, venv 0.4, gitignore-env 73.0% | same | PASS | |
| 58 | Track counts, Kruskal–Wallis (l. 276) | 145 / 115 / 115 / 29; H = 19.0, p = 0.062 | same; ε² = 0.019 | PASS | |
| 59 | Table 2 medians, tests, Python | per `facts.tracks` | recomputed matches | PASS | labels unvalidated (M12) |
| 60 | Table 3 clone vs API | 3,649 / 3,649 | 3,649 / 3,649 (re-run `git rev-list --count HEAD`) | PASS | |
| 61 | Table 3 template found / rewrote | 3,615 / 34 | 3,615 / 34; 0 of 34 have an organiser root commit | PASS | "rewrote" is plausible |
| 62 | Table 3 rebuilt vs earlier table | 3,641 / 3,644 / 3,648 | same (3,625 without the −1 adjustment) | PASS | not an independent source |
| 63 | Table 3 template fixes | 16 | 16 (created 27 Jun–31 Jul, 0 active) | PASS | |
| 64 | Fig. 1(c) "All reported numbers recomputed by separate code" | claimed | no such code in the repository | **FAIL** | M7 |
| 65 | "we release the derived data" (l. 48, 75, 319) | claimed | `public_data_generated/` empty | **FAIL** | M11 |
| 66 | PR-only commits "we report separately" (l. 173) | claimed | not in the paper (117 repositories in facts) | **FAIL** | minor |
| 67 | Gitleaks "kept only rule, file and time" (l. 167) | claimed | also commit SHA, line, entropy | **FAIL-desc** | privacy statement |

## 7. Citation-support audit (every `\cite` in `main.tex`)

Sources checked: `literature/notes/abstracts.md` and `abstracts_2.md`, the current `references.bib`, and live pages for grey literature: hackalem.ai, Astana Times, Qumash and Ulys were fetched on 27 Sep 2026. Kazinform returned HTTP 403, so I relied on search-result snippets for it. DOI metadata is audited separately. Below, I flag only metadata that affects meaning.

| Line | Cite key(s) | Sentence (short) | Supported? | Evidence | Fix |
|---|---|---|---|---|---|
| 55 | nolte2020hackathon, mcintosh2021hackathon, halmans2026hackrep | hackathons studied "through case studies and at scale through the repositories" | partly | All three are large-scale, repository- or listing-based. None is a case study. | Cite a review or case study for the first half, e.g. Chau & Gerber CHI 2023, or drop "case studies". |
| 55 | peng2023copilot | controlled experiments report faster task completion | yes | 55.8% faster in an RCT | — |
| 55 | ziegler2024copilot | "field studies report faster task completion" | **no** (for this clause) | CACM study relates *perceived* productivity to acceptance-rate data. Task completion time is not measured. | Cite Ziegler only for perceived productivity, as l. 92 does. |
| 55 | barke2023grounded | observational work on interaction | yes | grounded theory, 20 observed participants | — |
| 55 | liang2024usability | observational work on interaction | partly | It is a survey of 410 developers, not observation. | Say "observational and survey work". |
| 55 | jimenez2023swebench, yang2024sweagent | agents evaluated on real repository tasks | yes | SWE-bench (issue resolution); SWE-agent | — |
| 55 | li2025aidev, agarwal2026aiides | agents observed authoring PRs in OSS | yes | 456k agent PRs; difference-in-differences on AIDev | — |
| 55 | zhou2026quickbuild | interviews at one event | yes | exploratory interviews, two-day AI hackathon | — |
| 55 | gama2025vibes | one educational event, nine teams | yes | 31 participants, 9 teams | — |
| 55 | chen2026codeforall | month-long online event | yes (event) / partly (umbrella "qualitative and small") | mixed methods with standardised project evaluations; participant count not in abstract | Reword "mostly qualitative, single-event". |
| 55 | sajja2024genaihack | a single university case | yes | 2023 University of Iowa hackathon case study | — |
| 57 | hackalem2026site | Astana, in person, **five-hour window**, up to three, Codex required | partly | Site: mandatory offline presence, up to three members, Codex required. **No duration on the site.** | Cite Ulys, Astana Times or Kazinform for "five hours". |
| 57 | qumash2026queue, ulys2026survival | 6,586 applications for 2,500 seats | yes | Qumash: 6,586 applications, planned 2.5 thousand. Ulys: 6,586, about 2,500 simultaneously. | — |
| 57 | astanatimes2026guinness | official GWR attempt, category, result pending | yes | "most participants in an agentic AI hackathon"; result announced after verification | — |
| 89 | nolte2020hackathon | short-term continuation ↔ preparation and winning; long-term ↔ team skills | yes (slightly simplified) | also technical capabilities and intention to expand reach | optional |
| 89 | mcintosh2021hackathon | "MLH events of **two seasons**"; most commits in first week; few active after 6 months | partly | Abstract: "2018–2019 MLH-affiliated" projects (whether one or two MLH seasons is unclear); 77% of commits in week one; 7% active after 6 months | Say "the 2018–2019 MLH events". |
| 89 | halmans2026hackrep | large dataset from project listings; continuation, team composition, geography | yes (analyses) / check ("from project listings" not in abstract) | 100,356 repositories; preliminary analyses as stated | Confirm the collection source (Devpost) in the paper. |
| 92 | peng2023copilot | Copilot group faster than control | yes | | — |
| 92 | ziegler2024copilot | user study relating perceived productivity to usage data | yes | | — |
| 92 | barke2023grounded | acceleration and exploration modes | yes | | — |
| 92 | liang2024usability | benefits and control problems | yes | keystrokes and speed; trouble controlling the tool | — |
| 92 | jimenez2023swebench | measures issue resolution | yes | | — |
| 92 | yang2024sweagent | studies agent–computer interfaces | yes | title (no abstract in notes) | — |
| 92 | li2025aidev | agent PRs from five agents | yes | Codex, Devin, Copilot, Cursor, Claude Code | — |
| 92 | agarwal2026aiides | velocity gains after adoption plus persistent quality risks | partly | Velocity gains occur **only when agents are the first observable AI tool**; minimal otherwise. Quality risks persistent (yes). | Add the condition. |
| 92 | chatlatanagulchai2025agentreadmes | context files characterised in OSS | yes | 2,303 files, 1,925 repositories; TOSEM DOI 10.1145/3840295 verified | Key year 2025 vs published 2026 (cosmetic). |
| 92 | gloaguen2026agentsmd | effect on task success evaluated | yes | | — |
| 92 | baumann2026swechat | in a large share of sessions the agent writes nearly all committed code | yes | 41% of sessions | — |
| 95 | gama2025vibes, waseem2025vibepractice | definition of "vibe coding" | yes | both define it as NL-prompt-driven development | The style guide asks for the term's origin; it is not cited. |
| 95 | zhou2026quickbuild | GenAI for coding, learning, documentation; checking output under time pressure | yes | | — |
| 95 | gama2025vibes | novices deliver demos, little SE practice | yes | "limited engagement with core software engineering practices" | — |
| 95 | chen2026codeforall | no-manual-editing rule shapes prompting and debugging | yes | | — |
| 95 | prather2023robots, denny2024computinged | educators reviewed implications | yes | | — |
| 98 | meli2019git | leakage frequent and persistent | yes | >100k repositories; thousands of new secrets daily | — |
| 98 | sinha2015secretkeys | detection and mitigation methods proposed | yes | | — |
| 98 | basak2023secretbench | methods "benchmarked" | partly | SecretBench is a labelled *dataset for* evaluating tools; it does not itself benchmark tools | Add Basak et al., ESEM 2023 (tool comparison; DOI 10.1109/ESEM56168.2023.10304853). |
| 98 | krause2022pushed | developers who leaked describe remediation difficulty | yes | 14 interviews with developers who had leaked secrets | Bib now points to USENIX Security '23 (correct venue). |
| 98 | huang2024codesecret | completion models reproduce credentials | yes | | — |
| 98 | gao2026mindyourkey | LLM API keys leaked from mobile apps | yes | 444 iOS apps | — |
| 98 | zhao2025vibesafe, deng2026vibeinsecurity | vulnerabilities in agent-generated and vibe-coded apps | yes | | — |
| 101 | kalliamvakou2014perils | inactive/personal repositories; unmerged-looking PRs | yes | | — |
| 101 | hoess2025toolmatter | tools disagree on basic counts | yes | up to 500% | — |
| 101 | prana2019readme | README content categorised | yes | title | Bib year 2018 vs EMSE 24(3) 2019; align. |
| 101 | saghi2025procrastination | informs reading of deadline effects | partly | 15-developer interview study on procrastination; no deadline-timing data | See l. 285. |
| 106 | hackalem2026site | free; solo allowed | yes | "participation is free"; "can register individually" | — |
| 106 | qumash2026queue, ulys2026survival | queues; registered people not admitted; organisers said seats were limited | yes | both articles | — |
| 116 | hackalem2026site | date and place | yes | | — |
| 117 | astanatimes2026guinness, kazinform2026fivehours | "five hours; **13:00–18:00** ... inferred" | partly | Five hours: yes (Astana Times; Kazinform title; also Ulys). **Neither gives 13:00–18:00.** Kazinform returned 403. | Split the row: duration [press]; times "this study". |
| 118 | hackalem2026site | up to three; solo | yes | | — |
| 119 | hackalem2026site | Codex required | yes | "team must use Codex during development" | — |
| 120 | hackalem2026site, qumash, ulys | 2,500 seats; 6,586 applications | yes | site: "2 500 places, first come, first served" | — |
| 121 | kazinform2026fivehours, astanatimes2026guinness | 21 countries | yes (Astana Times); Kazinform not fetched (snippets consistent) | "More than 2,500 participants from 21 countries and 129 universities" | Consider adding the participant count. |
| 122 | hackalem2026site | US$1.1M prizes and resources | yes | "$1 100 000 in prizes and technology resources" | — |
| 123 | astanatimes2026guinness | category; previous record 2,089; pending | yes | 2,089, India, Dec 2025 | — |
| 124 | hackalem2026site | awards 1 Oct | yes | awards 01.10 at Digital Bridge (Demo Day 29.09 also listed) | — |
| 167 | gitleaks2026 | tool, v8.30.1 | yes | local binary and checksum file are v8.30.1 | Record the checksum in the paper or supplement. |
| 282 | qumash2026queue, ulys2026survival | people registered but could not get in | yes | | — |
| 285 | saghi2025procrastination | last-hour peak "resembles deadline behaviour described for developers in general" | partly | Interview study of procrastination causes and effects, not observed deadline surges | Cite deadline and commit-timing work (Edwards 2009; Kazerouni 2017; Kuutila 2020 time-pressure SLR). |
| 285 | baumann2026swechat | "with agents writing much of the code **in similar settings**" | partly | OSS developers' sessions, not hackathons or time-boxed events | Drop "in similar settings". |
| 285 | agarwal2026aiides, zhao2025vibesafe, deng2026vibeinsecurity | quality risks of agent code documented | yes | | — |
| 288 | li2025aidev | adoption estimated "from trailers or author accounts, as in datasets of agent pull requests" | partly | AIDev also uses **branch prefixes**, PR labels and co-author metadata, i.e. the "complementary traces" the paper recommends | Reword: AIDev already combines traces; note residual tool-specific bias. |
| 294 | meli2019git, krause2022pushed | measures (templates, org secret scanning with push protection, short-lived keys) "follow earlier recommendations" | partly | Neither recommends push protection or short-lived event keys specifically. Meli evaluates mitigations; Krause asks for low-cost tooling and platform support. | "are consistent with". |
| 297 | kalliamvakou2014perils, hoess2025toolmatter | such details can change basic counts | yes | | — |

**Summary of the citation audit:**
- One "no": Ziegler et al. for "faster task completion" (l. 55).
- 16 "partly":
  - l. 55: the case-study sentence, Liang, Chen (umbrella).
  - l. 57: the site cited for the five-hour window.
  - l. 89: McIntosh "two seasons".
  - l. 92: Agarwal (condition omitted).
  - l. 98: Basak "benchmarked".
  - l. 101: Saghi.
  - l. 117: Table 1 coding window.
  - l. 285: Saghi, Baumann "similar settings".
  - l. 288: AIDev method.
  - l. 294: "follow earlier recommendations".
  - HackRep "project listings" (check only).
- No fabricated references found. Every cited work I checked exists and is on topic.

## 8. Missing analyses that would materially strengthen the paper (feasibility with existing data)

1. **Funnel with archive status** (M1): repositories archived before the event, open, active, matched. Feasible now from `repos.csv` (S).
2. **Per-team deadline-share distribution** (M3/M4): ECDF plus share above 50%. Already computed (S).
3. **Robust creation-date model** (M5): categorical or spline on open, non-batch, non-test repositories. Feasible now (S).
4. **Sensitivity table**: committer vs author time (1,057 vs 1,057), window ±30/60 min (1,057–1,061), features at the 18:00 state vs final HEAD, excluding pre-event code. Clones available (S–M).
5. **Per-tool trace matrix**: Codex (AGENTS.md, codex/ branches, Codex trailers, organiser-app identity commits) vs Claude Code (CLAUDE.md or `.claude/`, trailers) vs others, with overlaps and lower bounds on use. Data available (S–M).
6. **Attendance triangulation**: distinct non-bot author e-mails per active repository (counted in memory; current sum 2,795 includes bots) vs "more than 2,500 participants". Feasible (S), and privacy-safe if aggregated.
7. **Pre-event code** (Imam et al. 2021): share of active repositories with pre-13:00 commits (173) and lines (33 above 1,000). Relate to tests and AGENTS.md. Feasible (S).
8. **AGENTS.md association with covariates**: activity, pre-event code, Codex branches, primary language. Already: OR for tests 3.5 [2.0–6.2] after log commits (S).
9. **Credential association, stratified** by OpenAI SDK and `.env.example` (M–H or logit), run privately. Also report key *first-appearance* time relative to the agent-signature timeline, for example whether keys enter in agent-signed commits. Aggregate only (M).
10. **Validated instruments**: two-rater README language labels (full text, κ); double-coded track sample; hand-check of the 127 provider findings (confirmed / placeholder / unclear). Private, aggregate only (M).
11. **Commit-level process measures**: inter-commit intervals, bursts (18 repositories have ≥10 commits in one minute), squash or imports, merge share (16.2%) by rhythm cluster (S–M).
12. **Baseline comparison** (journal version): HackRep provides commit timestamps for about 100k hackathon repositories. Compute last-hour share, test-file and Dockerfile prevalence for comparable one-day events before 2023 to test the "cheap artefacts under agents" conjecture (l. 285) (M–L).
13. **Jury linkage** (after 1 Oct, as planned): pre-register it now. Outcome is the award; predictors are activity, artefacts, traces. Report as confirmatory (M).

## 9. Related-work gaps (verified; DOIs checked by web search on 27 Sep 2026)

**Hackathons**
- Chau, C. W., & Gerber, E. M. (2023). *On Hackathons: A Multidisciplinary Literature Review.* CHI '23. DOI 10.1145/3544548.3581234. Supports the "case studies" half of l. 55.
- Imam, A., Dey, T., Nolte, A., Mockus, A., & Herbsleb, J. D. (2021). *The Secret Life of Hackathon Code: Where does it come from and where does it go?* MSR 2021, 68–79. DOI 10.1109/MSR52588.2021.00020. Pre-existing code in hackathon projects, relevant to the 173 active repositories with pre-event commits.

**Commit timing, deadlines, time pressure**
- Claes, M., Mäntylä, M. V., Kuutila, M., & Adams, B. (2018). *Do programmers work at night or during the weekend?* ICSE '18. DOI 10.1145/3180155.3180193.
- Karyotakis, I., Talos, E., & Spinellis, D. (2026). *TGIF: the evolution of developer commit times.* Empirical Software Engineering 31. DOI 10.1007/s10664-025-10767-2.
- Kuutila, M., Mäntylä, M., Farooq, U., & Claes, M. (2020). *Time pressure in software engineering: A systematic review.* IST 121, 106257. DOI 10.1016/j.infsof.2020.106257.
- Edwards, S. H., Snyder, J., Pérez-Quiñones, M. A., Allevato, A., Kim, D., & Tretola, B. (2009). *Comparing effective and ineffective behaviors of student programmers.* ICER '09. DOI 10.1145/1584322.1584325.
- Kazerouni, A. M., Edwards, S. H., & Shaffer, C. A. (2017). *Quantifying Incremental Development Practices and Their Relationship to Procrastination.* ICER '17. DOI 10.1145/3105726.3106180.

**Mining git (timestamps, rewritten history)**
- Bird, C., Rigby, P. C., Barr, E. T., Hamilton, D. J., German, D. M., & Devanbu, P. (2009). *The promises and perils of mining git.* MSR 2009. DOI 10.1109/MSR.2009.5069475.

**LLM and agent-assisted development in repositories (2024–2026)**
- Tufano, R., Mastropaolo, A., Pepe, F., Dabić, O., Di Penta, M., & Bavota, G. (2024). *Unveiling ChatGPT's Usage in Open Source Projects: A Mining-based Study.* MSR '24. DOI 10.1145/3643991.3644918.
- He, H., Miller, C., Agarwal, S., Kästner, C., & Vasilescu, B. (2026). *Speed at the Cost of Quality: How Cursor AI Increases Short-Term Velocity and Long-Term Complexity in Open-Source Projects.* MSR '26. DOI 10.1145/3793302.3793349.

**Secret detection tools**
- Basak, S. K., Cox, J., Reaves, B., & Williams, L. (2023). *A Comparative Study of Software Secrets Reporting by Secret Detection Tools.* ESEM 2023. DOI 10.1109/ESEM56168.2023.10304853. Directly relevant to Gitleaks precision and recall and to the placeholder filter.

**Methodology**
- Baltes, S., & Ralph, P. (2022). *Sampling in software engineering research: a critical review and guidelines.* EMSE 27, 94. DOI 10.1007/s10664-021-10072-8. For census vs inference (M5).
- Ralph, P., et al. (2020). *Empirical Standards for Software Engineering Research.* arXiv:2010.03525. DOI 10.48550/arXiv.2010.03525. Use its repository-mining standard as the checklist.
- Rousseeuw, P. J. (1987). *Silhouettes: a graphical aid to the interpretation and validation of cluster analysis.* J. Comput. Appl. Math. 20, 53–65. DOI 10.1016/0377-0427(87)90125-7.

**Gaps still to find (not verified; described only)**
- Studies of the language of README files and commit messages on GitHub, or of multilingual and non-English developer communities (for RQ5). *To find.*
- Studies of student or course project repositories on GitHub (the probable participant population; for RQ3/RQ5 comparisons). *To find.*
- Language identification for Kazakh/Russian code-mixed short text (to justify or replace the letter heuristic). *To find.*
- The origin of the term "vibe coding" (the style guide requires citing it). *To find* a citable form.
