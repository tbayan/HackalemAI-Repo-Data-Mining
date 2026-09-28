# Round 3: quick pre-submission review for MDPI BDCC

Date: 2026-09-28. Scope: main.tex (line numbers below refer to it), rendered main.pdf (17 pages), facts_paper.json, references.bib, reference_audit.md.
Automated checks run: `checks/lint_banned_words.py` (0 hits), `checks/check_numbers.py` (0 unapproved literals), `checks/check_citations.py` (61/61 cited, 0 errors). Abstract: about 186 words (limit 200).

**Decision: minor fixes.** The numbers in the PDF match facts_paper.json wherever I checked them: all subtotals add up, and I recomputed the Cramér's V values, a Wilson interval and ε² by hand. The equations are correct: s_i = ℓ_i/c_i, the even share of 20%, and ε² = H/(n−1) (Tomczak & Tomczak). Three things would get an MDPI editor's attention at once, and all are quick to fix: a visible placeholder in the Data Availability Statement, the arXiv "Preprint" template, and internal audit notes printed in the reference list. Beyond those, there are one factual inconsistency, several claims that go further than the evidence, and repetition between sections.

---

## 1. Unsupported, overstated or inconsistent sentences

| # | Line | Current text | Problem | Suggested rewrite |
|---|---|---|---|---|
| 1.1 | 323 | "Its errors lay in READMEs it called Kazakh (16/20 confirmed; the others were Russian) or mixed (2/6 confirmed)" | **Inconsistent with the data.** 69 of 80 agree, so there are 11 errors, but Kazakh and mixed together account for only 8 (4 + 4). facts: `agree_english = 22/25`, `agree_russian = 29/29`. | "Its errors lay in READMEs it called Kazakh (16 of 20 confirmed; the others were Russian), English (22 of 25) or mixed (2 of 6); all 29 it called Russian were confirmed." |
| 1.2 | 63 | "The organisers' actions account for most of the gap between repositories and activity" | Causal wording, although line 307 says "We do not know why the organisers archived…". The supporting share is only 56.8% (446 archived + 1,026 inactive batch = 1,472 of 2,592 inactive repositories). | "More than half of the inactive repositories (1,472 of 2,592) had been archived by the organisers before the event or created in an evening batch that stayed almost unused." Put the number into facts/numbers.tex. |
| 1.3 | 181 | "Most of the distance … thus lies in repositories that were closed or barely used before the event started." | The batch was not "barely used before the event started"; it went unused *during* the event. This also repeats 1.2. | Delete the sentence. If you keep it: "…lies in repositories archived before the event or created in the evening batch." |
| 1.4 | 63, 267, 310 | "Codex commits were seldom signed" / "Because Codex seldom signed its commits" / "in these repositories Codex commits were seldom signed" | The study cannot identify Codex commits, only signatures. What was actually observed is that Codex signatures were rare. | "Codex signatures were rare (1.5% of active repositories; 3.3% of those whose README named Codex)". At 267: "Because Codex signatures were rare, this does not show…" |
| 1.5 | 310 | "a known required tool shows its size and its direction in one setting" | Overclaims. Line 207 correctly says these shares are "not the recall of the traces over all users", so the study cannot give the *size* of the problem. | "…a known required tool makes its direction visible in one setting." |
| 1.6 | 310 | "Estimates such as those of Robbes et al., which combine several traces, are less exposed" | Asserts something the paper did not measure. | "…may be less exposed…" |
| 1.7 | 48 | "reproduced the core counts independently" | The recount is a second script by the same author (line 144), so "independently" overstates it. | "…and reproduced the core counts with a separate script." |
| 1.8 | 48 | "29.0% of all repositories but 48.2% of the rest" | "the rest" is ambiguous. | "…but 48.2% of the 2,163 that were open and not in the batch." |
| 1.9 | 65 | "exposed credentials of agent-assisted prototypes" | 45.0% of active repositories carry no agent trace, so calling all of them agent-assisted is an assumption. | "…of prototypes built under an agent requirement and one deadline." |
| 1.10 | 83 | "report velocity gains, largest when the agent is the first AI tool" | He et al. [7] report short-term, transient gains (their title says "Short-Term Velocity"). | "report short-term velocity gains, largest when…" |
| 1.11 | 125 | "because the repositories were archived their content could no longer change" | Organisation owners can unarchive a repository. | "…their content could not change while they remained archived; the final commit of every clone is listed with the data." |
| 1.12 | 207 | "(odds ratio 3.32 for Codex and 29.08 for Claude Code)" | No interval, and the 2×2 table is not defined (naming the tool × which trace?). facts_paper.json has the CIs. | "(odds ratio for naming the tool and carrying any trace of it: 3.32, 95% CI 2.19–5.03, for Codex; 29.08, 10.82–78.19, for Claude Code)". Check the definition against run_analysis.py. |
| 1.13 | 220 | "FastAPI (43.2%), usually served by Uvicorn (43.9%)" | "usually served by" is a conditional claim that no reported number supports, and Uvicorn is found in more repositories than FastAPI. | "…and FastAPI (43.2%) the most common back-end framework, with Uvicorn in 43.9%…" |
| 1.14 | 258 | "…30 of which still hold such a string. By the author dates that Gitleaks reports, all of them were committed during the event window." | "all of them" could mean the 30 repositories or the 77 findings. | "All 77 OpenAI findings have author dates within the event window." |
| 1.15 | 194 | "The teams therefore form a continuum rather than types" | The silhouette of 0.30 is above the null of 0.19, so there is *some* structure. | "A continuum therefore describes the teams better than distinct types:" |
| 1.16 | 307 | "The lesson for research is general." | Vague, and a generalisation from a single event. | Delete it and start the next sentence with "For any study of organiser-created repositories, …" |
| 1.17 | 92 | "Credential leakage has been measured at the scale of all of GitHub, but not for software built under an agent requirement…" | A negative claim that cannot be verified. | "…but we found no measurement for software built under…" |
| 1.18 | 316 | "the measures above would reduce the exposure of keys" | Not tested. | "could reduce" |
| 1.19 | 179 | "activity varied little with the creation date … from 43.2% … to 53.9% (… p = 0.002, V = 0.08)" | A range of 11 points with p = 0.002 does not read as "little". | "activity varied only weakly with the creation date (V = 0.08)…" |
| 1.20 | 55 vs 313 | "nearly all of the committed code" vs "virtually all of the committed code" [1] | The same claim from one source is worded two ways. | Keep it once (line 55) and cut it from 313 (see §2). |
| 1.21 | 323 | "86.2%" (69/80 = 86.25 exactly) | Python rounds half to even. A reviewer who recomputes will get 86.3. | Report "86%", or round half up. |

## 2. Repetition to cut

- **Results preview in the Introduction (line 63).** "446 repositories were archived… 1,040… 21.7%… 46.3%… Keys reached the public history mainly through committed environment files" repeats the abstract almost word for word. Cut the paragraph, or reduce it to one sentence without numbers. The contributions paragraph (line 65) already frames the results.
- **"21.7%" and "46.3%"** appear six times: abstract, line 63, line 205, Table 4, line 310 ("Every team was told to use Codex, yet… only 21.7%… only 46.3%") and the Conclusion. In 6.2, open with the interpretation instead ("If all teams complied, a study based on these traces would have found Codex in fewer than half of the repositories (§5.3).").
- **"73.2%" and "3.3%"** appear in the abstract, line 207, Table 4 and line 310 ("Among teams whose README named the tool, signatures revealed Claude Code in 73.2%…"). Cut them from line 310.
- **"Keys entered the history mainly through committed environment/template files"** appears four times: line 63, the end of line 267 ("The keys therefore entered the public history mainly…"), line 313 ("The exposed keys sat in environment files… committed during the event") and line 332. Keep it in Results and the Conclusion only.
- **"Rates can only be read after organiser actions are reconstructed"** appears three times: line 65 ("a step that studies of organiser-created repositories have to take before any rate can be read"), line 307 ("have to be reconstructed before any rate is read as participation") and line 316 ("all have to be checked before counting"). Keep one, in Implications.
- **Reproducibility** is claimed five times: abstract, line 65, line 144, line 168 ("Every number in the paper is generated from the data by the released scripts") and line 325 ("the headline results can be recomputed from the public files"). Keep line 65 and the Data Availability Statement, and cut the line 168 sentence and the line 325 duplicate.
- **"Tests present ≠ working tests"** appears at line 220 ("We did not run the tests, so their presence shows an intention to test, not working tests"), line 313 ("Whether the tests run or pass is unknown") and line 323. Keep it in Results and Threats.
- **"README naming is not independent of the traces"** appears at line 134, line 207 and line 323. Keep lines 134 and 323.
- **"A repository stands for one registration… no claims about individuals"** appears at line 129 and line 323. Keep one.

## 3. Structure and BDCC format

1. **Data Availability Statement (line 348):** "[pending: archived release with DOI]" is printed in the PDF. Replace it with the Zenodo DOI, and confirm that the GitHub repository and the OSF page (osf.io/bm3je) are public.
2. **Template.** The paper uses the arXiv style: a "Preprint" header (lines 37–38), the title-page date, and `unsrtnat`. Move to the MDPI LaTeX template (`mdpi.cls`, `\journal{BDCC}`), or first confirm that BDCC accepts free-format first submissions. Sections should follow MDPI naming: "Materials and Methods" (not "Methodology") and "Conclusions" (not "Conclusion").
3. **Back matter order (MDPI):** Author Contributions → Funding → Institutional Review Board Statement → Informed Consent Statement → Data Availability Statement → (Acknowledgments) → Conflicts of Interest → (Abbreviations). "Ethics statement" (line 350) is not an MDPI section. Move its content into §4.3 (handling of secrets and disclosure) and §4.1 (salted hashing), or into the IRB statement. Add an Abbreviations list (API, CI, IQR, LLM, SDK). Use CRediT wording for Author Contributions (for a single author: "The author conducted conceptualisation, methodology, …").
4. **Research questions are not carried through.** RQ1–RQ4 are defined at line 61 but never appear again. Tag the Results subsections, e.g. "5.1 Population and participation (RQ1)", or add one sentence per subsection.
5. **§5.2 (timing) is left undiscussed.** The last-hour share and the clustering never come up in the Discussion or the Conclusion, and the time-pressure and procrastination references in §2.3 ([36]–[40], line 86) are never used again. Either add two or three sentences to §6.3 relating the 30.8% median last-hour share and the 79.3% of teams active in four or more hours to [37]–[39], or shorten §5.2 and cut those references. As it stands, RQ2 joins two unrelated questions.
6. **Short or fragmented parts:**
   - §3 "Study setting" is one paragraph plus a table. Merge it into Methods as §4.1 (MDPI "Materials and Methods").
   - Line 173 is a one-sentence Results preamble. Fold it into the first sentence of §5.1.
   - Line 83, "Agents are also evaluated on repository tasks [27,28].", is a stray sentence. Cut it (and the two references) or connect it to the argument.
   - §6.4 Implications mostly restates §6.1–6.2. After the cuts in §2 it will be one short paragraph; that is acceptable if it adds only the recommendations.
   - External validity (line 327) is two sentences. Add one: the README-naming subset (120 and 41 repositories) limits what the detection shares say about all users.
7. **Float placement.** Tables 3 and 4 appear inside the Discussion (pages 10–11). Table 4 is cited at the start of Results (page 6) but typeset on page 11, and it splits a Discussion sentence ("…that the rules did / not require"). Use `[tbp]` and a `\FloatBarrier` before §6, or move the tables to where they are first cited.
8. **Captions that do not stand alone.**
   - Table 2, "Validation and sensitivity checks.": define "earlier table" and "window".
   - Table 4: add "Active: at least one team commit between 13:00 and 18:00 on 23 September 2026; batch: repositories created 18:00–20:00 on 22 September".
9. **Abstract:** it does not mention credentials, but "credential leakage" is a keyword and RQ4 is about credentials. Add, for example: "OpenAI key strings reached the public history of 5.8% of active repositories, mostly through committed `.env` and `.env.example` files." To stay under 200 words, shorten "derived measures with deterministic rules and reproduced the core counts independently" to "and derived all measures with deterministic rules".
10. **Scope framing for BDCC.** Add one clause in the Introduction that places the study as large-scale mining of repository data about AI tool use, so the editor sees the fit. Citing [19] (BDCC 2024) already helps.
11. **Wording:** line 127 renders as "created between 18:00–20:00". Use "between 18:00 and 20:00", or change `\batchwindow`.

## 4. Figures

- **Figure 5:** the row "Mentions a coding agent, 24.9% (257 of 1,033)" is not defined in Methods and is not mentioned in the text. facts: `rq3.readme_mentions_agent`. It also has exactly the same value as the Claude Code trace share (24.9%), which invites confusion. Define it in §4.2 and cite it in §5.4, or drop the row. The three groups (artefacts, LLM, README) are separated only by gaps; add small group labels as in the other figures.
- **Figure 2b:**
  - The caption says "filled" for open repositories, but the markers are hollow circles with a pale fill.
  - The grey batch marker is missing from the legend.
  - No diamond is shown for "22 Sep (other)" because it coincides with the circle; the caption should say so.
  - The n labels are the counts of open repositories, and they sum to 2,161, not 2,163, because the 2 repositories created on 23 September are excluded (facts: `creation.sep23`). State this in the caption.
- **Figure 4:** in (b), value labels collide with error-bar caps ("61.0", "73.2", "90.2"). In (a), the Claude markers at 0.0 and 0.5 are cut by the axis. The Claude orange is saturated, while the other figures use pastel fills with darker edges. Use a pastel orange with a darker edge to match the Figure 1 palette.
- **Figure 6a:** the rows add up to 80, but only 73 repositories are affected. Add "a repository can appear in more than one row" to the caption.
- **Figure 1:** the output boxes ("Process and agent traces", "Product") do not match the section titles or RQs. Rename them, e.g. "RQ1 Population", "RQ2 Work and traces", "RQ3 Artefacts and READMEs", "RQ4 Credentials".
- Figures 2, 3 and 6 are consistent with each other and legible at print size. Fonts match the text.

## 5. References

- The rendered list contains internal audit notes. Remove them from the `note` fields at references.bib lines 382, 391 and 404:
  - [21]: "States that commits get a git trailer such as Co-Authored-By by default."
  - [25]: "States that Codex reads AGENTS.md files before doing any work."
  - [57]: "Peer-reviewed; no DOI registered. Full text read 27 September 2026; gives the rank-based epsilon squared…"
- arXiv DOIs are in the .bib but are not printed for [1], [2], [18], [26], [29], [33], [48], [49], [50] and [60], while [27] and [45] print theirs. Your rule is "DOI where one exists", so print 10.48550/arXiv.* for all of them. The MDPI .bst will do this.
- [60]: "Davide Taibi" appears twice in the author list (bib line 288). The duplicate comes from the DataCite metadata; remove it.
- [55] Prana et al.: EMSE 24(3) is the 2019 issue, so use the year 2019, not "October 2018".
- [13]: the title is missing its colon ("The Secret Life of Hackathon Code: Where does it come from…").
- [9] and [14] (EMSE): add the article numbers.
- `unsrtnat` prints "page 496–507". The MDPI style will fix this.

## 6. Desk-reject risks

1. Placeholder text in the Data Availability Statement (§3.1 above).
2. A non-MDPI template with a "Preprint" header (§3.2).
3. Internal notes in the reference list (§5).
4. Statements that will be out of date by the time of review:
   - Table 1, line 114: "result pending".
   - Table 1, line 115: "winners are announced on 29 September; awards on 1 October 2026". Update after 1 October, or write "were scheduled for".
   - The title-page date (27 September) is earlier than the disclosure date reported at line 351 (28 September). Confirm that the e-mail and Telegram disclosure was actually sent on that date, and update `\versiondate`.
