# Decision letter and revision plan (27 September 2026)

Inputs: `reviewer_1_methods.md` (methods, data audit, citation support), `reviewer_2_framing.md` (framing, writing, figures), `editor_assessment.md` (repository review, written before reading the reviews) and `../literature/reference_audit.md` (reference metadata audit). Every reviewer claim that changes a number or a conclusion was re-checked by the editor. The results of that check are in Section 2.

## 1. Decision

| Target | Reviewer 1 | Reviewer 2 | Editor |
|---|---|---|---|
| arXiv preprint | major revision (1–2 weeks, no new data) | minor revision, do not post current build | **Revise before posting.** Several sentences are false and one finding changes the RQ1 denominator. |
| Q1 journal | major revision (reject-and-resubmit at EMSE) | major revision (desk-reject risk at MAKE) | **Major revision.** The data are strong enough for Q1; the paper needs a thesis, fewer and sharper RQs, validated instruments, and a comparison or outcome variable. |

Neither reviewer found a fabricated number or a fabricated reference. Reviewer 1 recomputed 67 claims from the data: every number reproduces. The failures are in how sentences describe the numbers, in denominators, and in claims about validation and data release.

## 2. Reviewer claims re-checked by the editor

| Claim | Check | Result |
|---|---|---|
| 446 repositories were archived before the event | `repos.csv` `updated_at` < 13:00, 23 Sep; `pushed_at` never later | **Confirmed.** Bulk operations: 126 repositories on 15 Sep 18:30–18:32 (up to 69 per minute); 56 on 17 Sep; 242 on 22 Sep 20:01–20:05 (up to 73 per minute), minutes after the 1,040-repository batch was created; 22 others. None became active. Active share among the 3,203 repositories open during the event: **33.0%**. |
| Conclusion: "Most active teams worked through all five hours" is false | `facts_paper.json` | **Confirmed.** 44.5% committed in all five hours; 79.3% in at least four. |
| Abstract: the late-surge cluster "made most of their commits then" is a cluster mean | facts | **Confirmed.** Centroid 58.3%. At team level, 15.4% of active teams (163) made most of their commits in the last hour. The median team's last-hour share is 30.8%. |
| Test files: 76.9% overall vs about 89% in every track | facts | **Confirmed.** Weighted mean over the 984 matched active repositories is 89.0%. The overall figure uses 1,254 repositories, including the 197 with commits only outside the window. |
| The README rule labels mostly-English READMEs as Kazakh | `readme_features.csv`, `readme_features.py` | **Confirmed.** 11 of 34 "Kazakh" READMEs are mostly Latin script. The rule tests Kazakh letters only among Cyrillic letters. |
| "77 of 77 findings have the OpenAI marker" is circular | `run_analysis.py:405` | **Confirmed.** It is set to `len(oa)`, and the Gitleaks rule itself requires the marker. |
| Pull-request-only commits "reported separately" but not in the paper | facts | **Confirmed.** 117 repositories; not reported. |
| 14 references suggested by Reviewer 2 and 12 by Reviewer 1 | Crossref and DataCite | **All 26 exist**, and title and authors match. Karyotakis et al. is 2025 in Crossref, not 2026. |

The following were computed by Reviewer 1 and not re-checked here. They will be recomputed inside the pipeline during revision:
- 48.2% active among open, non-batch repositories;
- the no-batch odds ratio moves to 1.872 when repositories created before 1 September are excluded;
- a null-model silhouette of 0.18;
- a Gaussian mixture preferring k = 3;
- `.gitignore` covering `.env` in 91.1% of repositories with the OpenAI SDK against 46.0% without;
- Claude signatures in 199 repositories and Codex signatures in 48;
- 16 feature commits made under the organiser's app identity;
- README percentages computed over 1,185 READMEs (12.6 / 97.5 / 18.8 / 7.2%).

## 3. Blockers before any public posting

1. **False or misdescribed sentences:**
   - abstract l. 48 (the cluster claim);
   - Conclusion l. 324 ("most … all five hours"; "a third … concentrated");
   - l. 291 ("Russian and English");
   - l. 285 and l. 324 ("common", and a list read as universal);
   - l. 224 (the centroid presented as the group's share);
   - l. 57 and Table 1 ("archived after the deadline");
   - l. 167 (the Gitleaks fields we store privately include the commit SHA and line number).
2. **The pre-event archive stage.** Add it to the funnel, rerun RQ1 on the repositories open during the event, and say what the 446 are from timestamps alone. If the author asks the organisers anyway, one question would settle their meaning, but this is optional.
3. **Validation claims that do not hold:**
   - remove the circular marker row;
   - either remove "all reported numbers recomputed by separate code" from Fig. 1 or write that code (recommended: `checks/recompute_core.py`, which counts from the clones with git and no shared code);
   - call the earlier table a consistency check, not an independent source.
4. **The data release claim.**
   - `public_data_generated/` is empty.
   - Release it with *random* pseudonymous IDs. Hashes of public repository names can be reversed by hashing the public list.
   - Include a data card, and split the pipeline into a public stage (reruns every macro except RQ6) and a private stage.
   - Commit everything and archive it on Zenodo.
5. **README language.** Fix the rule so that "Kazakh" also requires most letters to be Cyrillic. Then validate it against the author's hand labels on full READMEs, and report the accuracy.
6. **Open items:**
   - affiliation;
   - other AI tools used;
   - key disclosure to the organisers (the author, via Telegram);
   - archived DOI.
7. **Timing.** Reviewer 1 notes that publishing, before the 1 October awards, an aggregate showing Claude signatures in about 200 repositories under a Codex-only rule could affect judging. **Recommendation: post the preprint after 1 October**, once the disclosure has been made and the language labels are done.

## 4. Revision plan

### Phase A: correctness, no new data (2–3 days)
- **A1.** Fix every sentence in Section 3, item 1.
- **A2.** Build the funnel as: created, then archived before the event, then open, then with team commits, then active, then matched to a track. Report the batch and repeated names as strata. RQ1 statistics:
  - use repositories open during the event;
  - report the no-batch estimate first;
  - model creation date by category or spline, not linear weeks, because the relationship is not monotonic;
  - drop the n = 2 group from the χ² test.
- **A3.** Define the population as *organiser-created repositories*. Add a reconciliation paragraph: 6,586 applications, 2,500 seats, "more than 2,500 participants" in the press, 3,649 repositories, 446 archived before the event, 1,040 in the batch, 3,203 open, 1,057 active. State that repository → registration → team is an assumption and that creation date stands in for registration date.
- **A4.** One denominator per family of measures, stated in every table and figure:
  - process measures (RQ2): active repositories;
  - product measures (stack, artefacts, documentation): active repositories, with the 1,254-repository figures in the supplement;
  - commits: say whether window or all.
- **A5.** Methods accuracy:
  - the window is defined on committer time;
  - the placeholder filter is described;
  - Gitleaks covers the 1,254 clones with team commits;
  - `AGENTS.md` and `CLAUDE.md` are matched as the code actually matches them;
  - pull-request refs count as a *workflow* trace, not an agent trace;
  - "SDK" includes API endpoint patterns;
  - the README "instructions" feature is tightened or renamed.
- **A6.** Statistics honesty:
  - reword "plan before any test" to "tests fixed after descriptive exploration";
  - add a table of deviations from the plan;
  - label exploratory analyses;
  - state the census interpretation (Baltes & Ralph 2022);
  - list every test with its correction family;
  - give Kruskal–Wallis its degrees of freedom and ε²;
  - give odds ratios and effect sizes to 2 decimals.
- **A7.** Citation wording, from the Reviewer 1 table:
  - Ziegler: perceived productivity only;
  - Liang: a survey;
  - McIntosh: the 2018–2019 MLH events;
  - Agarwal: add the "first AI tool" condition;
  - Basak: add the ESEM 2023 tool comparison;
  - Saghi: replace with the commit-timing literature;
  - Baumann: drop "similar settings";
  - AIDev: already combines several traces;
  - "follow earlier recommendations" becomes "are consistent with";
  - the five-hour window: cite the press, and mark 13:00–18:00 as inferred by this study.
- **A8.** The public dataset and independent recomputation (Section 3, items 3–4).

### Phase B: story and structure (3–4 days)
- **B1. Thesis** (adapted from Reviewer 2): *Because the organisers created a repository before the event for every registration they accepted, and every team had to use Codex, HackAlem AI gives a record of agent-assisted work under a fixed deadline with a known denominator and a known intended tool. The record shows that what repositories reveal about participation, agent use and credential exposure depends on how the event was run and on each tool's defaults, and researchers should account for both before reading repository traces as evidence of how people work with coding agents.*
- **B2. Four RQs:**
  - **RQ1 Population:** repositories, the pre-event archive, the batch, repeats and activity.
  - **RQ2 Process:** work rhythm, plus traces of the required and the non-required agents.
  - **RQ3 Product:** stack, artefacts and documentation, by track.
  - **RQ4 Risk:** credentials and the set-ups associated with them.
  - The current RQ7 folds into RQ1 and RQ3.
  - For the journal, **RQ5 Outcome:** which repository features are associated with the jury's decisions.
- **B3. Contributions mapped to RQs:**
  - C1: a census dataset;
  - C2: participation rates on a known denominator;
  - C3: trace-based detection of agent use tested against a known mandate;
  - C4: prevalence of artefacts and exposure;
  - C5: evidence-linked recommendations for organisers and researchers.
- **B4. Related work arranged by claim**, not by topic. Add the verified references in Section 6.
- **B5. Results.** End each RQ with a one-sentence answer, and add a table "Answers to the research questions" (RQ, unit and n, answer, key estimates with 95% CI, figure). Move the lists of numbers out of the prose and into that table.
- **B6. Discussion in three themes, each compared with published numbers:**
  - *Denominators decide rates.*
  - *What traces reveal under a known mandate:* compare with Robbes et al.'s adoption rates and the `AGENTS.md` prevalence in Chatlatanagulchai et al.
  - *Cheap artefacts, costly mistakes:* compare with Meli et al.
  - Then implications for organisers, researchers and educators.
- **B7. Threats** following the ACM SIGSOFT Empirical Standards for repository mining, each threat with its mitigation. Add an ethics statement: exemption, or the reason none is needed.
- **B8. Remove the 22 repetitions** listed by Reviewer 2. Say AI use once in Methods, and once in the Acknowledgments for MDPI. The abstract stays within 200 words.
- **B9. Reporting conventions**, written into `style_guide.md`:
  - counts as "n (x.x%)";
  - "(95% CI a–b)" every time;
  - descriptive medians as "median (IQR a–b)", with a CI only when the median is estimated or compared;
  - odds ratios, V and δ to 2 decimals, test statistics to 1;
  - figures use 1 decimal, matching the text;
  - "%" always, never "per cent";
  - "10 min" in figures and "ten minutes" in prose;
  - one term per concept: *team repository, active repository, event window, agent trace, workflow trace, credential exposure*.

### Phase C: new analyses from the existing data (about 1 week; can go into arXiv v1)
- **C1.** The per-team distribution of last-hour shares (ECDF or histogram) replaces the clusters. The clusters become exploratory, with a null-model silhouette and bootstrap stability.
- **C2. Trace × tool matrix and UpSet plot**, covering Codex, Claude Code and others, and context files, trailers and branches. This tests the published trace heuristics (Robbes et al.) against the known mandate. It also gives a lower bound on use of a non-required agent.
- **C3. Security linkage** (private, aggregates only):
  - were key-bearing commits agent-signed?
  - the `.gitignore` association stratified by OpenAI-SDK use and `.env.example`;
  - a hand check of the 127 provider findings;
  - a statement of recall limits.
- **C4. Sensitivity table:**
  - author vs committer time;
  - window shifted by ±30/60 min;
  - features at the 18:00 state vs the final HEAD;
  - excluding pre-event code (Imam et al. 2021).
- **C5. Attendance triangulation:** distinct non-bot authors per active repository, counted in memory and reported as an aggregate, against "more than 2,500 participants".
- **C6. README language by track**, to test the task-language explanation (the meeting-minutes track involves Kazakh audio).

### Phase D: journal level (after 1 October)
- **D1. Pre-registered jury analysis.** Time-critical: finalists may be known at Demo Day on 29 September, so register by **28 September**. Hypothesis: within a track, the jury rewards artefacts that agents make cheap no more than chance. Use track-stratified permutation tests or conditional logit, with honest power statements.
- **D2. Pre-agent baseline** from HackRep (Zenodo 10.5281/zenodo.17572684, CC BY 4.0, 2.5 GB), matched on event length. Compare artefact prevalence, README length and commit timing.
- **D3. Homogenisation within a track**, measured by README, dependency and file-tree similarity (Doshi & Hauser 2024; Anderson et al. 2024).
- **D4. For MAKE:**
  - a human-labelled benchmark comparing rules, an LLM and humans (κ; this also closes the README validation);
  - a positive-unlabelled estimate of the share of agent-written commits (Elkan & Noto 2008; Bekker & Davis 2020).
- **D5. Do the tests run?** A stratified sample of about 100 repositories, run in isolated containers with no network.

## 5. Venues

The reviewers agree on the order: EMSE first for subject fit, then BDCC, which fits with a human–AI framing and has already published a paper on generative AI in hackathons, then MAKE, only with Phase D4. JSS and IEEE Access are alternatives. For the dataset: Scientific Data, Data in Brief or MDPI Data. A Scientific Data descriptor may not contain analyses, so do not split the results across two papers. Check quartiles and review times on JCR, Scopus and the journal pages before choosing.

## 6. References to add (all verified in Crossref or DataCite, 27 September 2026)

| Group | Reference and DOI | Supports |
|---|---|---|
| Agent traces | Robbes et al., MSR 2026, 10.1145/3793302.3793375 | trace heuristics, partial observability |
| | Robbes et al., TOSEM 2026, 10.1145/3822180 | adoption rates to compare against |
| | Robbes et al. 2026, arXiv 10.48550/arXiv.2606.07448 | adoption in new projects |
| | Galster et al. 2026, arXiv 10.48550/arXiv.2605.08435 | agent configuration files |
| | Tufano et al., MSR 2024, 10.1145/3643991.3644918 | ChatGPT use mined from repositories |
| | He et al., MSR 2026, 10.1145/3793302.3793349 | Cursor: velocity vs complexity |
| Hackathons | Mahmoud et al., EMSE 2022, 10.1007/s10664-022-10201-x | hackathon code creation and reuse |
| | Imam et al., MSR 2021, 10.1109/MSR52588.2021.00020 | pre-event code in hackathon projects |
| | Chau & Gerber, CHI 2023, 10.1145/3544548.3581234 | hackathon literature review |
| Timing | Claes et al., ICSE 2018, 10.1145/3180155.3180193 | commit timing |
| | Karyotakis et al., EMSE 2025, 10.1007/s10664-025-10767-2 | commit times |
| | Kuutila et al., IST 2020, 10.1016/j.infsof.2020.106257 | time pressure (SLR) |
| | Edwards et al., ICER 2009, 10.1145/1584322.1584325 | student deadline behaviour |
| | Kazerouni et al., ICER 2017, 10.1145/3105726.3106180 | procrastination and incremental work |
| Mining | Bird et al., MSR 2009, 10.1109/MSR.2009.5069475 | perils of mining git (timestamps) |
| | Baltes & Ralph, EMSE 2022, 10.1007/s10664-021-10072-8 | census vs sampling |
| | Ralph et al. 2020, 10.48550/arXiv.2010.03525 | Empirical Standards |
| Secrets | Basak et al., ESEM 2023, 10.1109/ESEM56168.2023.10304853 | comparison of secret detection tools |
| | Perry et al., CCS 2023, 10.1145/3576915.3623157 | insecure code with AI assistants |
| Statistics | Rousseeuw 1987, 10.1016/0377-0427(87)90125-7 | reading silhouette values |
| Language | Togmanov et al., ACL 2025, 10.18653/v1/2025.acl-long.701 | LLMs on Kazakh (KazMMLU) |
| Optional (Phase D) | Doshi & Hauser 2024, 10.1126/sciadv.adn5290; Anderson et al. 2024, 10.1145/3635636.3656204; Elkan & Noto 2008, 10.1145/1401890.1401920; Bekker & Davis 2020, 10.1007/s10994-020-05877-5; Kaufman & Rousseeuw 1990, 10.1002/9780470316801 | homogenisation; PU learning; clustering |

Each is added only after its abstract is read and it is logged in `screening.csv`, as for the existing 39.
