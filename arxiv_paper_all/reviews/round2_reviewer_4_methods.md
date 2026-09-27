# Round 2, Reviewer 4: methods, statistics and reproducibility

**Manuscript:** "Measuring AI Coding Agent Use from Repository Traces: Evidence from a Hackathon Where Codex Was Required" (v3, `latex/main.tex`, 318 lines; `main.pdf` built 27 Sep 11:33).
**Reviewer profile:** empirical SE methodology, mining software repositories, statistics, reproducibility (IST, EMSE, TSE).
**How I checked:**
- I read `main.tex`, the rendered PDF, all listed scripts, `deviations.md`, `analysis_plan.md`, the round-1 reviews and the response.
- I recomputed about 75 numbers independently from `data/{repo_table,stack,commits,commit_repo_features,readme_features,repos}.csv`, using track labels from `public_data_generated/repositories.csv`. The scripts are `scratchpad/r4/recompute.py` and a few inline checks.
- I ran `reproduce_public.py` after confirming that it only reads files and prints. I did not run `recompute_core.py`, because it writes `recompute_core_result.json`, and I read its code instead.
- I opened nothing under `data/secrets_private/`, no `.env` file, no README sample or prereg file, and no clone or README text. I name no team repository here.
- **Versions:** `latex/numbers.tex` and `facts_paper.json` are byte-identical to the `versions/v2_2026-09-27/` snapshot. v3 changes prose only. The numbers that changed are the v1 → v2 changes (new denominators, new analyses), and the audit concentrates on those.
- **Tooling note:** the Write tool was blocked by a hook timeout, so this file was written with a quoted shell heredoc.

---

## 1. Summary

The paper studies all 3,649 repositories that the organisers of a five-hour hackathon created, at an event where Codex was mandatory. It reports:
- participation on a known denominator, with organiser artefacts separated out (pre-event archiving, an evening batch);
- process measures;
- agent traces per tool, now with two new exploratory analyses: README self-reports as a reference channel, and a within-repository comparison of commit sizes;
- product features;
- credential strings in public history.

The engineering is careful. **Every number I recomputed from the derived data matches the paper**, including all new v3/v2 numbers (Section 6). The round-1 methods issues are mostly resolved.

The remaining problems sit in the **interpretation of the new analyses**, in a few **statements the data contradict**, and in **reproducibility claims that the release does not yet support**:
1. The README self-report is described as an "independent" reference, but the regex and the data show that it is not independent of the traces.
2. The commit-size result is mislabelled and does not survive a minimal robustness check. Its comparison with Robbes et al. says the tool "was not chosen freely", but 89% of signed commits name Claude Code, the tool that was *not* required.
3. More than half of the Codex detections rest on `AGENTS.md` alone, a cross-tool file, so the 46.4% headline is not Codex-specific.
4. "Not through missing ignore rules" compares a final-state `.gitignore` with keys committed earlier.
5. The public data cannot reproduce the abstract's 69.6% or the commit-size result, although l. 65 says the headline results can be recomputed from public files alone.

## 2. Decision

**(a) arXiv preprint: accept after minor revision, with two hard blockers.**
- *Blocker 1:* responsible disclosure of the 61 repositories with OpenAI-format strings (30 still at HEAD) must be completed before posting (l. 309). `public_data_generated/` (credential aggregates plus a list of all 3,649 repositories with their HEAD commits) is already committed to git, so it must not be pushed before disclosure either.
- *Blocker 2:* remove or resolve the `\pending{}` placeholders (l. 168, 295, 309, 311, 313). An arXiv version should not carry "labelling in progress".
- The text fixes in Section 9 take about a day. No new data collection is needed.

**(b) EMSE / IST: major revision.** Reasons:
- The central contribution (what traces recover when the tool is known) rests on a reference channel with no measured validity.
- The per-tool trace definitions include unverified account matches and a non-specific context file.
- The README-language and track instruments are still not validated.
- The credential findings are not hand-checked.
- The public release does not reproduce the new analyses.

A journal version needs a validated reference (for example, a hand-coded sample of README mentions and account hits), sensitivity bounds for the trace definitions, and full public reproducibility.

---

## 3. Round-1 Reviewer 1 (methods): resolution

| # | Issue | Status | Evidence in v3 |
|---|---|---|---|
| M1 | 446 repositories archived before the event | **Resolved** (one residual error) | Funnel stage added (Fig. 2a, l. 181). χ² rerun on open non-batch repositories: I reproduce χ²(3) = 14.9, V = 0.083. The false "archived after the deadline" wording is gone. *Residual:* l. 121 says "the rest were archived before the event began", but 3,201 + 446 = 3,647. Two repositories were archived at 20:40 and 21:21 on 23 Sep. |
| M2 | "Complete population of registrations" | **Resolved** | Population is now "organiser-created repositories". Mapping and creation-date proxy are stated as assumptions (l. 132). Reconciliation: ≤ 2,740 author identities vs. > 2,500 participants (l. 185; I reproduce 2,740). The applications/seats reconciliation stays thin (Table 1 only). |
| M3 | False headline sentences | **Resolved** | 44.5% all five hours, 79.3% ≥ 4, median share 30.8%, 15.4% majority: all reproduced. |
| M4 | Weak clusters | **Mostly resolved** | Exploratory; null silhouette 0.19; Rousseeuw cited; distribution reported (Fig. 3b). Not done: restriction to teams with ≥ 5 commits and bootstrap stability (optional). |
| M5 | Fragile RQ1 inference; census stance | **Resolved** | Logit dropped. Census interpretation stated (l. 174). Kruskal–Wallis listed with ε². The naive χ² is shown only as an illustration (l. 279). |
| M6 | README language rule; validation; denominators | **Partly resolved** | Rule fixed (Kazakh needs a Cyrillic majority; 22/1,033). Denominators unified to 1,033. **Hand labels still pending** (Table 2, l. 168, 295). New problems: the run-instructions detector counts any fenced ```` ```python ```` block and file trees that list `docker-compose.yml` (see m4). The self-report shares use 1,057, not 1,033 (see m3). |
| M7 | Circular validation | **Resolved** | Marker row removed. Independent recount exists and shares no code (I read `recompute_core.py`; its logic is sound). The earlier table is called a consistency check. PR-only commits reported (427 in 117). |
| M8 | Credential analysis | **Partly resolved** | Placeholder filter described (l. 142). MH stratification reproduced from aggregates (6.1% vs 4.0%, χ² p = 0.287). Exploratory label added. Key commits joined to signatures. Recall cited. The "unreadable" class is empty (117 + 10 = 127). **Not fixed:** (i) `in_head` still matches on (rule, file), yet l. 142 says "whether the matched string was still present". (ii) "73 commits" (l. 273) are 73 *findings* joined to commits. (iii) The Gitleaks date basis (author date) is not stated. (iv) Hand check of the 127 findings deferred. (v) Disclosure pending. |
| M9 | Agent-trace constructs | **Mostly resolved; new issues** | PR refs separated. Bots excluded (`agent_kind != "bot"`). Exact tool-name match. "Generated with" parsing fixed. Per-tool matrix and overlap reproduced (309/181/82/485). Lower bound on non-required use stated. **Not done:** manual review of account hits. This matters now, because 255 of 332 Codex-signed commits (41 of 47 repositories) are account-only matches (see M3 below). |
| M10 | Plan wording; deviations; exploratory labels | **Partly resolved** | Wording fixed (l. 174). Deviations file has 14 items. **But** `deviations.md` #9 says the commit-size analysis was *dropped*, and v3 reports it with a new definition and a new test. The self-report analysis is not in the deviations file. l. 297 says commit size was "added after the analysis plan", but the plan contains it (as a pooled, exploratory median/IQR comparison). |
| M11 | Data release | **Partly resolved** | `public_data_generated/` exists, is committed (HEAD 3e86089) and passes its checksums. `reproduce_public.py` gives 17/17 PASS (I ran it). **But:** `arxiv_paper_all/` (including `reproduce_public.py`, `run_analysis.py`, the plan and the deviations) is untracked. The committed `src/extract_commits.py` and `src/readme_features.py` are older than the versions that produced the data (the working tree is modified). `requirements.txt` is unpinned and omits scipy. The DOI is pending. The new analyses cannot be run from public data (Section 8). |
| M12 | Track labels | **Resolved for arXiv** | 933/946, κ = 0.98. Unchecked subsets reported (19, 73). Caption qualified. Double-coding is deferred to the journal version. |

---

## 4. Major issues

### M1. The README self-report is presented as an independent reference, but it is neither independent nor a measure of use (l. 48, 63, 65, 137, 211, 282, 295)

**Definition.** `readme_features.py:48–50,92–93` sets `mentions_codex = \bcodex\b` and `mentions_claude = \bclaude\b`, case-insensitive, over the **raw README**: code blocks, URLs, badges and file trees included. The prose-cleaning step used for language (`NOISE`, `CODE_BLOCK`) is not applied. Consequences:
- `\bclaude\b` matches `CLAUDE.md` and `.claude/`, which READMEs list in project-structure trees. This couples the "self-report" mechanically to the `CLAUDE.md` file trace. Among repositories with a Claude mention, 48.1% have the file.
- `\bcodex\b` matches model identifiers such as `gpt-5-codex` or `codex-mini` (the product's model, not the development tool), `@openai/codex` install lines, `openai/codex` links and `codex/` branch names quoted in the README.
- "Claude" also names the product's LLM. **19 of the 81** Claude-mention repositories use the Anthropic SDK, and 5 of the 18 Claude mentions without any Claude Code trace are among them.

**Dependence on the traces (my recomputation, active repositories).** Even among repositories without any trace, mentions occur at some rate:

| | P(mention \| trace) | P(mention \| no trace) | OR |
|---|---|---|---|
| Codex | 117/490 = 23.9% | 51/567 = 9.0% | **3.2** |
| Claude | 63/263 = 24.0% | 18/794 = 2.3% | **13.6** |

A strong association is expected if both channels reflect use. But the conditional-independence assumption that turns P(trace | mention) into a recall estimate (trace ⟂ mention | use) is violated by at least three mechanisms:
- agent-written READMEs (the paper concedes this at l. 295);
- file-tree listings of context files;
- teams with elaborate workflows writing longer READMEs. READMEs that mention Codex have a median of 2,238 words, against 1,575 for other written READMEs.

The rule itself cuts the other way. Compliance statements ("we used Codex") can appear without meaningful use, which lowers P(trace | mention). So **69.6% is P(trace | README contains the token "codex")**. It is neither an upper nor a lower bound on the recall of the traces among Codex users.

**Coverage.** Only 15.9% of active repositories (16.3% of written READMEs) name Codex despite the mandate. The reference therefore covers a small, self-selected subgroup.

**Claims to change.**
- l. 137: "As a fourth channel, **independent of the traces**, we record whether the README names Codex or Claude, which we treat as a **self-report of use**." Rewrite: "As a fourth channel we record whether the README text contains the word Codex or Claude. We treat this as a partial self-report. It is not independent of the traces, because agents may write READMEs and READMEs may list context files."
- l. 65: "using README self-reports as an **independent** reference" → "using README mentions as a partial reference".
- l. 211: "The README self-reports ... **show how much the traces miss**" → "give a partial reference: among the 168 repositories whose README contains 'Codex', ...".
- l. 282: "a known required tool and README self-reports **make it possible to size it**" → "... make it possible to bound it under stated assumptions".

**Needed.**
1. Apply the prose cleaning (drop code blocks, URLs and file trees) and exclude `CLAUDE.md`, `.claude`, `*-codex` model names and `openai/codex` URLs. Report how the numbers change.
2. Hand-code a sample (for example all 81 Claude and 100 Codex mentions) as "states the dev tool was used" / "product model" / "other", with two raters and κ, and report P(trace | coded use).
3. Use one denominator (1,033 written READMEs) or state why it is 1,057 (see m3).

### M2. The commit-size comparison is mislabelled, fragile and mis-compared with Robbes et al. (l. 139, 174, 220, 282, 297)

**What the code does** (`run_analysis.py:359–369`):
- Unit and pairing: the per-repository median `code_lines` of signed and of other non-merge commits, in active repositories with both kinds (217). The two sets of medians are compared with a Wilcoxon signed-rank test.
- Reproduced exactly: 217 repositories; 240 vs 202; signed larger in 131/217 = 60.4% (Wilson 53.7–66.6); p = 0.0021.

**Problems.**
1. **Mislabelled statistic.** l. 220: "the median signed commit changed 240 lines and the median other commit 202". These are **medians of per-repository medians**. The pooled median signed commit changed 119 lines and the pooled median other commit 109. Rewrite: "across these repositories, the median of the per-repository median was 240 lines for signed and 202 for other commits".
2. **No effect size.** The matched-pairs rank-biserial correlation is 0.24 and the median paired difference is 58 lines. Report one of them.
3. **Not restricted to the window**, although l. 132 makes window commits the default. With window-only commits: 211 repositories, 58.8%, p = 0.008. The direction is the same, but say which set is used.
4. **Fragile.** Many per-repository "signed" medians rest on one or two commits (14% of pairs have exactly one signed commit):

   | Sample | Repos | Signed larger | p | Rank-biserial |
   |---|---|---|---|---|
   | Paper | 217 | 60.4% | 0.002 | 0.24 |
   | ≥ 3 signed commits | 160 | 54.4% | **0.80** | 0.02 |
   | ≥ 5 signed commits | 134 | 56.0% | **0.91** | 0.01 |
   | Claude-signed vs unsigned | 171 | 57.9% | **0.075** | 0.16 |
   | Codex-signed vs unsigned | 45 | 68.9% | 0.005 | 0.49 |
   | added + deleted, no exclusions | 217 | 61.3% | 0.0006 | 0.27 |

   The result is driven by repositories with few signed commits and by the Codex account-based commits (see M3). It is not a general property of agent-signed commits here.
5. **Wrong comparison claim.** l. 282: "The larger size of agent-signed commits agrees with their finding ... **here within the same repositories and in a setting where the tool was not chosen freely**."
   - 3,503 of 3,953 signed commits (88.6%) name Claude Code, the *non-required*, freely chosen tool.
   - In 77% of the 217 pairs the signed commits are mostly Claude.
   - The "other" group certainly contains unsigned Codex work, because Codex was required and signs in only 4.4% of repositories.

   The within-repository design is a real strength over Robbes et al., whose TOSEM abstract contrasts trace-detected "agent-assisted" commits with commits "only authored by human developers". But here the control group is known to be contaminated. Rewrite: "Within repositories, commits with an agent signature (mostly Claude Code) were somewhat larger than unsigned commits, which may themselves include unsigned Codex work. The difference was not robust to requiring at least three signed commits per repository."

   Alternatively, drop the sentence from the Discussion.
6. **NON_CODE regex** (`extract_commits.py:52–54`) is narrower than the paper's wording "lock files, data files and generated output" (l. 139).
   - Not excluded: `.json` data (the generic Gitleaks rule found 93.5% of its 4,597 findings in `.json/.jsonl/.txt/.csv`), `.txt`, `.sql`, `.xml`, `.html` reports, `coverage/`, `out/`, `target/`, migrations and snapshots.
   - Excluded, although it is code: `.ipynb`.
   - Harmless: binary files (numstat `-`) count 0 anyway, and rename parsing (`split(" => ")[-1].rstrip("}")`) is adequate.
   - The result does not depend on the regex (61.3% without any exclusion), so state the list exactly rather than widening it.
7. **Deviation not disclosed.** `deviations.md` #9 says "Dropped". The plan specified a pooled median/IQR comparison, and v3 uses a paired within-repository test on a new measure. l. 297 wrongly says the analysis "was added after the analysis plan". Update #9 and add the self-report analysis as a new item.

The conventional-commit contrast (48.5% vs 42.1%, l. 220) pools all 31,955 team commits across all repositories and times. It is not a within-repository comparison. Window/active only: 48.7% vs 43.1%. Label it pooled and descriptive, or pair it like the size analysis.

### M3. Tool-specific trace definitions: Codex detection is partly non-specific, and Codex "signatures" are unverified account matches (l. 48, 137, 209, 282)

- **`AGENTS.md` carries half the Codex headline.** 259 of the 490 Codex-detected repositories (52.9%) are detected **only** through `AGENTS.md`. Of the 181 "both Codex and Claude" repositories, **120** show Codex only through `AGENTS.md`. 125 repositories have both `AGENTS.md` and `CLAUDE.md`. `AGENTS.md` is a cross-tool convention; the paper says other agents read it (l. 137). Treating `AGENTS.md` in Claude-traced repositories as non-specific gives a Codex-specific rate of **370/1,057 = 35.0%**. Report the bracket (35.0–46.4%). It strengthens the "traces miss Codex" conclusion, but the abstract's 46.4% has to be read as "Codex or a shared context file".
- **Codex signatures are mostly accounts, not trailers.** Codex-kind signed commits: 77 trailer, 1 marker-only, **254 account-only** (255 with an account hit). At repository level: 41 of 47 are account-only.
  - The account rule is `BOT_ACCOUNT` (`[bot]`, `@openai.com`, `copilot`, …) or `TOOL_NAME.fullmatch` on the author or committer name.
  - It fires on a human who sets `user.name` to "codex", and on `[bot]` committers whose paired author string contains an agent token (`kind = agent_kind(author + " " + committer)`, l. 129).
  - Round 1 asked for a manual review of non-trailer account hits. It has still not been done, and it now carries most of the Codex signature channel and much of the commit-size effect (M2).
- **Branch trace wording.** l. 209 says "a branch starting with `codex`". `AGENT_BRANCH` plus `agent_kind` also map `openai-*`, `openai/*` and `chatgpt-*` branches to Codex (and `anthropic-*` to Claude). In a hackathon where 69.3% of repositories call the OpenAI API, a branch such as `openai-integration` is plausible. Report the count that literally starts with `codex`, or fix the rule.
- **Timing of traces.** Signatures come from all team commits (195 signed commits in active repositories fall outside the window), and files come from the final state. With window-only signatures: Claude 176 (vs 179) and Codex 47 (unchanged). This is minor, but state it.
- The "generated with/by … openai" false-positive risk I expected is negligible: one Codex commit is marker-only.

### M4. The credential route claims and the threat-model bounds do not follow from the measures (l. 142, 144, 273, 285)

- **"Not through ... missing ignore rules"** (l. 273; l. 285: "neither agent-signed commits nor missing ignore rules explain them").
  - `gitignore_covers_env` is measured at the **final** state, while the keys were committed earlier.
  - By git semantics, each of the **27 OpenAI findings in `.env` files** was committed when `.env` was not ignored, or was force-added. Adding the ignore rule afterwards is a common remediation, and in that case the final-state flag reads "covered".
  - So the data cannot rule out missing ignore rules for the `.env` route, which is about 35% of OpenAI findings.
  - The template route (`.env.example`, 32 findings) is the one the data support.
  - Rewrite: "Most key strings sat in committed `.env.example` templates, which ignore rules do not cover. Keys in `.env` files were committed while those files were not ignored. The final-state `.gitignore` cannot tell whether the rule existed at that time."
- **"Not through agent-signed commits"** is literally true (5 of 73; baseline 9.0%). But the required agent did not sign, so this says nothing about whether agents were involved. Add: "unsigned commits may still be agent-written".
- **Threat-model bounds** (l. 144): "Our counts are therefore upper bounds on usable keys and lower bounds on exposure, because keys in formats that the rules do not cover are missed."
  - The two halves conflict. If keys in uncovered formats are missed, the count is not an upper bound on usable keys.
  - It is an upper bound only on usable keys *of the covered formats*: not every matched string is valid, and the unit is findings or repositories, not distinct keys.
  - It is a lower bound on exposure for more reasons than format coverage: history rewritten before collection (34 repositories lack the template commit), force-pushed or deleted commits a real-time observer would have seen, and Gitleaks recall within covered formats. It holds only if the unvalidated placeholder filter does not pass fake strings. For OpenAI this is unlikely, because the rule requires the `T3BlbkFJ` segment. For whole-line rules (curl header, JWT) it is less clear.
  - Rewrite: "The counts are upper bounds on the number of repositories with a usable key in the covered formats, since we did not test validity, and lower bounds on the number with any exposed credential, since uncovered formats, commits removed before our collection and scanner misses are not counted. Our post-hoc clone sees less than the real-time observer of the threat model."
- **Stored fields** (l. 142): the scanner also keeps `Entropy`. More importantly, `in_head` is a (rule, file) match at HEAD, not "the matched string". Rewrite: "whether a finding of the same rule remained in the same file in the final state".
- **Units** (l. 273): "5 of the 73 **commits**" are 73 of 77 findings joined to team commits (`kc` has one row per finding). Report distinct commits, and say that the 4 unmatched findings sit on commits outside the branches (for example PR-only).
- **Date basis** (l. 264): state that Gitleaks reports the author date.
- **Organiser-issued keys?** If the event issued API keys, several repositories may hold the same key. Ask the organisers and state the answer. It changes what "exposure" means.

### M5. Reproducibility claims exceed what the release supports (l. 65, 297, 311; DATA_CARD)

- l. 65: "the headline results can be recomputed from the public files alone". **This check fails for the new headline analyses.**
  - `public_data_generated/repositories.csv` has no `mentions_codex` or `mentions_claude` (only `readme_mentions_agent_tool`), so the 69.6% of the abstract, introduction and conclusion cannot be recomputed.
  - `commits.csv` has no `code_lines`, so the commit-size result cannot be recomputed (only the unfiltered variant).
  - `reproduce_public.py` checks 17 numbers, none of them from the new analyses. On the shared columns the public files agree exactly with the regenerated private data (agent kinds, added and deleted lines, scripts). They were exported at 02:37, before the 02:59 regeneration, and are consistent.
- The public git tree lacks `arxiv_paper_all/` (untracked), which holds `run_analysis.py`, `reproduce_public.py`, `analysis_plan.md` and `deviations.md`. DATA_CARD tells readers to run a script that is not in the repository.
- The committed `src/extract_commits.py` and `src/readme_features.py` predate the working-tree versions that generated `code_lines`, `subject_script`, `author_key`, `mentions_codex` and `mentions_claude`.
- `requirements.txt` is unpinned (`>=`) and omits scipy and numpy. The Git and Gitleaks versions are not in a lock file.
- DATA_CARD carries the v2 title. Its sentence "[recollection.csv] cannot be joined to the other files" is misleading: 806 of 1,057 active repositories are unique on (creation date, team commits, window commits, branches), and anyone can recompute these from GitHub. The privacy section admits this. Reword to "shares no key with the other files".
- **Fix:** add `mentions_codex`, `mentions_claude` (after the M1 cleaning) and `code_lines` to the release, and extend `reproduce_public.py` to every abstract and conclusion number. Commit `arxiv_paper_all/` (minus private inputs) and the current `src/`. Pin the environment (`pip freeze`) and record the Git and Gitleaks versions with checksums. Update the DATA_CARD title.

---

## 5. Minor issues

- **m1 (l. 121).** "the rest were archived before the event began": 2 repositories were archived at 20:40 and 21:21 on 23 Sep. Use "446 before the event and 2 later that evening".
- **m2 (l. 282).** "If all teams complied, a trace-based study of this event would have missed about half of the **use** of the required tool." The unit is repositories, not use, and compliance is doubtful (82 repositories show only Claude Code). Use "... would have classified about half of the active repositories as showing no Codex use".
- **m3 (l. 132 vs 211).** The self-report shares use all 1,057 active repositories, although l. 132 says README measures use the 1,033 written READMEs. On 1,033 the Codex mention share is 16.3% and the Claude share 7.8%.
- **m4 (l. 139, 233).** Run instructions: `CODE_BLOCK.findall` returns the fence line, so ```` ```python ```` matches `\bpython\b`. A file tree listing `docker-compose.yml` matches `\bdocker\b`. The 97.2% is therefore "a setup heading, or a code block mentioning a run tool". Say so, or match only lines that begin with a command.
- **m5 (l. 304).** "the organisers' own actions **moved** the activity rate by 19.2 percentage points" is causal wording for a denominator choice. Use "... the choice of denominator, driven by the organisers' actions, changes the activity rate by 19.2 percentage points". l. 63 "most of the gap": 1,472 of 2,592 inactive repositories (56.8%) are archived or in the batch. Give the figure.
- **m6 (l. 282).** "Adoption estimates that rely on signatures [li2025aidev, robbes2026agenticmuch]". AIDev is built from agent-authored PRs, and Robbes et al. combine several heuristics. Use "to the extent that adoption estimates rely on signatures ...".
- **m7 (l. 209).** "Of all team commits, 3,953 (12.4%)" uses all 31,955 commits in all 1,254 repositories and at all times. Window commits of active repositories: 3,541/30,418 = 11.6%. Either is fine if it is labelled.
- **m8 (l. 297).** "the self-report and commit-size analyses were added after the analysis plan": commit size was in the plan (see M2.7).
- **m9 (l. 220).** "In a second exploratory comparison" for `AGENTS.md`. The plan pre-specified this family (RQ4, Holm across three outcomes), so it is planned, not exploratory. Labelling it exploratory is conservative, but `run_analysis.py:325` and the text should agree with the plan.
- **m10 (l. 174).** The ε² formula is correct (see Section 7), but name its source, because readers also meet η²_H = (H − k + 1)/(n − k) (0.008 here).
- **m11 (l. 273).** The MH stratifies by any LLM SDK. Stratifying by OpenAI-SDK use is more specific to OpenAI keys. The estimate is unlikely to change (crude p = 0.287).
- **m12 (l. 168).** The README label sample (81 items) was drawn from the 02:12 feature file, and the features were regenerated at 02:59. Confirm that the key file's automatic labels equal the current labels before computing agreement.

---

## 6. Data-to-claim audit (macro → facts_paper.json → code → my recomputation from data/*.csv)

All values below were recomputed with my own code (`scratchpad/r4/recompute.py`), not by rerunning `run_analysis.py`. "New" marks v2/v3 analyses or changed denominators.

| # | Claim (line) | Paper | Mine | Result |
|---|---|---|---|---|
| 1 | Repositories (48) | 3,649 | 3,649 | pass |
| 2 | Archived before event (48, 181) | 446 (12.2%) | 446 | pass |
| 3 | Bulk ops: 126 (18:30–18:32, 15 Sep), 56 (17 Sep), 242 (20:01–20:05, 22 Sep), 22 other (181) | as stated | 126 / 56 / 242 / 22 | pass |
| 4 | Pre-archived created 15–21 Sep / with team commits (181) | 426 / 157 | 426 / 157 | pass |
| 5 | Evening batch; max per minute vs organic (48, 132) | 1,040; 15 vs 8 | 1,040; 15 vs 8 | pass |
| 6 | Batch active (181) | 14 (1.3%) | 14/1,040 = 1.3% | pass |
| 7 | Active (48, 183) | 1,057, 29.0% (27.5–30.5) | 1,057, 29.0% (27.5–30.5) | pass |
| 8 | Active of open (183) | 33.0% of 3,203 | 1,057/3,203 = 33.0% | pass |
| 9 | Active of open non-batch (48, 183) | 1,043/2,163 = 48.2% (46.1–50.3) | same | pass |
| 10 | Creation χ² open non-batch (183) | χ²(3) = 14.9, p = 0.002, V = 0.08 | 14.9, p = 0.0019, V = 0.083 | pass |
| 11 | Creation shares 43.2% (22 Sep) to 53.9% (1–14 Sep) (183) | as stated | 16/37 = 43.2%; 407/755 = 53.9% | pass |
| 12 | Naive χ² (279) | χ²(3) = 608.2, V = 0.41 | 608.2, V = 0.408 | pass |
| 13 | Outside-only 197 / all before 194 / pre-archived 157 (185) | as stated | 197 / 194 / 157 | pass |
| 14 | Author identities sum / median (185) | 2,740 / 3 | 2,740 / 3 | pass |
| 15 | Window commits (196) | 30,418 | 30,418 | pass |
| 16 | Pooled last-hour share; peak 17:40–17:50, 1,649 (196) | 28.8%; 1,649 | 28.8%; 17:40, 1,649 | pass |
| 17 | Median s_i, IQR (196) | 30.8 (19.4–43.8) | 30.8 (19.4–43.8) | pass |
| 18 | Majority in last hour (196) | 163, 15.4% (13.4–17.7) | 163, 15.4% (13.4–17.7) | pass |
| 19 | ≥ 4 hours / all 5 hours (196) | 79.3% / 44.5% | 838 → 79.3% / 470 → 44.5% | pass |
| 20 | First commit / last before deadline / commits per team (196) | 61; 9; 19 (10–35) | 60.8; 9.0; 19 (10–35) | pass |
| 21 | Pre-event repos / post-deadline repos (196) | 173 / 73 | 173 / 73 | pass |
| 22 | **New.** Codex any (48, 209) | 490, 46.4% (43.4–49.4) | 490, 46.4% (43.4–49.4) | pass |
| 23 | **New.** AGENTS.md / codex branch / Codex signature (209) | 33.3 / 18.9 / 4.4% | 352 / 200 / 47 → same | pass |
| 24 | **New.** Claude any / signature / file (48, 209) | 24.9 / 16.9 / 14.2% | 263 / 179 / 150 → same | pass |
| 25 | **New.** Overlap only Codex / both / only Claude / neither (209) | 309 / 181 / 82 / 485 | 309 / 181 / 82 / 485 | pass |
| 26 | Cursor / Copilot / Gemini (209) | 20 / 5 / 2 | 20 / 5 / 2 | pass |
| 27 | Signed commits; Claude / Codex (209) | 3,953 (12.4%); 3,503 / 332 | 3,953/31,955; 3,503 / 332 | pass (denominator: all team commits, see m7) |
| 28 | PR refs; with Codex branch (209) | 35.9%; 143 | 379 → 35.9%; 143 | pass |
| 29 | **New.** README names Codex (211) | 168 (15.9%) | 168/1,057 | pass (denominator, see m3) |
| 30 | **New.** Codex trace \| mention (48, 211) | 69.6% (62.3–76.1) | 117/168, same CI | pass (interpretation, see M1) |
| 31 | **New.** File / branch / signature \| Codex mention (211) | 49.4 / 30.4 / 7.7 | 83 / 51 / 13 of 168 | pass |
| 32 | **New.** Claude mention; trace \| mention; signature \| mention (211) | 81; 77.8; 58.0 | 81; 63/81; 47/81 | pass |
| 33 | **New.** Codex trace or mention (211) | 51.2% | 541/1,057 | pass |
| 34 | **New.** Commit size: repositories; medians (220) | 217; 240 vs 202 | 217; 240 vs 202 (medians of per-repo medians; pooled 119 vs 109) | pass (numbers) / **fail (wording)** |
| 35 | **New.** Signed larger; Wilcoxon (220) | 60.4% (53.7–66.6); p = 0.002 | 131/217; p = 0.0021 | pass (**not robust**, see M2) |
| 36 | **New.** Conventional signed vs other (220) | 48.5 vs 42.1 | 48.5 vs 42.1 (pooled, all times) | pass |
| 37 | AGENTS.md: commits 28 vs 16, δ = 0.36; hours 5 vs 4, δ = 0.26; tests 95.7 vs 82.7 (220) | as stated | 28 vs 16, 0.356; 5 vs 4, 0.260; 95.7 vs 82.7 | pass |
| 38 | Holm-adjusted p (220) | all < 0.001 | 9.5e−21, 2.5e−13, 2.7e−9 | pass |
| 39 | Adjusted OR for tests (220) | 3.51 (1.99–6.17) | 3.51 (1.99–6.17) | pass |
| 40 | Python / TypeScript / JavaScript (224) | 58.5 / 21.7 / 12.5 | same | pass |
| 41 | React / FastAPI / Vite / Tailwind / Next.js (224) | 46.5 / 43.2 / 32.8 / 21.2 / 16.5 | same | pass |
| 42 | Any LLM / OpenAI / other providers at most (224) | 73.0 / 69.3 / 2.9 | 772 → 73.0 / 69.3 / Anthropic 2.9 | pass |
| 43 | **New denominator.** Tests / Dockerfile / CI / deploy (224) | 87.0 / 33.3 / 14.3 / 6.2 | 920 / 352 / 151 / 66 of 1,057 | pass |
| 44 | Sensitivity: tests (224) | 86.6% of 831 | 720/831 | pass |
| 45 | **New denominator.** Russian / English / Kazakh / mixed (233) | 88.1 / 9.3 / 2.1 / 0.5 of 1,033 | 910 / 96 / 22 / 5 of 1,033 | pass |
| 46 | Any Kazakh letter (233) | 14.2% | 147/1,033 | pass |
| 47 | Subject script Latin / Cyrillic (233) | 87.5 / 12.1 | 87.5 / 12.1 | pass |
| 48 | Words median (IQR), headings (233) | 1,645 (1,049–2,413); 16 | same | pass |
| 49 | Run instructions / images / deployed link (233) | 97.2 / 21.3 / 8.1 | 1,004 / 220 / 84 of 1,033 | pass (construct, see m4) |
| 50 | Language × track (235) | χ²(33) = 201.1, V = 0.26, 8 of 48 cells < 5 | 201.1, 0.261, 8/48 | pass |
| 51 | Kruskal–Wallis (235) | H(11) = 19.0, p = 0.062, ε² = 0.02 | 18.97, 0.062, 0.0193 | pass |
| 52 | Python by track: min / max (235) | 30.4 (T12) / 95.7 (T4) | same | pass |
| 53 | Median commits by track (235) | 16–31 | 16–31 | pass |
| 54 | `.gitignore` covers `.env` / `.env.example` / `.env` committed (273) | 83.6 / 74.3 / 3.2 | 884 / 785 / 34 of 1,057 | pass |
| 55 | Ignore coverage among LLM / no LLM (273) | 90.9 / 63.9 | 90.9 / 63.9 | pass |
| 56 | Key share with / without ignore; p (273) | 6.1 vs 4.0; p = 0.287 | 54/884 vs 7/173 from aggregates; χ² p = 0.287 | pass (consistency) |
| 57 | Signed key commits vs baseline (273) | 5/73 (6.8%) vs 9.0% | Wilson 3.0–15.1; 138/1,528 = 9.0% | pass (unit, see M4) |
| 58 | Window shift −60 / −30 / +30 / +60 (Table 2) | 1,026 / 1,040 / 1,060 / 1,059 | same | pass |
| 59 | Author-time active (Table 2) | 1,057 | 1,057 | pass |
| 60 | Activity gap (304) | 19.2 pp | 48.2 − 29.0 | pass |
| 61 | Archive wave (121) | 3,201; "the rest before the event" | 3,201 + 446 + **2** later | **fail (text)** |
| 62 | Public reproduction (65) | "headline results ... from public files alone" | 17/17 pass, but the 69.6% and commit size cannot be computed | **fail (claim)** |

I could not recompute the RQ4 per-finding numbers (private by design). The aggregates are internally consistent: 54 + 7 = 51 + 10 = 61 repositories; 32 + 27 + 3 + 15 = 77 findings; 117 + 10 = 127.

---

## 7. Equation and statistic check

| Item | Paper | Check | Verdict |
|---|---|---|---|
| Last-hour share | s_i = ℓ_i / c_i, ℓ_i in 17:00–18:00, even spread 20% | Code: `hour = (ctime − 13:00)//3600 + 13`, `hour == 17` ⇔ 17:00 ≤ t < 18:00. Window [13:00, 18:00). "Most" = s_i > 0.5. | Correct |
| ε² for Kruskal–Wallis | ε² = H/(n − 1) | Equals the rank-based E²_R = H / ((n² − 1)/(n + 1)). I verified numerically (0.01930 both ways). Distinct from η²_H = (H − k + 1)/(n − k) = 0.008. | Correct; cite the source (m10) |
| Wilson intervals | 95% Wilson | `proportion_confint(method="wilson")`. I reproduced e.g. 117/168 → 62.3–76.1 and 5/73 → 3.0–15.1. | Correct |
| Cramér's V | Effect size for χ² | √(χ² / (n·(min(r, c) − 1))), no continuity correction. Reproduced 0.083, 0.408, 0.261. | Correct (uncorrected V; fine) |
| Cliff's δ | Effect size for Mann–Whitney | (#(x > y) − #(x < y)) / (n·m). Reproduced 0.356 and 0.260. | Correct |
| Mantel–Haenszel | Pooled OR across LLM strata | `StratifiedTable` on 2×2 tables ordered [ignore 1, 0] × [key 1, 0]. The OR is odds(key \| ignore) / odds(key \| no ignore), with the Robins–Breslow–Greenland CI. | Correct; stratifier choice (m11) |
| Holm | Family of three `AGENTS.md` tests | `multipletests(method="holm")` on two Mann–Whitney tests and one χ². Reproduced. | Correct |
| Wilcoxon signed-rank | Per-repository medians, paired | `scipy.stats.wilcoxon` drops 2 zero differences; normal approximation. The test is correct, but "median signed commit" is mislabelled and no effect size is given. | Test correct; **label wrong** (M2) |
| "95% CI" on share of repositories where signed is larger | Wilson on 131/217 | Correct as a descriptive interval. It is a sign-test proportion, not a CI for the size difference; say so. | Acceptable |
| Logistic OR (tests \| AGENTS.md, log1p commits) | 3.51 (1.99–6.17) | Reproduced. | Correct |
| Census stance (l. 174) | Intervals describe the data-generating process | Coherent, and cites Baltes & Ralph. | Fine |

No equation is wrong. One statistic is mislabelled (the commit-size medians), and one bound statement (the threat model) is logically inconsistent.

---

## 8. Reproducibility and privacy check

**Reproducibility.**
- `reproduce_public.py` writes nothing (read-only on `facts_paper.json` and two CSVs). I ran it: **17/17 PASS**. `sha256sum -c SHA256SUMS`: all OK.
- The public files agree with the current private data on every shared column (31,955 commits; kinds 3,503 / 332 / 99 / 12 / 7 / 26 bot; identical added and deleted sums; identical subject scripts).
- **Gaps:**
  - no `mentions_codex`, `mentions_claude` or `code_lines`, so the new analyses cannot be reproduced;
  - `arxiv_paper_all/` is untracked;
  - the committed `src/` is behind the data-generating versions;
  - no pinned environment;
  - track labels depend on a private table, although the public `track` / `track_source` columns suffice to recompute Table 3 (I did so).
- `recompute_core.py` shares no code with `build_repo_table.py`: it uses `git log --branches --shortstat` and re-derives the template rule. Its result file matches (3,649 / 3,649 / 3,649). It writes only `recompute_core_result.json`. I did not run it.

**Privacy of `public_data_generated/`.**
- No 40-hex SHAs, e-mail addresses, `hack-` names or URLs in `repositories.csv`, `commits.csv` or `aggregates/`. The only names and SHAs are in `recollection.csv`, by design.
- **No column flags credentials.** No `env_file_committed`, no per-repository finding. `gitignore_covers_env`, `env_example` and `llm_sdks` are released. With the aggregates they allow no per-repository inference: the published strata are only percentages. The smallest credential cells (Stripe 1, Telegram 2) cannot be linked to features. The 5 signed key commits (Claude 2, Codex 2, Cursor 1) point at best to the 16 repositories with Cursor signatures, which does not identify anyone.
- **Re-identification is trivial, as the data card concedes.** 806 of 1,057 active repositories are unique on four coarse columns, and `recollection.csv` hands a reader the full list to recompute them. Acceptable for public repositories if described as pseudonymisation. Fix the "cannot be joined" wording.
- `commits.csv` gives commit times to 0.01 min plus added and deleted lines per commit, so it links to GitHub trivially. Same comment.
- Authors are ordinal within each repository, from a salted hash whose salt is never saved. `author_key` is not released. Fine.
- **Key operational risk:** the release (credential aggregates plus the complete repository list) is committed at HEAD 3e86089 while disclosure to the organisers is pending (l. 309). Do not push, or post the preprint, until the organisers have been told and the 30 HEAD-present strings have been reported for revocation.

---

## 9. Remaining overclaims: quotes and rewrites

1. l. 137. "As a fourth channel, independent of the traces, we record whether the README names Codex or Claude, which we treat as a self-report of use." → "As a fourth channel, we record whether the README text contains 'Codex' or 'Claude'. We treat this as a partial self-report that is not independent of the traces: agents may write READMEs, READMEs may list context files, and 'Claude' may name the product's model."
2. l. 65. "using README self-reports as an independent reference" → "using README mentions as a partial reference".
3. l. 211. "The README self-reports, an exploratory addition, show how much the traces miss" → "The README mentions, an exploratory addition, give a partial reference".
4. l. 48 and 63. Keep "69.6% of those whose README named it", and add in the Results that 259 of the 490 detections rest on `AGENTS.md` alone (Codex-specific lower bracket 35.0%).
5. l. 220. "the median signed commit changed 240 lines and the median other commit 202" → "the median over repositories of the per-repository median was 240 lines for signed and 202 for other commits (pooled medians 119 and 109)". Add the effect size and the ≥ 3-signed-commit sensitivity (p = 0.80).
6. l. 282. "The larger size of agent-signed commits agrees with their finding ... here within the same repositories and in a setting where the tool was not chosen freely." → "Within repositories, commits carrying an agent signature (89% of them from Claude Code, which was not required) were somewhat larger than unsigned commits. The unsigned commits may include Codex work, and the difference disappears when at least three signed commits per repository are required. This is weaker support for the finding of Robbes et al. than a like-for-like comparison would give."
7. l. 282. "would have missed about half of the use of the required tool" → "would have classified about half of the active repositories as showing no Codex use".
8. l. 282. "make it possible to size it" → "make it possible to bound it under stated assumptions".
9. l. 273 and 285. "not through agent-signed commits or missing ignore rules" / "neither agent-signed commits nor missing ignore rules explain them" → "Most key strings sat in committed `.env.example` templates, which ignore rules do not cover. The keys in `.env` files entered history while those files were not ignored. Few key-bearing commits carried an agent signature, although the required agent rarely signs."
10. l. 144. Replace the bound sentence as in M4.
11. l. 142. "whether the matched string was still present in the final state" → "whether a finding of the same rule remained in the same file in the final state".
12. l. 297. "the self-report and commit-size analyses were added after the analysis plan" → "the self-report analysis was added after the analysis plan, and the commit-size analysis was changed from the planned pooled comparison to a within-repository test (deviations #9 and #15)".
13. l. 304. "the organisers' own actions moved the activity rate by 19.2 percentage points" → "whether the organisers' archived and batch repositories are counted changes the activity rate by 19.2 percentage points".
14. l. 121. "the rest were archived before the event began" → "446 had been archived before the event began, and 2 later that evening".

## 10. Recommended fixes, in priority order

1. **Before posting:** complete disclosure to the organisers (l. 309) and hold `git push` of the release until then. Remove or resolve every `\pending{}`.
2. **Self-report channel (M1):** clean the regex (prose only; exclude `CLAUDE.md`, `.claude`, model names, URLs). Rerun, and drop "independent". Report P(mention | trace) and P(mention | no trace), the Anthropic-SDK overlap (19/81), and the denominator. For the journal version, hand-code the mentions.
3. **Commit size (M2):** fix the label, add the effect size and the robustness table (≥ 3 signed, per kind, window-only), and rewrite or remove the Robbes comparison. Update `deviations.md` #9 and add the self-report analysis as #15.
4. **Trace specificity (M3):** report the Codex bracket 35.0–46.4% (`AGENTS.md`-only detections), the channel breakdown of Codex signatures (77% account-only), and a manual check of all 41 account-only Codex repositories and the 13 Claude account commits. Report literal `codex*` branch counts, or restrict the rule.
5. **Credential text (M4):** fix the route claims, the bound sentence, the `in_head` wording, the units (findings vs commits) and the date basis. Ask the organisers whether they issued keys.
6. **Release (M5):** add `mentions_codex`, `mentions_claude` and `code_lines` to the public files. Extend `reproduce_public.py` to every abstract and conclusion number. Commit `arxiv_paper_all/` and the current `src/`. Pin the environment and tool versions. Fix the DATA_CARD title and the "cannot be joined" wording.
7. **Minor items** m1–m12.
8. **Journal version:** README-language labels with two raters, a hand check of the 127 provider findings, double-coded tracks, the HackRep baseline, and the pre-registered jury analysis.
