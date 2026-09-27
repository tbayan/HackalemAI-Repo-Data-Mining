# Round 2, Reviewer 3: assessment for MDPI Big Data and Cognitive Computing (BDCC)

**Manuscript:** "Measuring AI Coding Agent Use from Repository Traces: Evidence from a Hackathon Where Codex Was Required" (v3, `latex/main.tex`, 318 lines; `main.pdf` built 27 Sep 2026 11:33, 15 pages).
**Reviewer profile:** academic editor and frequent reviewer for BDCC; also reviews for Expert Systems with Applications and IEEE Access. Areas: AI systems, human–AI interaction, large-scale data studies. Independent of the round-1 reviewers.
**How I checked:**
- I read `main.tex`, the rendered PDF (every page as an image, with Figs 1, 2 and 4 at higher resolution), the round-1 reviews, the editor's synthesis, the response, v2, `deviations.md`, `analysis_plan.md`, the relevant parts of `run_analysis.py`, `src/readme_features.py` and `src/scan_secrets.py`, the data card and the literature notes.
- I recomputed 40 numbers independently from `public_data_generated/` with my own script (`scratchpad/r3/recheck.py`), and I ran `reproduce_public.py` (17/17 PASS).
- I did not open `data/secrets_private/`, any `.env` file or the README language sample.
- Line numbers (l.) refer to `latex/main.tex`, where each paragraph is one line. Page numbers (p.) refer to the PDF.

---

## 1. Summary

The paper studies the 3,649 public repositories that the organisers of HackAlem AI (Astana, 23 September 2026) created for registered teams before a five-hour event at which every team had to use OpenAI Codex. The author mirrored every repository and answers four questions:
- **RQ1, participation.** 446 repositories were archived before the event, and a batch of 1,040 was created the evening before. The activity rate is 29.0% of all repositories, 33.0% of the open ones and 48.2% of those open and not in the batch.
- **RQ2, work timing and agent traces.**
  - The median team made 30.8% of its window commits in the last hour.
  - A Codex trace (AGENTS.md, a `codex` branch or a signature) appears in 46.4% of active repositories, and in 69.6% of those whose README names Codex.
  - A Claude Code trace appears in 24.9%.
- **RQ3, artefacts and documentation.** Test files appear in 87.0% of active repositories, and 88.1% of READMEs are in Russian.
- **RQ4, credentials.** Strings in the OpenAI key format appear in the history of 61 repositories, mostly in environment files.

The thesis is that repository-based measures of agent use depend on how the population was formed and on tool defaults.

v3 is a clear improvement on v1:
- The false sentences are gone.
- The funnel now includes the pre-event archive.
- Denominators are mostly unified.
- The data release exists and reproduces.
- The structure is a conventional research article, as the author wants.
- The writing is plain, and the banned-word lint passes (0 hits).

Every number I recomputed from the public files matches `facts_paper.json`.

The paper's core scientific claim is new: it measures what trace heuristics recover when the intended tool is known. That claim is now its selling point for an AI journal, but its evidence has three weaknesses that v3 introduced or left open:
1. The README self-report used as the reference is not independent of the traces. The matching regex runs on raw README text, so "CLAUDE.md" counts as naming Claude. The self-report is also unvalidated and cannot be reproduced from the public files.
2. More than half of the Codex detections rest on `AGENTS.md` alone, a file that other agents also read and write. The paper runs no sensitivity analysis for this.
3. The paper contrasts "Codex seldom signs" with "Claude signs by default", but gives no source for Codex's default attribution behaviour at the event date.

The credential conclusions also contradict the paper's own measurement finding. Several descriptions of commit-level statistics use a different denominator from the one stated. The file of deviations from the plan was not updated for v3.

## 2. Decision

| Target | Decision | Condition |
|---|---|---|
| **MDPI BDCC** | **Major revision** | Fix major issues MJ1–MJ6 and the MDPI back matter (MJ9). Add at least one analysis that gives the AI-measurement contribution a quantitative estimate (suggestions S1–S2) and a human–AI angle (S4). |
| **arXiv preprint** | **Minor revision; do not post the current build** | Seven `pending` markers still render in the PDF (orange text on pp. 5, 11 and 12). Several things must happen before posting: tell the organisers about the credentials; finish the README-language labels or remove that row; commit the release files; and fix the sentence-level problems in MJ1–MJ6 (mostly rewording). As round 1 recommended, post after the 1 October awards. |

---

## 3. Were the round-1 major issues resolved?

Status: **R** = resolved, **P** = partly resolved, **N** = not resolved.

### Reviewer 1 (methods)

| # | Issue | Status | Evidence in v3 |
|---|---|---|---|
| M1 | 446 repositories archived before the event | **R** | Its own funnel stage (l. 132, 181; Fig. 2a); RQ1 rerun on open repositories (l. 183). Residual: l. 181 says "three bulk operations", but the 17 September cluster spans 12:10–18:32 (`prearchived.clusters.sep17`), which is not one operation. l. 121 says "the rest were archived before the event", but 3,649 − 3,201 = 448, of which 446 were archived before the event; the other 2 were archived on the event day outside the wave. |
| M2 | "Complete population of registrations" | **R** | "Organiser-created repositories" (l. 72, 181); the repository → registration mapping and creation date as a proxy are stated as assumptions (l. 132); author identities are compared with reported participants (l. 185). The applications/seats reconciliation is left to Table 1 without a sentence; that is acceptable. |
| M3 | False headline sentences | **R** | The abstract (l. 48) and Conclusion (l. 304) now match the facts (46.4 < half; 69.6 < three quarters; 24.9 ≈ a quarter). |
| M4 | Weak clusters | **R** | Labelled exploratory, compared with a null model (0.30 vs 0.19), Rousseeuw cited (l. 198); histogram in Fig. 3b. Bootstrap stability and a minimum-commit filter are not reported (minor). |
| M5 | Fragile RQ1 inference; census inference | **R** | Categorical χ² on open, non-batch repositories, χ²(3) = 14.9, V = 0.08 (l. 183); census stance and test families (l. 174); Kruskal–Wallis with df and ε² (l. 235). Not stated: the test uses n = 2,161, not 2,163, because the 2 repositories created on 23 September are dropped. |
| M6 | README language rule | **P** | The rule is fixed (l. 139), the denominator is unified to 1,033 written READMEs (l. 132, 233) and "run instructions" is defined (l. 139). **The accuracy check is still pending** (Table 2 last row, l. 168; l. 295): 0 of 81 labels are done (`validation.readme_sample.labelled = 0`). |
| M7 | Circular or unsupported validation | **R** | Marker row removed; independent recount reported (Table 2, l. 161; `checks/recompute_core.py`); the earlier table is called a consistency check (l. 164); PR-only commits reported (l. 150). Residual: the rule that selected the 402 audited repositories is not stated (l. 150). |
| M8 | Credential analysis | **P** | Done: the placeholder filter is described and the stored fields are stated (l. 142), the MH stratification is reported (l. 273), recall limits are stated (l. 144), and the analysis is labelled exploratory.<br>Not done: the hand check of the 127 findings (acknowledged at l. 295).<br>`in_head` still matches on (rule, file), not on the string (`src/scan_secrets.py:70`), yet l. 264 says "the string is still present".<br>Which timestamp Gitleaks reports is still not stated (l. 264).<br>Disclosure is still `pending` (l. 309). |
| M9 | Agent-trace constructs | **P** | PR references are now a workflow trace (l. 137, 209); generic bots are excluded (l. 137); there is a per-tool matrix and overlap (l. 209, Fig. 4); the Claude traces are framed as a lower bound (l. 282).<br>Residual: `AGENTS.md` is counted as a Codex trace although l. 137 concedes that other agents read it, and there is no sensitivity analysis (see MJ2). Whether vendored folders are excluded when searching for context files "at any depth" is not stated. |
| M10 | Plan wording, deviations, exploratory labels | **P** | The wording at l. 174 is fixed and `deviations.md` exists. **But `deviations.md` is stale for v3.** Item 9 says commit size by signature was "Dropped", yet v3 reports it (l. 174, 220). The README self-report analysis, new in v3, is not listed. The planned `AGENTS.md` tests (plan, RQ4, Holm) are called "exploratory" at l. 220 (see MJ5). |
| M11 | Data release not met | **P** | `public_data_generated/` is committed, with a data card, checksums and random IDs, and `reproduce_public.py` gives 17/17 (I re-ran it). **But** `arxiv_paper_all/` is untracked in git. That directory holds the analysis plan, deviations, `run_analysis.py`, `reproduce_public.py` and `recompute_core.py`. `src/readme_features.py` and `src/extract_commits.py` have uncommitted edits. There is still no DOI (l. 311). So l. 174, l. 297 and l. 311 ("released") are not yet true. |
| M12 | Track labels | **P** | Agreement is reported (933/946, κ = 0.98; l. 147, Table 2) and the caption states where the labels come from (l. 239). Not done: double-coding (journal); the 34 unclear repositories that have a decisive keyword label (`tracks_kw.unclear_with_kw`) are not mentioned; the "earlier per-repository table" is still not cited (l. 147). |
| Cit. | Citation wording | **P** | Most items are fixed: Ziegler, Liang, Agarwal, Basak ESEM, Saghi, Baumann, "consistent with" and the five-hour window.<br>Still off:<br>• l. 282 cites AIDev as an estimate that "relies on signatures", but R1 noted that AIDev also uses branch prefixes and PR metadata.<br>• `prana2019readme` still renders as 2018 (reference [55]).<br>• l. 83 (Gloaguen): "lowered task success on average" is stronger than the abstract, which says context files "do not generally improve task success rates, while increasing inference cost by over 20%". |

### Reviewer 2 (framing and presentation)

| # | Issue | Status | Evidence in v3 |
|---|---|---|---|
| M1 | Factual overstatements | **R** (old ones) | The cluster, "all five hours" and "Russian and English" claims are gone. New overstatements appear in the credential and commit-size discussion (MJ4, MJ6). |
| M2 | No thesis; flat RQs | **P** | Four RQs in prose (l. 61), and the abstract's last sentence states the thesis. The Introduction no longer has an explicit thesis sentence: v2 had "Our argument is that …" and v3 removed it. RQ2 bundles two questions, work timing (5.2) and traces (5.3), so five Results subsections serve four RQs, and Fig. 1 shows four analyses without RQ labels. |
| M3 | Inconsistent denominators | **P** | Active repositories and written READMEs are used throughout the product measures, and Fig. 2a no longer shows the 27.0%.<br>Remaining:<br>• commit-level shares use all 31,955 team commits of 1,254 repositories (l. 209, 220);<br>• README mentions use 1,057 (l. 211), although l. 132 says README measures use 1,033;<br>• l. 264 "36 of them (3.4%)";<br>• l. 273 "73 commits" (see MJ4 and MJ6). |
| M4 | Registration framing | **R** | l. 132, 181. |
| M5 | Closest work missing | **R** | Robbes et al. (TOSEM, MSR 2026) are cited and discussed (l. 83, 282). |
| M6 | No baseline | **P** | The comparative words are mostly gone, but "READMEs were long" (l. 233), "a long README" (l. 235) and "long READMEs" (l. 285) remain without a baseline. The baseline itself is deferred to the journal version. |
| M7 | Discussion restates Results | **R** | Three themes plus implications, with a comparison against Robbes et al. (l. 279–288). No quantitative comparison with Meli et al. or with Chatlatanagulchai et al. on `AGENTS.md` prevalence (minor). |
| M8 | Number-heavy prose; CIs | **P, regressed** | Key shares carry CIs. The answer table (v2 Table 4) was removed in v3 to meet the author's "not Q&A" requirement, and nothing replaced it. Results paragraphs now carry 15–25 numbers each (l. 181, 183, 196, 209, 211, 220, 273). See MJ7 and S3 for a conventional fix. |
| M9 | Undisclosed deviations; clusters | **P** | Clusters resolved. Deviations stale (see R1-M10). |
| M10 | Placeholders; Fig. 1 claim | **P** | The Fig. 1 claim is now true (the recount exists) and the affiliation is filled. **Seven `\pending` markers remain:** l. 168, 295, 309 (two), 311 (two), 313. The response says Fig. 1 carries "units and n per RQ"; the v3 figure does not. |
| M11 | Agent use underclaimed | **R** | Lower bound on the non-required tool (l. 282). |
| M12 | Speculative security wording | **P** | The tests were run (MH OR, signed key commits), but the text now overclaims in the other direction: "not through agent-signed commits or missing ignore rules" (l. 63, 273, 285). See MJ4. |
| Fig. | Colour semantics | **P** | Figs 2–6 follow the colour rule in the style guide. Fig. 1 uses orange for its extraction boxes, while orange means Claude Code in Fig. 4. See §6.5. |
| Style | AI-feel patterns | **P** | Much reduced. A few short verdict sentences remain, such as l. 279 "The lesson for research is general." and l. 198 "The teams form a continuum rather than types." |
| Venue | Abstract ≤ 200 words | **R** | 199 words by `pdftotext`, so there is no room to add qualifiers without cutting elsewhere. |

**Round-1 items not fully resolved:**
- R1: M6, M8, M9, M10, M11, M12 and the citation wording.
- R2: M2, M3, M6, M8, M9, M10, M12, plus the Fig. 1 colours.

---

## 4. Fresh assessment for BDCC

**Significance and novelty.** BDCC's readers care about how AI use is measured at scale. Most evidence on coding-agent adoption comes from trace mining (AIDev; Robbes et al.), and this paper checks those traces in one of the few settings where the intended tool is known. That is a new and useful contribution, and it should be the paper's centre.

The other three contributions carry less weight for BDCC:
- Participation on a known denominator is a mining-methods point.
- Artefact prevalence is descriptive, with no baseline.
- Credentials are a secondary finding.

The "big data" scale is modest: 3,649 repositories and 31,955 commits. The "cognitive computing and human–AI interaction" angle is limited to the Claude-under-a-Codex-rule finding. To convince a BDCC editor, the paper should:
- put a quantitative estimate on trace recall that does not assume full compliance (S2);
- show how tool use relates to how teams worked (S4).

**Thesis.** The abstract states it (l. 48, last sentence) and the Conclusion restates it (l. 304). The Introduction implies it but never states it. Add one sentence at the end of l. 59 or l. 61: "We use this setting to test how much of the required agent's use repository traces recover, and how the way the population was formed changes participation rates."

**Abstract and Introduction.** The abstract has a clear motivation, gap, setting and results, and it is within the limit. Two changes are needed:
1. "and in 69.6% of those whose README named it" should say that this is an exploratory, selected subgroup.
2. "its commits were seldom signed, whereas Claude Code … signs commits by default" implies a documented default for Codex, which the paper does not have (MJ3).

The Introduction motivates the work well (l. 55–59). Its fourth paragraph (l. 63) previews results that later need qualification (MJ4). The contributions paragraph (l. 65) claims more than the paper shows in three places (§6.1).

**Structure.** The structure is conventional and coherent: Introduction, Background, Setting, Methodology, Results, Discussion, Threats, Conclusion, Declarations. This meets the author's requirement. Itemisation is gone. No paragraph is too short, except §2.5 (two sentences) and "External validity" (two sentences), which are acceptable.

**Contributions.**
- C1 (known denominator) is supported.
- C2 (what traces recover) is supported only under assumptions the paper does not state in the contribution: compliance, `AGENTS.md` as a Codex trace, and self-report as a reference.
- C3 is descriptive and supported.
- C4 claims more reproducibility than the release provides (§6.1).

---

## 5. Major issues

### MJ1. The README self-report is not independent of the traces, is unvalidated and cannot be reproduced from the public files
**Location:** l. 65 (C2: "an independent reference"), l. 137 ("As a fourth channel, independent of the traces"), l. 211, l. 282; abstract l. 48; Fig. 4b.

**Problem:**
- *How mentions are detected.* `src/readme_features.py:49–50, 92–93` sets `mentions_codex` and `mentions_claude` by searching the whole raw README with `\bcodex\b` and `\bclaude\b`. That text includes code blocks, file trees, links and paths.
- *Coupling with the file trace.* `\bclaude\b` matches "CLAUDE.md" and ".claude/", because "." is a word boundary. A README that lists the repository's files therefore "names Claude" whenever it contains the very file that counts as a Claude trace. This inflates `file_given_mention` (48.1%) and `trace_given_mention` (77.8%) by construction.
- *Coupling with the branch trace.* `\bcodex\b` matches `codex/…` branch names and paths in README commands, which couples the mention to the branch trace.
- *A second meaning of "Claude".* It also names the model an application calls: 31 active repositories use the Anthropic SDK or API (`llm_providers.Anthropic`). Such a mention is not a report of using the coding tool.
- *Selection.* The 168 repositories that name Codex are a selected 15.9% of active repositories, probably teams that used Codex heavily. Recall inside this group should not be read as recall of trace mining in general. l. 211 ("show how much the traces miss") and l. 282 ("make it possible to size it") read it that way.
- *Reproducibility.* The public `repositories.csv` has only `readme_mentions_agent_tool`, not the two per-tool flags. So the 69.6% in the abstract, and the 51.2%, 58.0% and 7.7%, cannot be recomputed from the public files, although C4 says the headline results can.
- The same regex issue affects Fig. 5's "Mentions a coding agent" (24.9%). `\bcursor\b` and `\bcopilot\b` on raw text match CSS `cursor:` and database cursors inside code blocks.

**Fix:**
- Restrict mentions to prose (outside code blocks, links and file trees).
- Exclude tokens that are themselves traces: `CLAUDE.md`, `.claude/`, `AGENTS.md`, `codex/…` paths.
- Exclude model and API names (for example `claude-3…`, `anthropic` in configuration examples).
- Double-code all 168 + 81 mentions for "reports using the tool to build this repository" and report κ.
- Report recall under both definitions.
- Release the per-tool mention flags.
- In C2 and l. 137, call the README "a second, imperfect reference" and state the selection.
- Drop "Mentions a coding agent" from Fig. 5, or fix it.

### MJ2. More than half of the Codex detections rest on `AGENTS.md` alone, with no sensitivity analysis
**Location:** l. 137, 209, 282; abstract l. 48; Fig. 4.

**Problem:** l. 137 concedes that other agents read `AGENTS.md`, but the analysis counts it as a Codex trace (`run_analysis.py`, `tools = {"codex": "agents_md", …}`). From the public data I computed:
- Of the 490 Codex-detected active repositories, **259 are detected by `AGENTS.md` alone**.
- Codex-specific traces (a `codex` branch or a Codex signature) appear in only **231 active repositories (21.9%)**.
- `AGENTS.md` is present in **59.7%** of repositories with a Claude Code trace, against **24.6%** of the rest.
- **61** repositories have `AGENTS.md` and a Claude signature but no Codex branch or signature.

The headline 46.4% therefore mixes a tool-specific measure with a shared one.

The direction of the bias matters for the thesis. If some `AGENTS.md` files come from other tools, Codex recall is lower than stated, which strengthens the claim that traces miss. The paper should still show both numbers.

**Fix:**
- Report Codex detection with and without `AGENTS.md` (a row in Fig. 4a and one sentence in the text).
- Call `AGENTS.md` a "shared context file".
- Discuss the 61 repositories.
- Say in Threats that the Codex trace is an upper bound in this respect.

### MJ3. The paper contrasts Codex's and Claude's signing defaults without documenting Codex's default
**Location:** abstract l. 48; l. 57, 63, 282 ("The loss is tool-specific"); Conclusion l. 304.

**Problem:**
- Claude Code's default is cited to the vendor's settings reference [21]. Codex's behaviour is only inferred from the data.
- The `openai/codex` repository shows a configurable `commit_attribution` option introduced in 2026:
  - PR #11617, "Use prompt-based co-author attribution with config override";
  - issue #19799, which asks whether the Codex trailer is on by default and whether it depends on the `codex_git_commit` feature flag.
- The paper does not say which Codex surface teams used (CLI, IDE extension or cloud) or which versions were current on 23 September.
- The 332 Codex-signed commits show that Codex did sign in some cases.

**Fix:**
- *To find:* the official Codex documentation of commit attribution in force on 23 September 2026, for each surface. Cite it as grey literature with an access date, as for [21].
- If none exists, say so.
- Word the contrast as observed behaviour ("Codex commits rarely carried a signature in this event") rather than a default.
- Add the unknown surface and version to Threats.

### MJ4. The credential conclusions contradict the paper's own measurement finding, and three descriptions are wrong
**Location:** l. 63, 264, 273, 285, 288.

**Problems:**
- *"Not tied to agents" (l. 273), "not through agent-signed commits" (l. 63, 273), "neither agent-signed commits … explain them" (l. 285).*
  - The paper's central finding is that the required agent rarely signs: signatures reveal Codex in 7.7% of the repositories that name it.
  - An unsigned key commit therefore says little about whether an agent wrote it.
  - Five key commits were signed.
- *"Not through … missing ignore rules" (l. 273, 285).*
  - 27 of the 77 OpenAI findings are in `.env` files. A committed `.env` means the ignore rule was missing, or was bypassed, when the key was committed.
  - `.gitignore` coverage is measured at the final state, not at the commit.
  - The MH odds ratio has a wide interval (0.45–2.37).
  - "No evidence of an association" is supported. "Not through" is not.
- *Wrong descriptions:*
  1. **"5 of the 73 commits that added one"** (l. 273). The 73 are OpenAI *findings* that could be matched to a commit (`kc.sha.notna().sum()`; 4 of 77 were not matched). They are not distinct commits, and one commit can hold several findings. The number 73 also collides with the 73 repositories that have provider findings in the same section.
  2. **"in 36 of them (3.4%) the string is still present"** (l. 264). 3.4% is 36 of 1,057 active repositories. As a share "of them" it is 36 of 73 = 49.3%. Also, `in_head` checks that the same rule fires in the same file at HEAD, not that the same string is present.
  3. **".env.example: 32 findings"** (l. 273, Fig. 6b). The code counts any file ending in `.example` (`\.env\.example$|\.example$`).
- *Unstated presupposition.* l. 285 ("short-lived keys issued for the event") and l. 288 ("keys issued for an event") assume the organisers issued API keys or credits. The paper never establishes this.

**Fix (rewrites):**
- l. 273: "Of the 77 OpenAI findings, 73 could be matched to a team commit, and 5 of these (6.8%) were in agent-signed commits, against 9.0% of window commits in the same repositories. Because Codex commits rarely carry a signature, this does not show that agents were not involved."
- l. 273, last sentence: "Exposure thus came mainly through committed template and environment files during the event; we found no association with agent signatures or with `.gitignore` coverage at the final state."
- l. 264: "…and 36 of them (49.3%) still hold a string of the same format in the same file in the final version."
- l. 285: replace "a route that simple measures would have closed" with "a route that standard measures target", and state whether the organisers distributed keys or credits.

### MJ5. The status of the analyses is mislabelled, and the deviations file is stale for v3
**Location:** l. 174, 211, 220, 297; `analysis/deviations.md`; `analysis/analysis_plan.md`.

**Problem:**
- The plan (RQ4) specified the three `AGENTS.md` comparisons with Holm correction. They are planned, not exploratory. Yet l. 220 opens "In a second exploratory comparison". The code comment at `run_analysis.py:325` wrongly says "exploratory in the plan".
- Conversely, `deviations.md` item 9 says commit size by signature was "Dropped (v2)", but v3 reports it with a Wilcoxon test (l. 174, 220).
- The README self-report is new in v3 and is the basis of C2 and an abstract number. It is not listed as a deviation.
- l. 297 says the commit-size analysis was "added after the analysis plan", but the plan lists commit size as exploratory. What was added is the within-repository Wilcoxon test.
- l. 174 says the plan and deviations "are released with the data", but `arxiv_paper_all/` is untracked in git (see R1-M11).

**Fix:**
- Update `deviations.md` for v3 (self-report added; commit size reinstated with the lock-file exclusion and the within-repository test).
- Call the `AGENTS.md` tests planned, and label only the adjusted odds ratio as added.
- Correct l. 297.
- Commit and push `arxiv_paper_all/analysis/` and `checks/`, or state that they will be released.

### MJ6. Commit-level statistics use denominators or summaries other than the ones described
**Location:** l. 132 vs l. 209 and 220; l. 282.

**Problem:**
- l. 132 says commit measures use the active repositories' team commits in the window "unless stated otherwise".
- **Signed commits (l. 209).** "Of all team commits, 3,953 (12.4%)" covers all 31,955 team commits of the 1,254 repositories with any team commit, at any time. For active repositories in the window the figure is 3,541 of 30,418 (11.6%).
- **Conventional commits (l. 220).** "48.5% against 42.1% of non-merge commits" also covers all repositories and all times (3,746 and 23,025 commits). On window commits of active repositories I get 48.7% against 43.1%, so the conclusion holds, but the text should use the stated denominator.
- **Commit size (l. 220).** "The median signed commit changed 240 lines" is the median across 217 repositories of each repository's median. It is computed over all non-merge commits of active repositories, not only window commits.
- **The Discussion (l. 282)** says the size result holds "in a setting where the tool was not chosen freely". But 3,503 of the 3,953 signed commits (88.6%) name Claude Code, which teams chose freely. The sentence contradicts the data.

**Fix:**
- Use window commits of active repositories, or state the other denominator in the sentence.
- l. 220: "…the median of the repositories' median signed-commit sizes was 240 lines, against 202 for other commits."
- Say that most signed commits are Claude Code commits, and delete "in a setting where the tool was not chosen freely".

### MJ7. With the answer table gone, the Results are hard to read
**Location:** l. 181 (about 20 numbers), 183 (18), 196 (22), 209 (25), 211 (15), 220 (20), 273 (15).

**Problem:** Removing the Q&A devices meets the author's requirement, but the numbers they carried moved back into the prose. Most sentences list several shares in a row, which reads like a table written out as text. BDCC reviewers will ask for condensation.

**Fix:** See S3. Add a conventional "Key estimates" table and keep two or three numbers per sentence in the text.

### MJ8. Things that must happen before any posting
**Location:** l. 168, 295, 309, 311, 313; git status.

The README-language accuracy is pending (Table 2, l. 295), the credential disclosure is pending (l. 309), and so are the ethics statement (l. 309), the DOI and OSF link (l. 311) and the list of other AI tools (l. 313).

**Fix:**
- Complete the disclosure first, and delay posting until after 1 October, as round 1 advised.
- Finish the 81 labels, or remove the row and write "not yet validated".
- Commit the release.

### MJ9. Readiness for BDCC: framing and MDPI back matter
**Location:** Declarations, l. 307–313; title and keywords.

**Problem:**
- *Missing MDPI back-matter statements:* Author Contributions (CRediT), Funding, Institutional Review Board Statement (currently pending), Informed Consent Statement ("Not applicable", with the reason) and Conflicts of Interest.
- *Where the AI disclosure goes.* BDCC's instructions ask authors to disclose GenAI use (text, data, graphics, design, analysis) in the back matter. v3 has a "Use of AI tools" paragraph; it should move to Acknowledgments (or wherever the template places it) and be summarised once in Methods.
- *A perceived conflict.* The analysis and text were produced with Claude Code, one of the two tools the paper compares, and the paper finds that tool's default favourable to detection. This is not a conflict of interest in the formal sense, but an editor will notice it. Say it explicitly in the AI-use and COI statements, and say that the author fixed the trace definitions.
- *Recount independence.* The "independent recount" (Table 2) was written by the same agent. It shares no code with the pipeline but could share a misreading of a definition. Add this to Threats.
- *Keyword.* "credential leakage" (l. 50) conflicts with the paper's term "credential exposure".

---

## 6. Minor issues

### 6.1 Claims to calibrate (current text, then rewrite)

| l. | Current | Suggested |
|---|---|---|
| 55 | "in many real sessions the agent writes nearly all of the committed code" | "in 41% of the sessions in a public dataset of real agent sessions, the agent wrote virtually all committed code" (use a macro; SWE-chat abstract) |
| 57 | "and no study can tell how many such repositories it misses" | "and without an external reference a trace-based study cannot estimate how many such repositories it misses" |
| 59 | "Hackathons offer a setting in which both quantities can be fixed in advance." | "Some hackathons fix both quantities in advance." |
| 63 | "Keys reached the public history mainly through committed environment files, not through agent-signed commits." | "Keys reached the public history mainly through committed environment files." (see MJ4) |
| 65 | "using README self-reports as an independent reference" | "using README mentions of each tool as a second, imperfect reference" |
| 65 | "exposed credentials of agent-assisted prototypes" | "…of prototypes built under a rule that required a coding agent" (only 55.1% show any agent trace) |
| 65 | "the headline results can be recomputed from the public files alone" | "the headline numbers on population, work timing, traces and artefacts (17 checks) can be recomputed from the public files; the README-mention and credential results need the private stage" |
| 83 | "in a benchmark such files lowered task success on average" | "in a benchmark such files did not generally improve task success and raised inference cost by over 20%" |
| 121 | "and Section 5.1 shows that the rest were archived before the event began" | "and 446 of the remaining 448 had been archived before the event began (Section 5.1)" |
| 132 | "created between 18:00–20:00" | "created between 18:00 and 20:00" |
| 183 | "activity varied little with the creation date" | "activity differed by up to 11 percentage points between creation groups (V = 0.08)" |
| 185 | "most of the distance … comes from repositories that were closed or barely used before the event started" | "1,472 of the 2,592 inactive repositories (57%) were archived before the event or belonged to the evening batch" (the batch was not "used before the event"; use macros) |
| 196 | "The median team made its first window commit 61 minutes after the start, its last 9 minutes before the deadline, and 19 commits" | "Teams made their first window commit a median of 61 minutes after the start …" (three separate medians, not one team) |
| 211 | "show how much the traces miss" | "show how much the traces miss among teams that named the tool" |
| 220 | "In a second exploratory comparison" | "In the planned comparison (Holm-adjusted across three tests)" |
| 224 | "The most common frameworks were React (46.5%), FastAPI (43.2%), Vite (32.8%), Tailwind (21.2%) and Next.js (16.5%)." | Uvicorn (43.9%), pytest (39.6%), Pydantic (30.9%), NumPy (29.8%) and pandas (29.4%) are all more common than Tailwind and Next.js (`rq3.frameworks`). Name the category: "Among web front-end and API frameworks …; the most common Python libraries were …". R1 minor 27 is still open. |
| 233, 235, 285 | "READMEs were long", "a long README", "long READMEs" | "READMEs had a median of 1,645 words" (there is no baseline) |
| 235 | "most teams produced a Python or TypeScript application that called an LLM, with test files and a long README, mostly in Russian" | I computed the joint share: 537 of 1,057 (50.8%) combine Python or TypeScript, LLM use, test files and a Russian README. Say "about half combined all four". |
| 279 | "The lesson for research is general." | Delete, or: "This applies to any study that counts activity in organiser-created repositories." |
| 282 | "the trace heuristics used in adoption studies detected Codex" | "trace heuristics of the kind used in adoption studies detected Codex" (the paper implements its own set, not Robbes et al.'s) |
| 282 | "Adoption estimates that rely on signatures [2,3] will therefore favour tools that sign by default." | "Estimates that rely mainly on signatures would favour tools that sign by default." (AIDev combines several signals; see the R1 citation table) |
| 282 | "a known required tool and README self-reports make it possible to size it" | "…make it possible to bound it, if teams complied" |
| 282 | "…here within the same repositories and in a setting where the tool was not chosen freely" | Delete the second clause (MJ6). |
| 288 | "the measures above would reduce the exposure of keys issued for an event" | "the measures above could reduce the exposure of keys used at an event" |
| 304 | "the organisers' own actions moved the activity rate by 19.2 percentage points" | "counting or excluding the repositories that the organisers archived or created in a batch changes the activity rate from 29.0% to 48.2%" |

### 6.2 Readability and flow
- l. 181, 209 and 224 are lists written out as sentences (archive operations; tool overlaps and other agents; frameworks and artefacts). Move them to the key-estimates table (S3).
- l. 209 packs trace prevalence, overlap, other agents, commit shares and PR references into one paragraph. Split it: one paragraph for the Codex traces and one for Claude Code and the overlap. Send the other numbers to the table.
- l. 220 joins two unrelated analyses (commit form, and `AGENTS.md` versus activity) in one paragraph. Split them.
- §5.3 has no closing sentence, unlike §5.1, 5.2, 5.4 and 5.5. Add one summarising what the traces recover.
- §2.5 (two sentences) could close §2.2. It would also help to say how the "we found no … study" claim was checked; `facts.literature` records 120 searches and 66 screened works.

### 6.3 Terminology
Define each term once and use it everywhere, including the figures and keywords:
- *Units:* "active repository" (defined) against "team" (l. 196: "163 teams", "79.3% of teams", "the median team").
- *Time:* "event window" (defined) against "event-time work" (abstract).
- *Self-report:* "README self-report", "README mention" and "README names the tool" (l. 137, 211; Fig. 4).
- *Traces:* "agent trace" and "repository trace" (l. 137, 209) against "Codex trace".
- *Credentials:* "key strings", "keys", "credentials" and "strings matching … key formats" (l. 264–273); "credential exposure" (section title) against "credential leakage" (keywords).
- *Documents:* the data card's paper title differs from the v3 title.

### 6.4 Statistics and definitions
- l. 183: give n = 2,161 for the χ² test, and say that the 2 repositories created on 23 September are excluded.
- l. 183 and l. 279: the all-repository test merges the batch into "22 September" (n = 3,647). Say so, or it looks inconsistent with Fig. 2b's five groups.
- l. 150: state the rule that selected the 402 audited repositories.
- l. 139: state that README mentions are matched anywhere in the raw file (see MJ1).
- l. 142: for rules without a candidate pattern (curl headers, JWT), the placeholder filter scores the whole line. Say so.
- l. 137: state whether vendored folders (`node_modules`, `venv`) are excluded when searching for `AGENTS.md` "at any depth".
- l. 264: say whether Gitleaks' `Date` is the author or the committer date. The window is defined on committer time.
- Fig. 3b: the 45–50% bin dips and the 50–55% bin peaks. This comes from binning ratios with small denominators (1/2, 2/4 …). Use bins closed on the left at 50%, or add an ECDF.
- `first_commit_by_codex_branch` (58 vs 61 minutes, δ = −0.12) is computed but not reported. Report it or drop it.

### 6.5 Figures and tables

**Fig. 1** (p. 2; architecture in the Transformer-figure style). The pastel rounded blocks, the "×3,649" repetition label and the left-to-right flow resemble the target style. Six problems:
1. The dashed arrow to "Checks" starts from a stub just outside the top-right corner of "Feature tables" (`[xshift=4pt]feat.north east`). At print size it reads as a stray tick, and the Checks box almost touches the Population box.
2. "Process and agent traces" is wider than the other three analysis boxes, so their right edges do not line up. The dashed "Known in advance" arrow enters it from the right, against the flow.
3. "Per repository, ×3,649" includes "Secret scan", but Gitleaks ran on the 1,254 clones with team commits (l. 142).
4. Event facts feed only the "Known in advance" box. Yet the event window, taken from the press, defines "active" and so affects every analysis.
5. The core comparison of the paper is not drawn. Three trace channels and the README mention, set against the known required tool, are the analogue of the attention block in the Transformer figure.
6. The fill colours carry no data meaning, and orange (the extraction boxes) means Claude Code in Fig. 4, against the style guide's colour rule.

Suggested redesign:
- neutral grey blocks;
- blue for Codex and orange for Claude Code, only where the trace channels are drawn;
- the analysis boxes labelled RQ1–RQ4 with their n (3,649; 1,057; 1,057 and 1,033; 1,057).

**Fig. 2.**
- (a) The "Active in the event window" bar is coloured as "Open, not in batch", but 14 of the 1,057 are batch repositories.
- (b) The caption should say that the n labels refer to open repositories, and that the grey point is the batch.

**Fig. 3.** The caption lacks n (1,057) and the bin width.

**Fig. 4.**
- The legend sits inside panel (a) next to the "README names the tool" row (R2 flagged this in round 1).
- The caption does not define each trace per tool: `AGENTS.md` against `CLAUDE.md` or `.claude/`; branch prefix; signature types.
- Add the Codex-specific row (MJ2).

**Fig. 5.**
- Add group labels (Engineering, LLM, README).
- "Mentions a coding agent" is not discussed in the text and uses the regex in MJ1. Fix it or drop it.

**Fig. 6.** Fine. Rename ".env.example" to "*.example templates", or change the code (MJ4).

**Table 2.** The caption "Validation and sensitivity checks." is not self-contained. Say that the unit is repositories and what "equal" means.

**Table 3.**
- The Task column wraps to three lines, which makes the table tall. Use a two-line summary or a table note.
- Add a row for the 73 unmatched repositories (R2 minor 18).
- The Kazakh (%) column has per-track denominators (written READMEs) that are not given.
- Two tracks are named "Special"; give the partner-based name.

### 6.6 MDPI BDCC checklist for the journal version

| Item | Status |
|---|---|
| Abstract of about 200 words or fewer | 199: at the limit |
| Keywords (3–10) | 6; align "credential leakage" with "credential exposure" |
| Author Contributions (CRediT) | **missing** |
| Funding | **missing** |
| Institutional Review Board Statement | **pending** (l. 309) |
| Informed Consent Statement | **missing** ("Not applicable": public data, no interaction) |
| Data Availability Statement | present; **DOI pending** (l. 311) |
| Acknowledgments with the GenAI disclosure | AI use is disclosed in "Use of AI tools" (l. 313); move it to the template's place; "other AI tools" pending |
| Conflicts of Interest | **missing** (the non-affiliation sentence at l. 309 belongs here; see MJ9) |
| References | numbered natbib; convert to the MDPI template. 9 are arXiv-only; recheck them for published versions before submission. |
| Figures | vector PDFs; fine |

### 6.7 References
- [59] Ralph et al.: "Davide Taibi" appears twice in the author list (`references.bib`, l. 288). Check it against arXiv:2010.03525.
- [55] Prana et al.: the year renders as 2018, but the issue is EMSE 24(3), 2019 (R1 minor 50, not fixed).
- The "earlier per-repository table" (l. 147) should be cited as the author's prior public report (R2 minor 6, not fixed).

---

## 7. Checked numbers (facts file, my independent recomputation, and whether the sentence describes the number correctly)

"Recomputed" means I computed it from `public_data_generated/` with my own script. "Facts" means I checked it against `facts_paper.json` and the code, because it is not in the public files.

| # | Claim (l.) | Paper | Facts | My value | Denominator and description |
|---|---|---|---|---|---|
| 1 | Repositories (l. 48, 181) | 3,649 | 3,649 | 3,649 (recomputed) | PASS |
| 2 | Archived before the event (l. 48, 181) | 446 (12.2%) | 446 | 446 | PASS. "Three bulk operations" is loose: the 17 Sep cluster spans 12:10–18:32. |
| 3 | "the rest were archived before the event" (l. 121) | 3,649 − 3,201 = 448 | 446 | 446 | **FAIL-desc**: 2 open repositories were archived on the event day outside the wave. |
| 4 | Batch; batch active (l. 181) | 1,040; 14 (1.3%) | same | same | PASS |
| 5 | Active (l. 48, 183) | 1,057 (29.0%; 27.5–30.5) | same | 1,057 (29.0%) | PASS |
| 6 | Open and not in batch (l. 48, 183) | 48.2% (1,043 of 2,163) | same | 1,043 / 2,163 = 48.2% | PASS; the abstract's "the rest" = 2,163 is correct. |
| 7 | χ² open, not in batch (l. 183) | χ²(3) = 14.9, V = 0.08 | n = 2,161 | 14.9; df 3; n 2,161; V 0.08 | PASS; n ≠ 2,163 is not stated. |
| 8 | χ² all repositories (l. 279) | χ²(3) = 608.2, V = 0.41 | n = 3,647 | 608.2; V 0.41 | PASS; the batch is merged into 22 Sep, which is not stated. |
| 9 | "most of the gap" (l. 63, 185) | "most" | — | 1,472 of 2,592 = 56.8% | PASS (just); give the number. |
| 10 | Window commits; pooled last hour (l. 196) | 30,418; 28.8% | same | 30,418; 28.8% | PASS |
| 11 | Median last-hour share; majority (l. 196) | 30.8% (IQR 19.4–43.8); 163 (15.4%) | same | 30.8; 163 (15.4%) | PASS |
| 12 | Hours (l. 196) | ≥4: 79.3%; all 5: 44.5% | same | 79.3; 44.5 | PASS |
| 13 | Codex trace (l. 48, 209) | 490 (46.4%); file 33.3, branch 18.9, signature 4.4 | same | same | PASS as a number. **Construct:** 259 of the 490 rest on `AGENTS.md` alone; Codex-specific traces 231 (21.9%) (MJ2). |
| 14 | Claude Code trace (l. 209) | 24.9%; signature 16.9, file 14.2 | same | same | PASS |
| 15 | Overlap (l. 209) | 309 / 181 / 82 / 485 | same | same (sum 1,057) | PASS |
| 16 | Signed commits (l. 209) | 3,953 (12.4%); 3,503 Claude, 332 Codex | same | same | **FAIL-desc (denominator)**: all 31,955 team commits of 1,254 repositories at all times; window and active gives 3,541 / 30,418 = 11.6%. |
| 17 | PR references (l. 209) | 35.9%; 143 with a Codex branch | same | same | PASS |
| 18 | README names Codex; recall (l. 48, 211) | 168 (15.9%); 69.6% (62.3–76.1) | 117/168 | not in public data | PASS against the facts. **Construct** problems (MJ1). The denominator 1,057 differs from the README rule (1,033, l. 132). Not reproducible from the public files. |
| 19 | Trace or mention (l. 211) | 51.2% | 541/1,057 | n/a | PASS (facts) |
| 20 | Claude named; trace; signature (l. 211, 282) | 81; 77.8%; 58.0% | same | n/a | PASS (facts); coupled with `CLAUDE.md` by the regex (MJ1). |
| 21 | Commit size (l. 220) | "the median signed commit changed 240 lines", other 202; 60.4% of 217 | same | n/a | **FAIL-desc**: median of the repositories' medians, over all non-merge commits of active repositories (not window only). |
| 22 | Conventional commits (l. 220) | 48.5% vs 42.1% of non-merge commits | 1,817/3,746 vs 9,686/23,025 | same; window and active: 48.7 vs 43.1 | **FAIL-desc (denominator)**: all repositories and all times; the conclusion is unchanged. |
| 23 | `AGENTS.md` association (l. 220) | 28 vs 16; 5 vs 4; 95.7 vs 82.7%; OR 3.51 (1.99–6.17) | same | 28/16; 5/4; 95.7/82.7 | PASS as numbers; **mislabelled** "exploratory" (MJ5). |
| 24 | Tests; Python; Dockerfile, CI, deployment (l. 224) | 87.0 (920/1,057); 58.5; 33.3 / 14.3 / 6.2 | same | same | PASS |
| 25 | Frameworks (l. 224) | "most common: React, FastAPI, Vite, Tailwind, Next.js" | Uvicorn 43.9, pytest 39.6, Pydantic 30.9, NumPy 29.8, pandas 29.4 | n/a | **FAIL-desc**: the list omits more common entries. |
| 26 | README language and words (l. 233) | of 1,033: Ru 88.1, En 9.3, Kk 2.1, mixed 0.5; median 1,645 (1,049–2,413) | same | same | PASS (construct pending validation) |
| 27 | Language × track; Kruskal–Wallis (l. 235) | χ²(33) = 201.1, V = 0.26; H(11) = 19.0, p = 0.062, ε² = 0.02 | same | KW 19.0, p 0.062, ε² 0.02 | PASS |
| 28 | Joint product claim (l. 235) | "most teams produced …" | — | 537 / 1,057 = 50.8% | borderline PASS; soften |
| 29 | Provider findings (l. 264) | 127; 10 placeholders; 117 in 73 active (6.9%) | same | n/a | PASS (facts) |
| 30 | Still present (l. 264) | "36 of them (3.4%)" | 36/1,057 | 36/73 = 49.3% | **FAIL-desc**: the percentage uses 1,057, not "them"; `in_head` matches (rule, file), not the string. |
| 31 | OpenAI (l. 48, 264) | 77 findings in 61 repositories (5.8%); 30 final | same | n/a | PASS (facts) |
| 32 | Key commits signed (l. 273) | "5 of the 73 commits" (6.8%) vs 9.0% | matched findings = 73 | n/a | **FAIL-desc**: 73 = findings matched to a commit, not distinct commits. |
| 33 | `.gitignore`, `.env.example` (l. 273) | 83.6%, 74.3% | same | 83.6; 74.3 | PASS |
| 34 | Conclusion gap (l. 304) | 19.2 pp | 48.2 − 29.0 | 19.2 | PASS arithmetically; "moved" is causal wording. |

**Summary:** 34 claims checked (the task asked for at least 10). The numbers are exact everywhere. Eight sentences describe the statistic or its denominator incorrectly (rows 3, 16, 21, 22, 25, 30, 32 and, in construct terms, 13 and 18). No fabricated number was found.

---

## 8. Suggestions (feasible with the existing data)

**S1. Rebuild and validate the self-report reference.** This is required for C2.
- Re-extract README mentions from prose only, excluding trace tokens and model or API names (MJ1).
- Double-code all 249 mentions (168 Codex, 81 Claude) for "the team reports using this tool to build the repository" (κ), and report recall under the raw and cleaned definitions.
- Add the per-tool flags to `repositories.csv` and the self-report numbers to `reproduce_public.py`.
- Effort: small to medium.

**S2. Separate tool-specific from shared traces, and estimate undetected use with capture–recapture.**
- Report Codex detection for Codex-specific traces (branch or signature: 231, 21.9%) and with `AGENTS.md` (490, 46.4%).
- Then treat the four channels (context file, branch, signature, cleaned README mention) as four incomplete "lists" of the same repositories. Fit log-linear multiple-systems models to the incomplete 2⁴ table to estimate how many repositories used Codex but appear in no list. Report the model-selection and list-dependence assumptions, and a sensitivity analysis over plausible models.
  - Method: Fienberg, S. E. (1972). The multiple recapture census for closed populations and incomplete 2^k contingency tables. *Biometrika* 59(3), 591–603. DOI 10.1093/biomet/59.3.591 (verified in Crossref).
  - Use in software engineering: Briand, L. C., El Emam, K., Freimut, B., Laitenberger, O. (2000). A comprehensive evaluation of capture-recapture models for estimating software defect content. *IEEE TSE* 26(6), 518–540. DOI 10.1109/32.852741 (verified in Crossref).
- This turns "if all teams complied, about half was missed" into an estimate with an interval that does not assume compliance. It would give BDCC a method readers can reuse on other trace datasets.
- Effort: medium.

**S3. Add a "Key estimates" table and thin the Results prose.**
- One conventional table, not Q&A. Rows for population, timing, traces (per tool and channel), artefacts, documentation and credentials. Columns: measure, unit, n/N, %, 95% CI and figure.
- Keep two or three numbers per sentence in §5.1–5.5, and move the lists at l. 181, 209, 224 and 273 into the table.
- Put every commit-level measure on window commits of active repositories (MJ6).
- This restores what the v2 answer table did without the Q&A form.
- Effort: small.

**S4. Compare the tool-use profiles (the human–AI angle for BDCC).** Label this analysis exploratory.
- Compare the four trace groups (Codex only 309, both 181, Claude Code only 82, neither 485) on last-hour share, hours with commits, window commits, test files, README length, LLM use and credential findings (aggregate only), with effect sizes. Everything except the credential flags is in the public files.
- This tests whether the "neither" group looks like low activity or like silent agent use. That bears directly on the interpretation of the 53.6% non-detection.
- It also describes how teams that brought a non-required tool worked, which is the human–AI interaction finding BDCC readers will look for.
- Effort: small.

**S5. Rebuild the credential route at commit time.** This is private work, reported only in aggregate. For each OpenAI finding:
- Count distinct commits.
- Record whether `.gitignore` covered `.env` in that commit's tree.
- Record whether the file was `.env`, `.env.example` or another `*.example` file.
- Record whether the commit is reachable from a `codex/` branch or a PR reference.
- Check "still present" with a salted hash computed in memory, instead of (rule, file).

This either supports or removes the "not through missing ignore rules" and "not tied to agents" statements (MJ4). It also gives the security paragraph evidence at the level of the individual commit.

Effort: small to medium.

---

## 9. External sources consulted in this review
- MDPI, *Big Data and Cognitive Computing, Instructions for Authors*: https://www.mdpi.com/journal/BDCC/instructions. The page returned 403 to the fetcher; its content was read from search results.
- openai/codex PR #11617, "Use prompt-based co-author attribution with config override": https://github.com/openai/codex/pull/11617
- openai/codex issue #19799, "Clarify Codex commit co-author attribution behavior": https://github.com/openai/codex/issues/19799
- Crossref records for DOI 10.1093/biomet/59.3.591 and DOI 10.1109/32.852741.
