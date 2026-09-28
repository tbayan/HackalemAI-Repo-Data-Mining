# Round 4: Reviewer A report for MDPI Big Data and Cognitive Computing (BDCC)

Manuscript: "Measuring AI Coding Agent Use from Repository Traces: Evidence from a Hackathon Where Codex Was Required" (single author; 18 pp. PDF dated 28 September 2026).
Material read: rendered `latex/main.pdf`, `latex/main.tex` (line numbers "L" below refer to it), the five data figures and the Fig. 1 preview, `analysis/facts_paper.json` (to check numbers and rule names), `src/extract_stack.py` (the test-file rule only), and the round 1–3 reviews. I do not repeat round-3 points that have been fixed. The few that are still open are grouped in item W12.

**Recommendation: minor revision.** The measurement work is careful and well validated. The remaining problems are about interpretation: what the headline tool contrast can support, how `AGENTS.md` is classified, and how the credential rules are named. Two small checks and some rewording would fix them. None of this needs new data collection.

---

## 1. Summary

The paper studies HackAlem AI, a five-hour in-person hackathon in Astana (23 September 2026). The organisers created a public GitHub repository for every registered team in advance, and the rules required every team to use OpenAI Codex. The author mirrored all 3,649 organiser-created repositories with full history, built feature tables with deterministic rules, and checked them against the GitHub API and against a separately written recount. There are four research questions: participation on a known denominator (RQ1), timing of work and agent traces (RQ2), artefacts and documentation (RQ3), and credential exposure (RQ4). The main findings are these:
- organiser actions (446 repositories archived before the event, and an evening batch of 1,040 that stayed almost unused) move the activity rate between 29.0% and 48.2%;
- traces specific to the required tool appear in 21.7% of active repositories, or 46.3% counting `AGENTS.md`;
- among teams that name a tool in their README, commit signatures reveal the non-required Claude Code far more often than Codex;
- OpenAI key strings reached the public history of 61 repositories, mostly through `.env` and `.env.example` files.

## 2. Novelty and contribution

Relative to the closest work, the contribution is clear and limited to what one event can show:

- **Trace-based adoption studies.** AIDev [2], Robbes et al. [3,4], Agarwal et al. [6], He et al. [7] and the context-file study [5] measure agent use in self-selected projects where neither the tool nor the sampling frame is known. This paper adds a setting where both the frame (every organiser-created repository, including empty ones) and the intended tool are fixed in advance. As far as I know this has not been reported before. It gives a concrete, if single-event, check on how much signature-based detection depends on a tool's defaults. This is the paper's main scientific contribution.
- **Hackathon repository studies.** Imam/Mahmoud et al. [13,14] and HackRep [15] start from listed projects. Here the population includes registrations that produced no code, and the RQ1 result shows why that matters. This is a real but modest methodological point.
- **Generative AI at hackathons.** [16–19] use interviews, surveys and project scoring at single events. This is the first census of a whole event's repositories under an agent requirement.
- **Credential leakage.** [41,44,45,48] cover GitHub as a whole or mobile apps. The finding here is descriptive and specific to the event (`.env.example` as the main route). It is useful, but it is secondary to the thesis.

The thesis (L63: rates depend on how the population was formed and on tool defaults) is stated clearly, and RQ1 and the trace part of RQ2 support it directly. RQ3, the timing part of RQ2 and much of RQ4 are descriptive and only loosely tied to it. The contribution would be easier to see if those parts were shorter (W8).

## 3. Strengths

1. **A known denominator and a known intended tool.** This is a strong natural setting for testing trace heuristics, and the author uses it for exactly that rather than for broad claims about productivity.
2. **Validation is well above the norm for a mining paper** (Table 2):
   - clone commit counts equal the API counts for 3,649 of 3,649 repositories;
   - a separately written recount reproduces three core counts for every repository;
   - the template commit is identified by a rule that does not depend on the author account, and an audit found the second organiser account;
   - the results are stable when the window is shifted or author time replaces committer time;
   - κ is reported for the track labels and for the language rule.
3. **Organiser actions are reconstructed and not mistaken for participation.** The archive bursts (15, 17 and 22 September) and the batch creation rate (up to 15 per minute, against at most 8 on earlier days) are documented, and Fig. 2b shows the effect clearly.
4. **Honest statistics.** The census-inference stance is stated, with a citation to Baltes and Ralph. Wilson intervals, effect sizes (V, δ, ε²) and small-cell counts are reported, the planned tests form a Holm family, and exploratory analyses are labelled throughout. The k-means result is compared with a null model and is not over-read.
5. **Careful handling of secrets and personal data:**
   - values are never stored, printed or tested;
   - authors are counted through a salted hash;
   - findings are released only as aggregates;
   - the organisers were told before publication.
6. **Reproducibility.** Every number is a macro generated from the data, and the release includes a pseudonymised dataset, a list for re-collecting the data and a deviations log.
7. **Restrained wording.** Most claims have been checked against their sources, and the Discussion keeps to what the data support (for example, Claude Code traces are not called "breaches").

## 4. Weaknesses and required changes

Items W1–W5 affect scientific soundness. W6–W12 concern presentation and format.

**W1. The headline contrast compares two reference groups that are not alike (Abstract L49; §4.3 L205; §5.2 L310; Conclusions L336).** The abstract's key numbers are the signature rates among teams whose README names each tool: 73.2% (30/41) for Claude Code and 3.3% (4/120) for Codex. But naming means different things for the two tools. Codex was required and presumably judged, so teams had a reason to name it whether or not they used it much; naming it may be a compliance statement. Naming a non-required tool is voluntary and probably comes from heavy users, whose READMEs the agent itself may have written. The gap therefore mixes tool defaults with what "naming" means. The paper already says the naming reference is not independent of the traces (L134, L207, L327), but it does not discuss this asymmetry. The analysis is also exploratory and was added after the plan (L205), yet it is the only RQ2 number in the abstract besides the overall shares.
*Fix:*
- Add the asymmetry to §5.2 and to Threats (construct validity).
- In the abstract, either label the comparison as exploratory or report the less extreme contrast of any tool-specific trace (90.2% vs 32.5%) next to the signature contrast.
- Consider one more reference group that is symmetric by construction, for example repositories that name both tools, or repositories with at least one trace of each tool, and compare signature rates within them.

**W2. The trace-producing defaults of Codex are inferred, not established (§3.3 L134; §5.2 L310).**
- The paper says "we found no documented default for Codex".
- Its own data show that Codex traces are mostly `codex…` branch names (18.7%) and author names "Codex" (3.1%; 195 of the 331 Codex-naming commits).
- Which Codex surface (CLI, IDE extension, cloud tasks, GitHub connector) produces which of these traces is not stated.

The argument that "tools that sign by default are counted more completely" is the paper's central mechanism, so it should rest on evidence rather than on the absence of documentation.
*Fix:* add a short controlled check, which is cheap and needs no new data from participants. Run each Codex surface and Claude Code once with default settings in a scratch repository, record which trace each leaves (trailer, author, branch prefix, PR), and report the result as a small table with tool versions and dates. If this is impossible, cite the Codex documentation on branch naming and commit authorship, or say explicitly that the mapping from surface to trace is unknown, and weaken L310 to match.

**W3. `AGENTS.md` is classed as non-specific mainly on evidence that cannot show this (§3.3 L134; §4.3 L203).** The paper argues that the file "is not specific to Codex: it was present in 59.7% of the repositories with a Claude Code trace, against 24.6% of the others". When Codex is required, co-occurrence with Claude traces is exactly what teams using both tools would produce. It therefore fits the view that `AGENTS.md` does indicate Codex use as well as the view that it does not.
*Fix:*
- Base the non-specificity on documentation: which agents read or generate `AGENTS.md` in 2026 (the open AGENTS.md convention and the vendors' documentation for Cursor, Copilot, Gemini and so on). Check whether Claude Code creates or reads it by default.
- Present the co-occurrence as descriptive, not as evidence.
- This also affects how the "21.7% vs 46.3%" pair is read. If `AGENTS.md` is mostly Codex-driven here, 46.3% is the better estimate. Say which reading the paper prefers, and why.

**W4. Some credential categories are misnamed, and the platform context is missing (§3.4 L139–141; §4.5 L258; Fig. 6a; §5.4 L320; Ethics L358).**
- *"Provider-specific" rules.* The 117 plausible findings in 73 repositories (Table 4, "Provider-format strings") include the Gitleaks rules `jwt`, `curl-auth-header` and `curl-auth-user` (facts: 3, 8 and 2 repositories). These are not provider key formats: a JWT may be a test token from the team's own application. Rename the category "format-specific (non-generic) rules" in the text, Table 4 and the Fig. 6a title, or restrict "provider key formats" to OpenAI, Google Cloud, Stripe and Telegram and report the other rules separately.
- *Plausibility of the OpenAI strings.* The placeholder filter is not validated (acknowledged at L327). Without printing or testing any value, you can report how many of the 77 OpenAI strings match the current key structure (prefix family and length). This is a cheap plausibility check that does not involve testing keys.
- *GitHub protections.* GitHub runs secret scanning with provider partners, and OpenAI keys are, to my knowledge, among the partner patterns: exposed keys are reported to the provider and may be revoked automatically. Push protection is also, to my knowledge, on by default for pushes to public repositories. Please verify both points and discuss them. They affect (i) the "upper bound on usable keys" reasoning in the threat model, (ii) the question of how 61 repositories got past push protection (bypass, pattern coverage, or strings that are not live keys), and (iii) the recommendation in L320 to enable push protection, which may already have been on.
- *Disclosure timing.* The organisers were told on 28 September, and the preprint is dated 28 September. Please report the outcome (acknowledged? keys revoked?). If the organisation name (`BAITC-Hacks`, Table 1 L119) stays in the paper, consider waiting a reasonable period, or until revocation is confirmed, before public posting. Anyone can re-run Gitleaks on a named, archived organisation.

**W5. A plausible explanation for the pre-event archiving is missing (§4.1 L175–179; §5.1 L307).** From the reported numbers, 157 of the 446 repositories archived before the event (35%) already held team commits from before it. Among the 3,203 open repositories, only about 210 did (173 active + 37 inactive with only pre-event commits, about 6.6%, by my arithmetic from facts `rq2.pre_event.repos` and `rq1.outside_only`). §5.1 offers seat allocation and withdrawn or duplicate registrations as possible reasons. It does not mention that archiving went strongly with early work, which fits enforcement of a no-early-start rule or teams that tested and left. *Fix:* report this contrast in §4.1 (one sentence, with numbers generated as macros) and add it to the list of possible reasons in §5.1. You still do not need to know the organisers' motive.

**W6. Say what the data identify about compliance and detection (§5.2 L310).** The sentence "If all teams complied, a trace-based study of this event would have found Codex in at most about half of the repositories" is confusing, because a trace-based study finds 46.3% whatever the compliance. The real point is that recall and compliance cannot be separated. *Fix:* state it directly: "The traces bound the product of compliance and detection: if every team used Codex, the traces recovered at most 46% of that use." You could add an illustrative bound. If detection among README namers (32.5% tool-specific; 71.7% including `AGENTS.md`) were no lower than among all users, the implied share of teams using Codex would be at least about 21.7/32.5 ≈ 67% (or 46.3/71.7 ≈ 65%). The same ratio gives about 28% for Claude Code (24.9/90.2). These are my calculations under a strong assumption; label them as such if used, and show the assumption.

**W7. Track labels come from an "earlier per-repository table" whose method is not described (§3.3 L132; Table 3).** The paper describes how the labels were checked (933/946, κ = 0.98) but not how they were first made: by hand, by rules, by clustering, or with model help. L125 states that "no language model labels or classifies the data". That claim can only be checked if the source of the labels is stated. *Fix:* describe how the earlier table was produced, and cite the public report it came from.

**W8. The scope is wider than the thesis (Title; RQ2 L63; §4.2, §4.4, Table 3).** RQ2 combines two unrelated questions (timing and traces). RQ3 and Table 3 (partners, tasks, README language by track) are descriptive and hardly connect to the argument about measurement. Several exploratory side analyses add length without supporting the thesis:
- k-means with a null model (L192);
- commit size of signed commits (L214);
- conventional-commit subjects (L214);
- `.gitignore` versus keys (L267).

*Fix (recommended, not strictly required):*
- Either split RQ2 into timing and traces, or move timing into RQ3 as "what teams did".
- Move Table 3 and the exploratory analyses to an appendix or the supplementary material.
- Keep in the main text what supports the thesis: population, traces, and the one planned test.

The author wants no redundancy, and this is the largest single saving.

**W9. The test-file measure is broad and unvalidated (§3.3 L132; §4.4 L220; Table 4; Fig. 5).** "Test files" at 87.0% is a headline estimate. The rule (`src/extract_stack.py` L83) counts any file under a `test/` or `tests/` folder, plus `test_*.py`, `*_test.py|go` and `*.test|spec.[jt]sx?`. Fixtures or data under `tests/` count too. Only 39.6% declare pytest. *Fix:* state the rule in the text (one clause), and spot-check a random sample of about 50 repositories, reporting how many contain at least one test function or test case. Alternatively, report "at least one file with a test function" as the measure. The `AGENTS.md`–tests association (L216) depends on this measure too.

**W10. Motivate the planned test (§3.6 L168; §4.3 L216).** The one planned family (`AGENTS.md` against window commits, hours with commits and test files) appears without a reason. *Fix:* add one sentence in §3.6 on why `AGENTS.md` was chosen as the predictor and why these three outcomes.

**W11. Methodological details placed in Threats (L327).** The results of the README-language validation (86.2%, κ = 0.80, the confirmation counts per class, the weighted 98.0%, the Chinese README) are method results. *Fix:* move them to §3.5 or into Table 2, and keep only the resulting limitation in Threats. This also makes Threats much shorter. Note that the "blind hand labels" were made by the author alone, so it is one rater against the rule; say so.

**W12. Items still open from round 3 (short):**
- Abstract L49: "48.2% of the rest" → "48.2% of the 2,163 open repositories outside the batch".
- Contribution 3 (L66): "agent-assisted prototypes" → "prototypes built under an agent requirement" (45.0% of active repositories carry no agent trace).
- L307: delete "The lesson for research is general."
- L177: "activity varied little with the creation date" (p = 0.002, an 11-point range) → "varied only weakly (V = 0.08)".
- L84: "Agents are also evaluated on repository tasks [27, 28]" is a stray sentence. Cut it and the two references, or connect it to the argument.
- L100: "began with an organiser commit" → "was created with", since 34 repositories rewrote their history (Table 2).
- "Hours with commits" (L144, Table 2) is never defined. Define it as the number of the five clock hours with at least one window commit.
- 69/80 = 86.25% prints as 86.2%. Round half up, or report 86%.
- References: [13] is missing the colon in its title; [9] and [14] need article numbers.

## 5. Readability and flow

The English is plain and mostly idiomatic. Sentences are short, jargon is usually defined, and the traditional IMRaD structure is followed. The main problem is density, not style.

- **Abstract, sentence 2** ("Such measurements rarely know which repositories…"): measurements do not "know". Write "Such studies rarely know…" or "…rarely have a complete list of the repositories that could have shown activity, or know which tool developers were meant to use."
- **§2.3 (L87)** has five strands in one paragraph: Copilot productivity, AI at hackathons, vibe coding, computing education and time pressure. [29]–[32], [34]–[36] and [40] are cited only here. Split the paragraph into "AI at hackathons" and "Deadlines and time use", and cut the Copilot and education citations that the Discussion never uses.
- **§2.5 (L93)** opens with "The four strands meet in a gap", which is a little ornate. Write "Taken together, these strands leave a gap."
- **§4.3, first paragraph (L203)** holds 15 or more numbers, and its last sentence runs into the next paragraph. Split it after "…carried no trace of any agent", and put the commit-level shares (11.6%, 87.6%, 331, 195) in their own short paragraph. The same value, 11.6%, is used for two different things in this subsection: signed window commits, and READMEs naming Codex. A reader may take one for the other, so give the denominator each time ("11.6% of window commits", "11.6% of written READMEs").
- **L205** "The README tells what teams chose to state (Figure 4b), in an analysis added after the plan." is awkward. Try "In an analysis added after the plan, we compared the traces with what teams wrote in their README (Figure 4b)."
- **§4.5 last sentence (L267)**, "The keys therefore entered the public history mainly through committed environment and template files during the event.", repeats the opening of the same paragraph. Delete it.
- **§5.3 (L315)**: "The median team made about a third of its window commits in the last hour". The measured value is 30.8%, so write "almost a third" or "31%".
- **§5.3 (L317)**: "Progress of language models in Kazakh has been limited [59]". KazMMLU is a snapshot benchmark and does not measure progress. Write "Language models still perform poorly on Kazakh-language benchmarks [59]".
- **Repetition that remains:**
  - "Tests present, not working tests" appears three times (L220, L317, L327).
  - "README naming is not independent of the traces" appears three times (L134, L205, L327).
  - "A repository stands for a registration; no claims about individuals" appears twice (L129, L327).
  - Keep one instance each, plus the Threats instance where appropriate.
- **Terms to define at first use:**
  - "mirror clone" and "reference" (git ref) in §3.2;
  - "co-author trailer" (one clause in §3.3);
  - "agent service account";
  - "vendored folders".

## 6. Figures and captions

The data figures share one style: pastel fills with darker edges of the same hue, the same serif font as the text, and light grids. Fig. 1 is a clean pastel block diagram in the manner requested. At print width all labels are legible. The main remaining problems are small inconsistencies between figure and text.

- **Fig. 1 (architecture).**
  - Clear, and the RQ labels now match the Results.
  - The "Checks" box still says "independent recount", while the text and Table 2 say "separate recount" (softened in round 3). Change it to "separate recount".
  - The dashed "Known in advance: deadline, required tool" arrow goes into RQ2 only, but the deadline also defines activity for RQ1. Either route it to both, or keep it and add "(deadline defines the window for all RQs)" to the caption.
  - The caption is self-contained and accurate.
- **Fig. 2 (population).**
  - (a) The thin grey sliver at the end of the 1,057 bar (the 14 active batch repositories) is correct but easy to miss. Say so in the caption, or label it "14".
  - (b) No diamond appears for "22 Sep (other)", because no repository created that day was archived beforehand, so the two series coincide. The caption should say so.
  - (b) The n labels are counts of open repositories only; say so.
  - (b) The grey batch marker is explained only in the caption. That is acceptable, but a legend entry would help.
  - (b) The diamonds have no intervals while the circles do. Either add intervals or say they are omitted.
- **Fig. 3 (timing).**
  - Clear. The saturated red deadline line is the one strong accent in the set. That is acceptable, but a darker pastel red would match Fig. 6.
  - (b) The spike at 95–100% (33 teams, 3.1%, whose window commits all fell in the last hour) is striking and not mentioned. Add one clause to the text or the caption, and state the bin width (5 percentage points).
- **Fig. 4 (traces).**
  - The label collisions from round 3 are gone.
  - In both panels the Claude Code row "Any trace incl. `AGENTS.md`" repeats "Any tool-specific trace" (24.9/24.9, 90.2/90.2), because `AGENTS.md` is not counted for Claude. Either drop the Claude marker in that row or add "for Claude Code the last two rows coincide" to the caption.
  - The markers at 0.0 and 0.5 are half clipped by the axis. Set `clip_on=False` or add a small left margin.
  - The caption is accurate. (b) could give n in the caption as well as in the axis label.
- **Fig. 5 (product).**
  - Accurate, and the "(n of N)" labels are helpful.
  - The three groups (artefacts, LLM use, README features) are still separated only by gaps. Add small group headings, as requested in round 3.
  - The x-axis runs to about 115 to make room for labels. That is acceptable, but end the axis line at 100.
- **Fig. 6 (credentials).**
  - The (a) title "Strings matching provider key formats" is inaccurate for "JSON Web Token", "Auth header in curl" and "Credentials in curl" (see W4). Rename it "Format-specific Gitleaks rules", or split the rows.
  - Colour meanings shift between figures. Red means "archived before the event" in Fig. 2 and "still in the final version" here, and blue means "open" or "Codex" elsewhere but "files" in (b). This is minor, but one sentence in a style note, or a neutral hue for (b), would make the colour code fully consistent.
- **Tables.**
  - Table 1 carries two rows that no analysis uses and that will soon be out of date: "Record attempt … result pending" (L117) and "After the event … winners are announced on 29 September" (L118). Cut the record row. Rewrite the second as "jury review 24–28 September; results after this analysis" or update it after 1 October.
  - Table 1's "one per registered team" (L119) states as fact what §3.2 treats as an assumption. Change it to "one per registration (assumed)".
  - Table 3 names two tracks "Special" (T11, T12). Give them distinguishable labels.

## 7. Fit for BDCC and what the editor will ask for

**Fit.** Acceptable. BDCC publishes empirical work on AI systems and data-driven analysis, and it has already published a study of generative AI at hackathons (Sajja et al., BDCC 2024, cited as [19]). The "big data" element is modest: 3,649 repositories and about 30,000 window commits. The fit rests more on the census design, the reproducible pipeline and the released dataset than on scale. One sentence in the Introduction presenting the study as large-scale mining of repository data about AI tool use, together with the dataset contribution, would make the fit explicit for the editor.

**What a BDCC editor will ask for before review:**
1. **MDPI template** (`mdpi.cls`, `\journal{BDCC}`) instead of the arXiv "PREPRINT" style with a title-page date. Back matter in MDPI order: Author Contributions (CRediT wording) → Funding → Institutional Review Board Statement → Informed Consent Statement → Data Availability Statement → (Acknowledgments) → Conflicts of Interest → Abbreviations. Abbreviations currently come first (L339). The "Ethics statement" (L357) is not an MDPI section: move its content into the IRB statement and §3.4.
2. **Data Availability Statement (L355):** the placeholder "[pending: archived release with DOI]" is still printed. Deposit the release on Zenodo and insert the DOI, and confirm that the GitHub repository and the OSF page are public.
3. **Ethics determination.** "Not applicable" is defensible for public repositories. However, the study processes names and e-mail addresses of committers (even if only transiently), releases pseudonymised data derived from them, and deals with exposed credentials. Many editors will ask for a short exemption letter or determination from the institution (Nazarbayev University or Manchester), or at least a sentence explaining why none was sought.
4. **Disclosure outcome** (W4): a sentence on what the organisers did.
5. **Out-of-date statements:** Table 1 "pending" and the announcement dates (L117–118).
6. **AI-use disclosure.** Not flagged, as instructed; the author will add it.

## 8. Ratings (1 = poor, 5 = excellent)

| Criterion | Score | Justification |
|---|---|---|
| Originality / novelty | 4 | A known denominator plus a known required tool is a new and useful test bed for trace heuristics; limited by being one event. |
| Significance of content | 3 | A clear methodological caution for agent-adoption studies. The effect sizes are specific to this event, and much of RQ3/RQ4 is descriptive. |
| Quality of presentation | 4 | Traditional structure, plain prose, consistent figures. Results §4.3 and Threats are dense, and some scope could move to an appendix. |
| Scientific soundness | 3 | Measurement and validation are strong. The headline tool contrast (W1), the Codex defaults (W2), the `AGENTS.md` classification (W3) and the credential categories (W4) need tightening. |
| Interest to readers | 4 | Relevant to anyone who measures AI tool use from digital traces, and to hackathon organisers. |
| Overall merit | 4 | A careful, reproducible, honestly hedged study; publishable once the interpretive points are addressed. |
| English language quality | 4 | Clear, human academic English, with a few awkward constructions (§5). |

## 9. Recommendation

**Minor revision.** W1–W4 are required; each can be handled with rewording plus one small check (a controlled default test for W2, a format-conformance count for W4). W5, W7, W9–W12 and the figure fixes are quick. W8 (moving RQ3 detail and the exploratory analyses to an appendix) is strongly recommended but left to the author. If the controlled test in W2 contradicts the "signs by default" mechanism, the Discussion would need to be revised substantially, and I would then want to see the paper again.
