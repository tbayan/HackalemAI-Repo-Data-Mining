# Reviewer 2 report: framing, storyline, writing and presentation

**Manuscript:** "Five Hours, 3,649 Repositories: An Empirical Study of an Agent-Assisted Mass Hackathon" (arXiv preprint draft, 12 pp., `latex/main.tex`, build of 26 Sep 2026)
**Reviewer focus:** novelty, significance, framing, research questions, contributions, writing quality, figures and tables.
**Line numbers** (l. N) refer to `latex/main.tex`. Rendered values were checked in `main.pdf`, and where it helped, against `analysis/facts_paper.json`.

---

## 1. Summary

The paper studies all 3,649 public GitHub repositories that the organisers of HackAlem AI (Astana, 23 Sep 2026) created before a five-hour, in-person hackathon at which teams had to use OpenAI Codex. The author mirrored every repository with its full history, validated the rebuilt counts against the GitHub API, and answers seven descriptive research questions: the funnel from repository to activity, the timing of work, the technology stack, agent traces, README language and completeness, credential leaks, and track distribution. Headline results: 29.0% of repositories were active during the event, 28.8% of event-time commits fell in the last hour, test files appear in 76.9% of repositories with team commits, Claude-signed commits outnumber Codex-signed ones about ten to one although Codex was required, READMEs are 87.0% Russian and 2.9% Kazakh, and OpenAI-key strings reached the public history of 61 repositories, many through `.env.example`. The data engineering is careful and transparent: every number is generated from the data, there is a claim ledger, and secrets were handled ethically. As a paper, though, it is a well-built census without an argument. The seven RQs are parallel inventories. The Discussion mostly restates the Results and then hedges. The strongest scientific asset, a complete population where the required agent is known, is never turned into a claim that someone else could test or build on.

**The paper's thesis as I can reconstruct it (it is not stated anywhere):** "Because the organisers opened a repository for every registration, we can describe the whole population of an agent-mandated hackathon." That is a description of the data, not a thesis.

**Proposed thesis sentence:**
> Because every registration received a repository and every team had to use Codex, HackAlem AI gives a complete, known-denominator record of agent-assisted work under a fixed deadline; this record shows that what repositories reveal about participation, agent use and credential exposure is shaped by event logistics and tool defaults, which must be accounted for before repository traces are read as evidence of how people work with coding agents.

## 2. Recommendation

**(a) arXiv readiness: minor revision. Do not post the current build.** Five placeholders are still visible in the PDF: affiliation (l. 39), AI-tools statement (l. 200), README-rule accuracy (l. 191, l. 306), organiser disclosure (l. 317) and dataset DOI (l. 319). Two of them are blockers. The organisers must be told about the leaked credentials before a public paper says they exist, and the README-language shares should not be published without the accuracy of the rule that produced them. The abstract and Conclusion also contain three factual misstatements (issue M1) that must be fixed before any public release. With those fixed and the denominators unified (M3), the preprint is a useful, honest data paper.

**(b) Q1 AI or human–AI journal (MDPI BDCC/MAKE, Elsevier IJHCS/CHB, IEEE Access, Springer EMSE): major revision.** In its current form I expect a desk rejection at MAKE (there is no machine-learning or knowledge-extraction contribution) and a borderline desk decision at BDCC (a descriptive MSR census with no thesis, no baseline and no AI/cognitive angle). The data are good enough for a Q1 paper. What is missing is an argument, a comparison and at least one analysis that only this dataset allows (Section 10). With the winners list after 1 October, a pre-registered outcome analysis would lift the paper considerably.

## 3. Strengths

1. **Unusual data design.** An organiser-provisioned, complete population with full history, a fixed five-hour window and a tool mandate. The gap statement at l. 89 ("These datasets contain projects that teams chose to list; they cannot show registrations that produced no code") is clear and true.
2. **Careful measurement.** All refs are mirrored. The template commit is detected by a rule that does not depend on the author account (l. 164). Clone and API counts agree for all 3,649 repositories. A live audit caught a real error (16 repositories with template commits by a second organiser account; l. 173), and the paper reports it openly.
3. **Reproducibility discipline.** Every number is a macro generated from `facts_paper.json`. There is a claim ledger, a literal-number check and a banned-word lint. `main.tex` has no hits for the banned list; I checked it independently.
4. **Ethics of secrets.** Output was redacted, keys were never tested, and results are reported only in aggregate (l. 167, l. 317).
5. **Candid AI-use statement** (l. 199–200), which is rare and welcome.
6. **One visual system.** A single Okabe–Ito palette, Times-metric fonts and vector PDFs, with no chart junk.

## 4. Major issues

Each entry gives the location, the problem, the fix and the effort: S (under 1 day), M (a few days) or L (more than a week).

**M1. Factual overstatements in the abstract, Discussion and Conclusion.** Effort: S.
- l. 48: "a cluster of \NRhythmCTwoPct\% of teams made most of their commits then". The 58.3% is the cluster *centroid*. At team level, only 15.4% of active teams (163; `teams_majority_last_hour` in `facts_paper.json`) made most of their commits in the last hour. The sentence reports a cluster mean as a fact about each team.
- l. 324: "Most active teams worked through all five hours". False: 44.5% committed in all five hours (l. 224). The true statement is "in at least four of the five hours" (79.3%).
- l. 324: "a third of them concentrated their work at the end" has the same problem as l. 48.
- l. 291: "Documentation was written mostly in Russian and English". English is 9.7%, so this should say "mostly in Russian".
- l. 285 "Tests, Docker files and long READMEs were common" and l. 324 "their repositories contain tests, Docker files, agent context files and long documentation": Dockerfiles appear in 28.6% and context files in 31.0%. Both sentences read as if all repositories contain all four. Quantify or narrow them.
- **Fix:** report the team-level statistic (15.4%, or the median team's last-hour share, 30.8%) in the abstract and Conclusion, and restate these sentences with their macros.

**M2. No thesis, seven flat RQs and a gap that is about method rather than about a question.** Effort: M.
- l. 55 builds the gap as "studies of generative AI inside hackathons ... are qualitative and small". l. 57 answers it with "HackAlem AI offers a different view". The gap is a *scale and design* gap, not a knowledge gap. The reader never learns what we do not know that matters.
- The RQs (l. 62–68) are "how many / how / which / what / in which / how often / how" questions, one per feature family. RQ2, RQ3, RQ5 and RQ7 have no motivating paragraph in Related Work. Time use appears only as the last sentence of "Mining GitHub" (l. 101). There is nothing on technology choice, nothing on multilingual documentation (which `positioning.md` lists as "still to search"), and nothing on track choice.
- No RQ has an explicit answer sentence. The contributions (l. 73–75) do not map to RQs: C1 bundles all seven.
- **Fix:** state the thesis at the end of the second Introduction paragraph, regroup into 3–4 RQs (Section 5), and end every Results subsection with a one-sentence answer, or add an answer table (Section 8).

**M3. Inconsistent denominators that make results look contradictory.** Effort: S–M.
- l. 164 says RQ2 and RQ7 use the 1,057 active repositories and RQ3–RQ6 use the 1,254 repositories with team commits. Fig. 1(e) (`figures/architecture.tex`, the "RQ3--RQ7" label) says RQ3–RQ7 use 1,254. One of the two is wrong.
- Test files: 76.9% of 1,254 (l. 235, abstract l. 48). Yet every one of the twelve per-track values in Table 2 (active repositories) is at least 76.1%, and the weighted mean over the 984 matched active repositories is about 89%. The overall figure is lower than almost every track because it includes the 197 repositories with commits only outside the window, which have few tests. A reader will read this as an error.
- Within RQ4, prevalence uses 1,254 (l. 246, Fig. 4) but the `AGENTS.md` association uses the active 1,057 (l. 248; n_with = 352 vs 360 overall).
- Fig. 2a labels "Matched to a track 984 (27.0%)", a share of 3,649. l. 207 gives "984 (93.1%)", a share of active repositories. The same number carries two percentages.
- The analysis plan (`analysis_plan.md`, RQ3) specified "Prevalence among active repositories". The paper deviates without saying so.
- **Fix:** use the active repositories as the single denominator for every process and product measure (RQ2–RQ7). Report the 1,254 figures in a supplement. State the denominator in every figure axis and table header.

**M4. The "complete population of registrations" framing is contradicted by the paper's own findings.** Effort: S.
- l. 57 says "The organisation therefore contains every registration". l. 324 says "Of 3,649 registrations". But l. 209 identifies 1,040 repositories (28.5% of the population) as "a batch created by the organisers, not as individual registrations", and l. 211 finds 480 repositories under 224 repeated team names.
- The headline RQ1 statistics mix the two populations. χ²(4) = 609.2, V = 0.409 and OR = 1.878 are all driven by the batch. The estimate without the batch (OR 1.170, 95% CI 1.082–1.265) is the defensible one and should come first.
- **Fix:** define the unit as *provisioned repository*, not *registration*. Report RQ1 with and without the batch. Change the wording at l. 48, l. 57 and l. 324. Also change "depended on" (l. 209) to "varied with", because this is an observational association.

**M5. The novelty claim and contribution 2 ignore the closest measurement literature.** Effort: M.
- The "first" claim (l. 71) is safe only because it carries three qualifiers (repository-level, complete population, AI use required). Editors read triple-qualified firsts as weak. What is missing is *why* completeness and the mandate matter scientifically.
- Contribution 2 (l. 74, "agent signatures that reflect tool defaults rather than use") and the Discussion paragraph at l. 288 overlap with published work that is not cited:
  - Robbes, Matricon, Degueule, Hora, Zacchiroli, "Promises, Perils, and (Timely) Heuristics for Mining Coding Agent Activity", MSR 2026, doi:10.1145/3793302.3793375. It names "partial observability" and "agent multiplicity" and lists branch prefixes such as `codex/` as heuristics.
  - The same authors, "Agentic Much? Adoption of Coding Agents on GitHub", ACM TOSEM 2026, doi:10.1145/3822180. It estimates adoption from traces across 128,018 projects.
  - Robbes et al., "Agentic Very Much! Adoption of Coding Agent in New GitHub Projects", arXiv:2606.07448 (2026).
  - Galster et al., "A Dataset of Agentic AI Coding Tool Configurations", arXiv:2605.08435 (2026).
  - For hackathon code at repository level: Mahmoud, Dey, Nolte, Mockus, Herbsleb, "One-off events? An empirical study of hackathon code creation and reuse", Empirical Software Engineering 2022, doi:10.1007/s10664-022-10201-x.
- **Fix, and the opportunity:** reposition the mandate as a *known intended tool*. This is the only setting I know of where a researcher can measure how much of a required agent's use the standard trace heuristics recover. Apply the Robbes et al. heuristics to every active repository and report detection per heuristic and for the union (see Idea 2). That turns contribution 2 from "we also noticed signatures are biased" into "we measured the bias against a known mandate".

**M6. No baseline, so the most quotable result cannot be interpreted.** Effort: L for the journal, S for the arXiv wording.
- l. 235 ("Engineering artefacts were common") and l. 252 ("READMEs are long for a five-hour event") are comparative claims with nothing to compare against. l. 285 admits "we cannot say how unusual this is".
- **Fix:** for the journal, run the same feature pipeline on a pre-agent and a recent non-mandated hackathon sample (Idea 3). For arXiv, drop "common" and "long for a five-hour event" and report the values plainly.

**M7. The Discussion restates the Results and does not interpret them.** Effort: M.
- Each Discussion paragraph opens by repeating a result: l. 282 "Two thirds of the repositories received no team commits", l. 288 "Commit signatures named Claude far more often than Codex, although Codex was required" (nearly verbatim from l. 246), l. 291, and l. 294.
- RQ3 and RQ7 have no Discussion at all. There is no comparison with prior quantitative findings: adoption rates in Robbes et al., `AGENTS.md` prevalence and content in Chatlatanagulchai et al., leak rates in Meli et al., or commit timing in McIntosh and Hardin. There is also no synthesis across RQs.
- The paragraph at l. 285 stacks three hedges and ends by saying nothing.
- **Fix:** build three cross-cutting themes (Section 5, proposed outline), each tied to a prior number, and add an "Implications" paragraph for organisers, researchers and educators.

**M8. The Results read as tables written out as prose, and the promised CIs are mostly missing.** Effort: M.
- Number macros per sentence: l. 235 about 5, l. 248 about 6, l. 252 about 6, l. 222 about 5. l. 197 promises "Proportions carry Wilson 95% confidence intervals", yet only one proportion in the text has a CI (tests, l. 235).
- **Fix:** add an RQ summary table (Section 8) that holds n, %, 95% CI and the source figure. Keep in the text only the two or three comparisons that carry each answer.

**M9. Undisclosed deviations from the analysis plan, and weak clusters presented as "two groups".** Effort: S.
- The plan specifies a logistic regression on *log days before the event*. The paper reports OR *per week* (l. 209).
- The plan marks commit size and the key-versus-`.gitignore` test as *exploratory* and promises "Anything added later is marked exploratory in the paper". Neither is marked at l. 248 or l. 265.
- The plan says RQ7 is "Descriptive only", but l. 276 runs a Kruskal–Wallis test. That test is not listed under Statistics (l. 197) and is reported without df or effect size.
- Only RQ4 says "Holm-adjusted" (l. 248), although l. 197 says Holm correction is applied within each question.
- l. 224, "Clustering the hourly profiles gives two groups (silhouette 0.304)": by the usual reading (Rousseeuw 1987, doi:10.1016/0377-0427(87)90125-7; Kaufman and Rousseeuw 1990, doi:10.1002/9780470316801), a silhouette of 0.26–0.50 indicates weak structure that may be artificial. The clusters split a continuum.
- **Fix:** add a "Deviations from the analysis plan" paragraph. Label the exploratory tests. Show the distribution of each team's last-hour share instead of, or before, the clusters.

**M10. Placeholders, and an unsupported claim in Fig. 1.** Effort: S–M.
- Pending items at l. 39, l. 191, l. 200, l. 306, l. 317 and l. 319.
- Fig. 1(c) states "All reported numbers recomputed by separate code". Neither the text nor Table 3 describes such an independent recomputation, and `checks/check_numbers.py` only checks that numbers are macros.
- **Fix:** either document the independent recomputation as a row in Table 3 or remove the claim from Fig. 1.

**M11. Agent use is underclaimed where a lower bound is safe.** Effort: S.
- l. 246 treats signatures "not as a measure of use". Yet 3,502 Claude-signed commits are *proof* that a non-required agent was used in at least the repositories that contain them. Together with `CLAUDE.md` in 153 repositories, this gives a lower bound on non-mandated tool use, an interesting finding for human–AI interaction (tool preference versus rules) that the paper leaves unreported.
- **Fix:** report the number of repositories with Claude, Codex and Cursor signatures, and their overlap with the context files (an UpSet plot), phrased as lower bounds.

**M12. Speculative causal wording in the security Discussion.** Effort: S.
- l. 294 says "Simple measures would have prevented most of them" and "matter more when an agent writes configuration files quickly". Neither is tested.
- l. 265 "This matches the association we observe" reads a small association (V = 0.079) as support for a mechanism.
- **Fix:** check whether the key-bearing commits or the commits that created `.env.example` were agent-signed. The data already exist. Then word the recommendation as "would likely have blocked". Report the cross-tabulation of file type (`.env.example` versus `.env`) by `.gitignore` coverage, which is the direct test of the "false sense of security" reading.

## 5. Minor issues

1. l. 32: "Mass hackathon" is vague, and "An Empirical Study of" says nothing. See Section 9 for alternatives.
2. l. 48: at 215 rendered words the abstract exceeds MDPI's 200-word limit. The Guinness sentence has no analytic role and reads as promotional in an abstract; keep it in Table 1 only.
3. l. 106 and l. 130: two short Event paragraphs. The first sentence at l. 106 only points to the table. Merge them, and move the archive timing (l. 130) to Collection (l. 161).
4. l. 106 and l. 110 (Table 1): the text and caption say these are the event facts "that we use" / "used in this paper", but the Prizes and Participants (21 countries) rows are never used. Drop them or change the caption.
5. Table 2 sits in Section 3 (Event) but contains results (Repos, median commits, Tests %, Python %). Results appear before Methods. Keep partner and task in Section 3 and move the result columns to RQ7, or to the appendix.
6. l. 170 and l. 173: "an earlier per-repository table" is never identified. It is the author's own public report (root `README.md` and the bilingual charts). Cite it as a prior version (GitHub or Zenodo) and say that it was produced by the same author.
7. l. 170 and l. 246: two sentences start with a numeral ("73 active repositories...", "3,979 commits..."). Rephrase them.
8. l. 167 and l. 235: "three per cent" and "less than three per cent" conflict with "%" everywhere else. In Methods, give thresholds as numbers (3%, 50%, 80%).
9. l. 246: "Codex appears instead in branch names: ... and 31.4% have pull-request references". Pull-request refs are not a Codex trace unless shown to be. Fig. 4 files "Pull-request refs" under "Agent footprint". Justify this or move it.
10. l. 252: "Commit messages are mostly in Latin script (89.4%)". Fig. 5 puts "English / Latin" in one legend entry, which conflates script with language (Latin-script commit messages include transliterated Russian and Kazakh).
11. l. 276: "did not differ clearly" (p = 0.062) is a soft dichotomy. Report H(11), p and ε², and say the medians range from 16 to 31.
12. l. 222: the first commit comes a median 61 minutes after the start, which is striking and never interpreted (set-up? agent cloud tasks that end in pull requests?). Either interpret it or drop it from the text.
13. l. 282 and l. 106 both cite the queue reports. Mention them once, in Discussion.
14. l. 297: "Three issues would have biased our results" gives no size for any of them. Quantify each (16 repositories with template commits by the second account; 117 repositories with pull-request-only commits, from the `validation` facts; duplicates 480).
15. l. 303–312: Threats is four short checklist paragraphs. "Reliability" (l. 312) repeats l. 319. Merge Reliability into Data availability, and give each threat its mitigation.
16. l. 315: the section title "Ethics, data availability and use of AI tools" repeats the Methods paragraph at l. 199. MDPI wants AI use in Methods *and* in Acknowledgments; do not have a third mention.
17. The PDF date "September 26, 2026" (US order, from `\today`) differs from the British "23 September 2026" used elsewhere.
18. Table 2: the leading zeros in "01–12" and the abbreviation "Creative ind." look informal. Add a row for the 73 unmatched repositories so the columns reconcile with 1,057.
19. Terminology drift. "Teams" (l. 222, 224, 276), "repositories" and "registrations" (l. 324) are used interchangeably, even though l. 164 says a repository is a registration. Likewise "agent traces" (l. 73, 244) versus "agent footprint" (Fig. 1, Fig. 4), and "credential hygiene" (l. 261) versus "security hygiene" (Fig. 1) versus "secret leakage" (keywords). Pick one term per concept and use it in the headings, figures and keywords.

## 6. Storyline

### 6.1 Current narrative (as written)

1. **Abstract:** event facts, then Guinness, then "we studied six things", then eight numbers, then "we release data".
2. **Introduction:** hackathons have been studied; AI assistants changed software; GenAI-in-hackathon studies are small. "HackAlem offers a different view" (event facts, repeated). Seven RQs, a triple-qualified "first", and three contributions.
3. **Related work:** five parallel paragraphs, none of which motivates RQ2, RQ3, RQ5 or RQ7.
4. **Event:** Table 1 (event facts, again), repository naming, archive times, and Table 2 (tracks, including results).
5. **Methods:** collection, definitions, features, labels, validation (Table 3), statistics, AI use.
6. **Results:** RQ1 to RQ7, parallel, heavy on numbers, no answers.
7. **Discussion:** six run-in paragraphs, roughly one per RQ, each opening with a restated result.
8. **Threats, then Ethics** (repeating Methods), then **Conclusion** (repeating the abstract, with two errors, M1).

**Diagnosis.** There is no tension, so every section hands off by listing rather than by argument. Sections 3 and 4 hand off well; Sections 2 to 5 and 5 to 6 do not. The Conclusion adds only the future-work sentence.

### 6.2 Proposed narrative

1. **Introduction (about 0.9 pages).**
   - Problem: coding agents now write much of the code in new projects, and research measures this through repository traces (AIDev; Robbes et al.) or through small qualitative hackathon studies.
   - Tension: both approaches rely on samples whose selection is unknown (listed projects, detectable agents), and neither knows which tool the developers were supposed to use.
   - Opportunity: HackAlem AI provisioned a repository for every registration and mandated a single agent under a fixed deadline, which gives a known denominator and a known intended tool.
   - Thesis sentence, then 4 RQs, then contributions mapped to the RQs.
2. **Related work, organised by claim rather than by topic:**
   - (i) selection in hackathon and GitHub mining, which motivates RQ1;
   - (ii) human time use under deadlines and measuring agent use from traces, which motivates RQ2 (add Robbes et al., Galster et al., Edwards et al. 2009, doi:10.1145/1584322.1584325);
   - (iii) what AI-assisted projects contain, including artefacts, documentation, homogenisation and low-resource languages, which motivates RQ3;
   - (iv) secrets and AI-built software, which motivates RQ4.
3. **Setting and data:** event, provisioning, collection and definitions in one section. Table 1 shortened; Table 2 without result columns.
4. **Methods and validation:** concise. Table 3 moves to the appendix. Add the plan deviations here.
5. **Results:** one subsection per RQ, each ending in a bold one-sentence answer, plus the RQ answer table.
6. **Discussion, as three themes rather than one paragraph per RQ:**
   - *Denominators decide rates:* registration is not participation, the batch and duplicates, and what this means for organiser-created data.
   - *What traces reveal about agent use under a known mandate:* signatures, context files and branches, compared with the Robbes et al. adoption rates.
   - *Artefacts cost little, mistakes cost more:* high artefact rates next to template-driven leaks, with the baseline comparison when available.
   - Then implications for organisers, for researchers mining agent activity, and for educators.
7. **Threats:** one paragraph per validity type, each with its mitigation.
8. **Ethics and data availability:** AI use is stated once, in Methods, and in Acknowledgments for MDPI.
9. **Conclusion (4–5 sentences):** the answer to the thesis, one lesson for each audience, and the jury analysis to come.

## 7. Revised research questions

The seven current RQs are too many and too flat for a journal. Each one names a feature family, not a question. I propose four, grouped by unit of analysis and tied to the thesis, plus a fifth for the journal version.

| New RQ | Wording | Current results that move here |
|---|---|---|
| **RQ1 Population** | Of the repositories provisioned for every registration, how many carried event-time work, and how much of the gap reflects logistics (creation timing, the organiser batch, duplicate registrations)? | Current RQ1 in full (l. 207–211, Fig. 2); track coverage (984 of 1,057 active, l. 207); track counts from RQ7 (l. 276), as a descriptive note |
| **RQ2 Process** | How did teams spread their work over the five-hour window, and which traces of the required and the non-required agents does that work leave? | Current RQ2 (l. 222–224, Fig. 3); current RQ4 (signatures, branches, PR refs, context files, commit size, `AGENTS.md` associations; l. 246–248); new: lower bound on non-mandated agent use (M11); detection by trace heuristic (Idea 2) |
| **RQ3 Product** | What did teams produce (stack, engineering artefacts, documentation and its language), and how does it vary between tracks? | Current RQ3 (l. 235, Fig. 4 engineering and LLM rows); current RQ5 (l. 252, Fig. 5); per-track variation from RQ7 and Table 2 (l. 276) |
| **RQ4 Risk** | How did credentials reach the public history, and which repository set-ups and workflows (templates, `.gitignore`, agent-signed commits) go with them? | Current RQ6 (l. 263–265, Fig. 6); new: agent-signature cross-tab for key-bearing commits (M12) |
| *RQ5 Outcome (journal)* | Which repository features are associated with the jury's decisions, within track? | New, from the winners list after 1 Oct (Idea 1) |

Contributions should then map one-to-one to these RQs (Section 9.3).

## 8. Redundancy list

These are repeated facts or sentences, with short quotes. The number of places each appears is given in brackets.

1. **Repository per registration [7].**
   - l. 48 "created a public GitHub repository for every registration" and, in the same abstract, "Because every registration received a repository";
   - l. 57 "created a public repository ... for every registration" and "The organisation therefore contains every registration";
   - l. 81 (Fig. 1 caption) "Every registration received a public repository (a)";
   - Fig. 1(a) "One public repository per registration";
   - l. 125 (Table 1) "one public repository per registration";
   - l. 324 "Because the organisers of HackAlem AI created a repository for every registration".
2. **Archived after the deadline [7].** l. 57, l. 125, l. 130, Fig. 1(a), l. 161 "The repositories were archived, so their content could no longer change", l. 294 "archived repositories whose history cannot be changed", l. 312 "now archived".
3. **Codex required [7].** l. 48, l. 57, l. 119, Fig. 1(a), l. 246 "although Codex was the required tool", l. 288 "although Codex was required", l. 324 "a common agent requirement".
4. **Signatures reflect defaults [3].** l. 74 "agent signatures that reflect tool defaults rather than use", l. 246 "evidence of each tool's default disclosure behaviour, not as a measure of use", l. 288 "tools differ in whether they sign commits by default".
5. **Keys never tested [5].** l. 167 "never tested any string against a service", l. 263 "We did not test whether any key worked", l. 303 "we did not test them", l. 317 "never tested", Fig. 1(d) "(redacted, never tested)".
6. **Numbers generated by scripts [5].** l. 75, l. 197 "All numbers in this paper are generated from the data by the released scripts", l. 312, l. 319, Fig. 1(f) "Paper with generated numbers".
7. **Hashed identifiers [5].** l. 75, l. 81, Fig. 1(f), l. 317, l. 319.
8. **Template commits by a second organiser account [5].** l. 74, l. 173, l. 185 (Table 3), Fig. 1(c), l. 297.
9. **Repository is not a person or team [4].** l. 164 "we never infer head counts", l. 282 (heading), l. 297 "one repository per registration rather than per person", l. 303 "A repository is a registration, not a person or necessarily a team".
10. **Association caveat for `AGENTS.md` [2].** l. 248 "These are associations: teams that set up context files may differ...", l. 306 "Associations with AGENTS.md may reflect differences between teams".
11. **Queue and entrance reports [2].** l. 106 and l. 282, both citing [17, 18].
12. **Solo entry [3].** l. 106, l. 118, l. 164.
13. **Track matching [3].** l. 170 "73 active repositories could not be assigned", l. 189 (Table 3), l. 207 "984 (93.1%) could be assigned".
14. **Event window inferred [2].** l. 117 (Table 1) and l. 306.
15. **The six-topic list [3].** l. 48 "participation, work rhythm, technology choices, traces of agent use, documentation language, and credential hygiene", l. 73 (the same list), and Fig. 1(d)/(e).
16. **Empty repositories [4].** l. 48 (65.6%), l. 207, l. 282 "Two thirds of the repositories received no team commits", Fig. 2a.
17. **Last-hour peak [5].** l. 48, l. 222, l. 224, l. 285, l. 324.
18. **Artefacts [4].** l. 48, l. 235, l. 285, l. 324.
19. **Russian and Kazakh documentation [4].** l. 48, l. 252, l. 291, l. 324.
20. **OpenAI keys and `.env.example` [4].** l. 48, l. 263–265, l. 294, l. 324.
21. **AI-tool use [3].** l. 199–200, l. 315 (section title), l. 319.
22. **Event facts [3].** l. 57 (Introduction), Table 1 (l. 116–125) and Fig. 1(a) all carry date, place, window, team size, Codex rule, seats and applications.

**Paragraphs to cut or merge:**
- l. 106 + l. 130: merge into one Setting paragraph, and drop the signpost sentence.
- l. 130 (archive timing) and l. 161: move to Collection.
- l. 170 + l. 207 (last sentence): give the track matching once, in Methods.
- l. 199–200 + l. 319: state AI use once.
- l. 297: shorten and quantify, and cross-reference l. 173 instead of restating it.
- l. 312 (Reliability): fold into l. 319.
- Fig. 1(a): remove the event facts that are already in Table 1.
- l. 324: rewrite (see M1 and Section 9.2).

## 9. "AI feel" in the prose, with rewrites

The banned-word discipline works: I found no hits in `main.tex`. What remains are *structural* signs that experienced reviewers recognise.

**Main patterns:**
1. **"Not X but Y" and "rather than" contrasts.** There are nine: l. 57, l. 74, l. 209, l. 246, l. 282, l. 297, l. 303 (twice), l. 306.
2. **Colon reveals.** l. 57 "the key design choice was technical:", l. 265 "This matches the association we observe:".
3. **Triplets.** l. 291, l. 294, l. 297.
4. **Dramatic short tags.** l. 200 "and they did.", l. 161 "All clones completed."
5. **Parallel "For X ...; for Y ..." closers.** l. 282.
6. **Hedge stacks.** l. 285.
7. **Paragraphs of uniform length with bold run-in heads** in the Discussion (six, 51–98 words each) and Threats (four, 1–4 sentences each). This gives a checklist rhythm.
8. **Results sentences that list 5–6 numbers.** l. 235, l. 248, l. 252.

**Specific sentences and suggested rewrites** (numbers are left as macros or placeholders):

| l. | Current | Suggested |
|---|---|---|
| 55 | "In parallel, AI programming assistants and, more recently, autonomous coding agents have changed how software is written." | "Coding agents such as Codex and Claude Code now edit whole repositories from natural-language instructions [cites]." |
| 57 | "HackAlem AI offers a different view." | Delete it. Start the paragraph with the fact: "At HackAlem AI, held in Astana on \eventdate, ..." |
| 57 | "For our purposes, the key design choice was technical: the organisers created a public repository ..." | "What makes the event useful for research is that the organisers created a public repository ... for every registration before the event and archived all of them at the deadline." |
| 48 | "Most active teams committed in at least four of the five hours, yet \NPctLastHour\% of event-time commits fell in the last hour, and a cluster ..." | "Work was spread across the afternoon: \NTeamsFourplusHoursPct\% of active teams committed in at least four of the five hours. The last hour held \NPctLastHour\% of event-time commits, and [team-level %] of teams made most of their commits in it." (The "yet" sets up a contrast that is not there.) |
| 48 | "We release the derived data and the pipeline, and discuss what organisers of agent-assisted events can learn from these records." | Name the lesson: "Provisioning repositories only after check-in and shipping placeholder-only `.env.example` templates would have removed the two largest sources of error and exposure that we found." (Adjust to what the revised analysis supports.) |
| 200 | "...were designed to catch errors in AI-produced analysis, and they did." | "One of these checks, the live audit of template commits, found an error in the first AI-produced counts (\NValidationTemplateFixes{} repositories), which we corrected." |
| 246 | "We therefore treat commit signatures as evidence of each tool's default disclosure behaviour, not as a measure of use." | "Signatures therefore show which tools sign by default. They give a lower bound on the use of each tool, not a rate." |
| 265 | "This matches the association we observe: keys were more frequent in repositories whose .gitignore covered .env ..." | "Repositories whose `.gitignore` covered `.env` had keys slightly more often (…; V = …). One reading is that teams relied on the ignore rule and then put the real key in the template. We checked this by …" (then add the cross-tab from M12) |
| 285 | "We have no baseline ..., so we cannot say how unusual this is; with agents writing much of the code ..., such artefacts may be cheap to produce. We did not measure whether the tests run or pass, so their presence says nothing about quality, ..." | "Without a baseline from events without agents, we cannot say whether these rates are high. What the data do show is narrower: most active repositories contain test files, but we did not run them, so they show an intention to test, not working tests." |
| 291 | "The data do not explain this. Possible factors include the audience teams wrote for, the language of the tasks, and the language in which teams worked with the agents." | "One factor we could check is the task language: [README language by track, e.g. Khattama, which involves Kazakh audio]. The audience and the language of prompts need participant data." |
| 294 | "...and matter more when an agent writes configuration files quickly." | Delete unless M12's check supports it. If it does: "In [n] of the key-bearing repositories, the file was created in an agent-signed commit." |
| 297 | "Three issues would have biased our results had we not checked them: ... such details can change basic counts, and they are easy to miss when a first analysis is produced quickly." | "Three details changed our counts: a second organiser account (\NValidationTemplateFixes{} repositories wrongly active), commits reachable only through pull-request refs ([117] repositories), and duplicate registrations (\NDupReposExclGeneric{} repositories)." |
| 303 | "A repository is a registration, not a person or necessarily a team. Commit counts measure activity, not effort or quality. ..." | Write connected prose that pairs each threat with the claim it limits and with its mitigation. For example: "Because a repository stands for a registration, all rates are per registration; we make no claims about individuals." |
| 324 | "Because the organisers of HackAlem AI created a repository for every registration, the organisation records the full path from registration to code ..." | Open with the answer to the thesis, not the premise (Section 9.2). |

**Rhythm.** Vary sentence length in the Results. Lead each paragraph with the comparison that answers the RQ and send lists to the table. In the Discussion, use three subsections, each with 2–3 paragraphs of different lengths, rather than six bolded blocks of the same size.

## 10. Measurement consistency

1. **Decimals in figures.** The style guide says "whole numbers in figures". Fig. 2a ("34.4%", and "100.0%"), Fig. 4 ("76.9%") and Fig. 5 ("87.0%") use one decimal. Fig. 3b's legend uses whole numbers ("69%", "31%"). Pick one rule. I suggest one decimal throughout to match the text, and dropping "(100.0%)".
2. **"per cent" versus "%".** "per cent" at l. 167 and l. 235; "%" everywhere else.
3. **CI format.**
   - "(95% CI 1.714–2.058)" and then "(1.082–1.265, n = 2,570)" at l. 209;
   - "(95% CI 59–64)" and then "(8–10)" at l. 222;
   - "(95% CI 74.5–79.1)" at l. 235;
   - "median 1,477 words, 95% CI 1,395–1,568", with no parentheses, at l. 252.
   - Use "(95% CI a–b)" every time, or define the format once ("intervals are 95% CIs") and write "(a–b)" consistently.
4. **CIs promised but absent.** l. 197 says every proportion carries a Wilson CI, but only tests (l. 235) has one in the text. Either put the CIs in a table or say where they are.
5. **Spread for medians.** Median + IQR at l. 222 ("interquartile range 10–35") and l. 248 ("interquartile range 21–561"). Median + bootstrap CI at l. 222 (first and last commit) and l. 252. Median alone at l. 248 ("28 vs. 16", "5 vs. 4") and in Table 2. Use "median (IQR)" to describe distributions and add a CI only when a median is compared or estimated. Use the abbreviation "IQR" after first use.
6. **Denominators** (see M3). 1,254 (l. 235–265, Fig. 4) versus 1,057 (l. 222–224, l. 248, l. 276) versus 984 (Table 2). Fig. 1(e) conflicts with l. 164. Fig. 2a "984 (27.0%)" versus l. 207 "984 (93.1%)". Commit denominators are 31,955 (all team commits: l. 246 "12.5%", l. 248 "36.6%", Fig. 5) versus 30,418 (window commits: rhythm). "Non-merge commit" (l. 248) has no n given.
7. **n notation.** Figures write "n=1,185" and "n=758" without spaces; the text writes "$n = 2,570$".
8. **p values.** "p < 0.001", "p = 0.062" and "p = 0.008" are formatted consistently. "Holm-adjusted" appears only at l. 248. The tests at l. 209, l. 235, l. 265 and l. 276 do not say whether they are adjusted.
9. **Statistic symbols.**
   - χ² is given with df (l. 209, l. 235), but the Kruskal–Wallis H has no df (l. 276) and no effect size.
   - "Cliff's δ" at first use and "δ" afterwards is fine. "Cramér's V" is not reintroduced in RQ6, which is fine.
   - Odds ratios, V and δ are given to 3 decimals and test statistics to 1. Consider 2 decimals for effect sizes and ORs.
10. **Minutes.** "ten minutes" (l. 222, l. 229) versus "10 min" (Fig. 3a axis).
11. **Dates.** "23 September 2026" in the text, "1 Sep" and "22 Sep" in Fig. 2b (acceptable in a figure), and "September 26, 2026" in the PDF date (US order).
12. **Times.** The 24-hour colon format ("13:00–18:00") is consistent. Good.
13. **Cross-references.** cleveref produces "Figure 2a", "Table 2" and "Section 5" consistently. Good. The captions use "(a)" and the text uses "Figure 2a". This is fine, but the panel titles inside the figures repeat the caption text (item 18 below).
14. **En-dashes** are correct for ranges and names (Mann–Whitney, Kruskal–Wallis). The keywords at l. 50 use "·" separators from the template. Fine.
15. **Spelling** is consistently British: organise, behaviour, artefact, centre, labelling. Good. Keep "artefacts" in the figures (Fig. 4 says "Engineering", which is fine).
16. **Verbal quantifiers** stand next to exact numbers: "Two thirds" (l. 282; 65.6%), "a third" (l. 324; 30.6% or 15.4%), "nearly all repositories" (l. 173; Table 3 has exact values), "almost all before the event" (l. 207; not quantified), "almost none became active" (l. 282; 1.3%), "few name Codex" (l. 246), "Most are OpenAI API keys" (l. 263). Give the number wherever the claim matters.
17. **Artefact names.** "Dockerfile" (l. 235, Fig. 4) versus "Docker files" (l. 285, l. 324). "test files" (l. 235) versus "Tests" (l. 285).
18. **Figure titles.** The style guide says "figures carry no titles". Every two-panel figure has panel titles ("(a) From provisioning to activity"), which the captions then repeat. Either allow short panel labels in the guide or remove them.

## 11. Figures and tables

**As a set.** Fonts (Liberation Serif, 7–8.5 pt), line weights and the Okabe–Ito palette are consistent, and the PDFs are vector. The main problem is **colour semantics**. Vermilion means verification (Fig. 1), the organiser batch (Fig. 2b), the deadline and the late-surge cluster (Fig. 3), agent footprint (Fig. 4), Kazakh (Fig. 5) and "still in final version" (Fig. 6). Blue means data stages, Russian/Cyrillic, the steady cluster and engineering. `paper_style.py` itself says "Colour follows the entity". Fix one mapping: blue for the main series, vermilion only for risk, the deadline or exceptions, and grey for context.

**Fig. 1 (overview, TikZ).** This is a pipeline of four bullet-list boxes plus an RQ row. It is text-heavy (well over 100 words), it repeats Table 1 and the Methods, it contains an unsupported claim ("All reported numbers recomputed by separate code") and the wrong RQ7 denominator, it hyphenates "Documen-tation" in a chip, and its arrow from (d) to (e) enters at an odd place. At NeurIPS or ICML level, Fig. 1 carries the *idea* of the paper. **Suggestion:** replace it with a two-part conceptual figure.
- Left: "listing-based samples see only the tip" versus "provisioned census", drawn as nested areas 3,649 → 1,254 → 1,057 → 984, with the batch and the duplicates shaded. This also replaces Fig. 2a.
- Right: the unit of analysis for each RQ (repository, commit, file or finding) with its n, and the known mandate (Codex) set against the observed traces.
- Keep it under about 40 words, with no bullet lists and one colour meaning.

**Fig. 2.**
- Panel (a) duplicates the text and has an x-axis running to 5,000 with only 3,649 at most. Merge it into the new Fig. 1 or drop it.
- Panel (b) is good. Add a note or label for the two repositories created on 23 Sep that are excluded, and add the no-batch estimate.

**Fig. 3.**
- Panel (a) works. Add a dotted reference for a uniform rate, or show the cumulative share.
- Panel (b) presents weak clusters (M9). Replace it with a histogram or ECDF of each team's last-hour share, with reference lines at 20% (uniform) and 50% (majority). That supports the corrected abstract claim directly.

**Fig. 4.** A dot plot with CIs is a good choice.
- Recompute on active repositories (M3).
- "Pull-request refs" should not sit under "Agent footprint" without justification.
- The legend sits inside the data area next to the last row.
- **Better:** split the agent traces into their own panel as a *trace type × tool* matrix (context file, signature, branch; Codex, Claude, Cursor, other), or an UpSet plot of trace co-occurrence. That figure would carry the measurement contribution (M5, M11).

**Fig. 5.** Two stacked bars with 0.1–0.4% slivers carry little information, and the legend conflates language with script. Replace it with a small table, or give the figure a real comparison: README language *by track* as small multiples, which would test the task-language explanation raised at l. 291.

**Fig. 6.** The two panels use different units (repositories versus occurrences); say so in the caption. Panel (b) could become the cross-tab of file type × `.gitignore` coverage that supports the argument at l. 265.

**Tables.**
- Table 1: shorten (see minor 4).
- Table 2: split the event facts from the results (see minor 5). Add the unmatched row. Add README-language and deployed-link columns, which the plan promised for RQ7.
- Table 3: fine, but move it to the appendix in the journal version.

**New table (strongly recommended): "Answers to the research questions".** Columns: RQ | unit and n | answer in one sentence | key estimates with 95% CIs | Figure/Table. Place it at the end of the Results or the start of the Discussion. It also absorbs the number lists from l. 235, l. 248 and l. 252.

**Captions.** Most are short and not self-contained. Fig. 5's caption is 9 words with no n and no definition of the categories. Fig. 3's caption does not say that "share" is per team or what the clusters are. Each caption should state the unit, n, what the error bars show and the one thing the reader should see.

## 12. Title, abstract, keywords and contributions

### 12.1 Title options

1. **Every Registration a Repository: A Census of 3,649 GitHub Repositories from an Agent-Mandated Hackathon**
2. **What Repositories Reveal About Agent-Assisted Work: Evidence from a Complete Hackathon Population with a Required Coding Agent**
3. **Required to Use Codex: Participation, Work Timing, Agent Traces and Credential Leaks in 3,649 Hackathon Repositories**

I recommend option 2 for BDCC or MAKE, because it states the thesis, and option 1 for arXiv. For the journal, "agent-mandated" is more precise than "agent-assisted".

### 12.2 Abstract outline (at most 200 words for MDPI; use macros, invent no numbers)

1. **Context (1 sentence):** coding agents write much of the code in new projects, and researchers increasingly measure their use from repository traces.
2. **Gap (1 sentence):** repository studies see self-selected projects and do not know which agent developers used; hackathon studies of generative AI are small and qualitative.
3. **Setting (1–2 sentences):** HackAlem AI (\eventdate) was a five-hour event with Codex required; the organisers provisioned a public repository for every registration (\NReposTotal).
4. **Method (1 sentence):** full-history mirrors, validated against the GitHub API, analysed with a pre-specified plan.
5. **Results (4 sentences, one per RQ):**
   - population: \NReposActive{} (\NPctActive\%) active; the organiser batch and duplicates;
   - process: last-hour share \NPctLastHour\% and the team-level majority-last-hour share; Claude-signed commits (\NAgentSignedByKindClaude) against Codex-signed commits (\NAgentSignedByKindCodex) under a Codex mandate;
   - product: test files in [active-denominator %]; README language \NReadmeRussianPct\% Russian and \NReadmeKazakhPct\% Kazakh;
   - risk: OpenAI-key strings in \NReposOpenaiKeyN{} repositories, \NOpenaiKeyFilesEnvExample{} of \NOpenaiFindings{} occurrences in `.env.example`.
6. **Implication (1–2 sentences):** trace-based measures of agent use reflect tool defaults, and rates depend on how the population is provisioned; organisers can provision repositories after check-in and ship placeholder-only templates.
7. **Availability (half a sentence):** dataset and pipeline released.

**Keywords:** hackathons; AI coding agents; human–AI collaboration; mining software repositories; complete-population study; credential leakage; OpenAI Codex. Drop "developer behaviour", which is too generic, and use the same term for secrets as the headings do.

### 12.3 Contributions (rewritten, distinct from findings, mapped to RQs)

- **C1 (data, all RQs).** A census of all 3,649 repositories provisioned for one agent-mandated, fixed-deadline hackathon, with full history across all refs, released as a derived dataset with hashed identifiers and a pipeline that regenerates every reported number.
- **C2 (RQ1).** Participation estimates on a known denominator, with and without an organiser-created batch and duplicate registrations, showing how provisioning practice changes participation rates.
- **C3 (RQ2).** A test of trace-based agent detection against a known mandated tool: how often context files, signatures and branch names reveal the required agent, and how often they reveal a non-required one.
- **C4 (RQ3–RQ4).** Population-level prevalence, with CIs, of engineering artefacts, documentation language and credential exposure in agent-assisted prototypes, and the repository set-ups associated with exposure.
- **C5 (practice).** Evidence-linked recommendations for organisers (provisioning, templates, push protection) and a checklist for researchers mining organiser-created repositories (template audit, all-ref mining, denominators).

## 13. Venue ranking

I state impact factors and quartiles for none of these; check the current JCR and Scopus quartiles before choosing. The review-speed figures come from journal pages as surfaced in search results on 27 Sep 2026; verify them on the journal sites.

| Rank | Venue | Fit now | What the paper must add | Review speed (as far as verified) |
|---|---|---|---|---|
| 1 | **Empirical Software Engineering** (Springer) | Best topical fit: an MSR-style census with measurement lessons | The Robbes et al. positioning; the trace-detection test (Idea 2); a baseline (Idea 3); a replication package with DOI | Springer page reports a median of about 24 days to first decision (verify); full review rounds usually take longer |
| 2 | **Big Data and Cognitive Computing** (MDPI) | Fits if framed as a large-scale human–AI study | A thesis on human–agent work; the homogenisation or outcome analysis (Ideas 1 and 4); an abstract of at most 200 words; AI-use statements in Methods and Acknowledgments | MDPI states a median first decision of about 23 days (H1 2026) |
| 3 | **Machine Learning and Knowledge Extraction** (MDPI) | Weak now; fits only with a real ML or extraction contribution | The rule-based versus LLM versus human extraction benchmark and the PU-learning estimate of agent-authored commits (Idea 5) | MDPI pages report roughly 21–26 days to first decision (verify) |
| 4 | **Journal of Systems and Software** (Elsevier; research or "In Practice" track) | Good for the organiser and researcher lessons | Quantified lessons, the baseline and the security linkage | Check the journal page |
| 5 | **IEEE Access** | Accepts descriptive empirical work | Mainly M1–M4 and M8; a clear contribution statement | Check; usually fast |
| 6 | **Computers in Human Behavior: Artificial Humans** or **International Journal of Human-Computer Studies** (Elsevier) | Only with human data | A consented participant survey or interviews linked to repositories (Idea 10) | Check |
| 7 | **IEEE Transactions on Learning Technologies** | Weak: no learning outcomes | An education framing plus outcomes (jury results, participant level) | Check |
| Data | **Scientific Data** (Nature; Data Descriptor), **Data in Brief** (Elsevier) or **MDPI Data**; also the MSR Data and Tool Showcase track | Good for the dataset itself | Scientific Data wants no results or analyses in the descriptor and requires a repository with a persistent identifier (DOI); a data paper needs a schema, a validation section and usage notes | Check |

**Suggested path.** Post on arXiv now (after M1, M3, M4 and M10). Then send the journal version with Ideas 1–3 to EMSE, or to BDCC if the author prefers MDPI's speed, and send a separate Data Descriptor to Scientific Data or Data in Brief. Do not split the analyses across the two papers: the descriptor must carry no results.

## 14. New ideas that would lift the paper to Q1 (feasible with the existing data and the 1 Oct winners list)

1. **A pre-registered jury-outcome analysis. This is time-critical: register before 1 October.** Register the hypotheses and analysis on OSF now, while the winners are still unknown. The core hypothesis is the "cheap signals" one: juries reward artefacts that agents make cheap (tests, Docker, long READMEs, deployment links) no more than chance within track. Other variables: work rhythm, agent traces and LLM SDK use. Use track-stratified permutation tests or a conditional logistic model, with honest power statements given the small number of winners. This gives the paper an outcome variable, which it currently lacks. Effort: S to register, M to analyse.
2. **The mandate as ground truth for agent-trace detection.** Apply the published heuristics (Robbes et al., MSR 2026, doi:10.1145/3793302.3793375; TOSEM 2026, doi:10.1145/3822180) to every active repository. Report the share flagged by each heuristic and by their union, broken down by tool (Codex, Claude, Cursor), and show co-occurrence in an UpSet plot. If compliance with the mandate is assumed, the flagged share bounds the recall of trace-based adoption studies. If it is not assumed, the Claude traces measure non-compliance. Either way, this is a result no other dataset can give. Effort: S.
3. **A baseline using the same pipeline.** Sample repositories from HackRep (Halmans et al., MSR 2026) or Devpost-linked projects (as in Mahmoud et al., EMSE 2022), matched on event length (48 hours or less) where possible, from before 2022 and from 2024–25 without an agent mandate. Compare test, Docker and CI prevalence, README length and language, commit timing curves and secret findings. This turns "common" and "long" into comparative findings. Effort: M–L.
4. **Homogenisation within tracks.** Measure how similar the teams on the same task are: README embeddings and heading sets (MinHash), dependency Jaccard, file-tree structure. Compare against the baseline, and relate similarity to jury outcome. This connects the paper to the AI-homogenisation literature (Doshi and Hauser, *Science Advances* 2024, doi:10.1126/sciadv.adn5290; Anderson, Shah and Kreminski, C&C 2024, doi:10.1145/3635636.3656204) and gives BDCC readers a cognitive-computing angle. Effort: M.
5. **A human-labelled extraction benchmark plus a PU-learning estimate of agent-authored commits** (for MAKE). Double-code a stratified sample of about 200 repositories for track, README language (which also closes the pending item at l. 191), "runnable" and agent involvement. Compare rule-based with LLM-based extraction, as already promised at l. 324, and report Cohen's κ. Then treat signed commits as labelled positives and the rest as unlabelled, and estimate the share of agent-written commits with positive-unlabelled learning (Elkan and Noto, KDD 2008, doi:10.1145/1401890.1401920; Bekker and Davis, *Machine Learning* 2020, doi:10.1007/s10994-020-05877-5). Include a sensitivity analysis for the bias that arises because only Claude signs by default. Effort: M.
6. **Security linkage.** Check whether the key-bearing commits and the commits that created `.env.example` were agent-signed, cross-tabulate against `.gitignore` coverage, and run static analysis (Semgrep or Bandit) on the final states for vulnerability classes, linking to Perry et al., CCS 2023 (doi:10.1145/3576915.3623157) and the vibe-coding security papers already cited. Never test keys. Effort: S–M.
7. **Do the tests run?** For a stratified sample of about 100 active repositories, run the included tests in a sandbox and report the shares that collect, run and pass. This turns "test files present" into a quality measure. Effort: M.
8. **Better timing models.** A survival model for time to first commit (the median of 61 minutes is unexplained), with covariates such as `AGENTS.md`, stack and track; a mixture model or distributional summary in place of k-means; and a changepoint analysis of the event-wide curve. Effort: S–M.
9. **Language and LLM support.** Relate README and commit language to track and task language (Khattama involves Kazakh audio), and discuss the results against evidence on LLM performance in Kazakh (Togmanov et al., KazMMLU, ACL 2025, doi:10.18653/v1/2025.acl-long.701). Still to find: studies of multilingual README practice on GitHub. Effort: S.
10. **Participant data, for an HCI venue.** A short, ethics-approved survey of participants who consent to link their answers to their repository (tool choice, prompt language, reasons for using Claude under a Codex mandate). Effort: L.

**Still to find:** computing-education studies that mine complete, instructor-provisioned cohorts of GitHub Classroom repositories. These are the nearest precedent for the census design, and the "first" claim should be checked against them.
