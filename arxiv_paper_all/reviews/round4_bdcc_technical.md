# Round 4: technical review (Reviewer B, MDPI BDCC)

Date: 2026-09-28. Scope: `latex/main.tex` (line numbers below refer to it), `main.pdf` (18 pages, built 03:48 from the current sources), `numbers.tex`, `facts_paper.json`, `figures/*.png` and `architecture.tex`, `references.bib`, `reference_audit.md`, `public_data_generated/`. The paper does not mention the AI tools used to write it; as instructed, I have not flagged this.

## Verdict

**Minor revision.** The numbers are unusually well controlled. All 166 n/N/% triples in `facts_paper.json` round correctly (half-up), and every Wilson interval matches to ±0.05. I also recomputed about 60 reported numbers from the released CSVs with my own code, not the authors' script. Nearly all of them match. I found two real numerical errors: a pooled median taken over the wrong set of repositories (item 1), and truncated medians in Table 3 (item 2). There is also one internal contradiction, in Fig. 1 against the Methods (item 3). The rest is reporting precision, terminology, reference formatting and gaps in the data documentation.

## 0. Reproduction result

- `.venv/bin/python arxiv_paper_all/analysis/reproduce_public.py` reports **PASS 23 of 23** and exits with 0 in 0.2 s. It only reads files; `git status` is the same before and after.
- `sha256sum -c SHA256SUMS` passes for all 11 files.
- Independent recomputation from `repositories.csv` and `commits.csv` (script in my scratchpad, not in the repository). These match:
  - **RQ1:** 1,043/2,163; 14/1,040; 157; 197/194/157; χ²(3) = 14.9, p = 0.002, V = 0.08; χ² = 608.2, V = 0.41.
  - **Timing:** 30,418; 28.8%; 17:40–17:50; 30.8 (19.4–43.8); 163; 838; 61 (43–94); 9; 19 (10–35); 173/73.
  - **Window shifts:** 1,026/1,040/1,060/1,059; author time 1,057.
  - **Clustering:** silhouette 0.30 with 323 late teams.
  - **Traces:** every count in §4.3 and Fig. 4 (229/489/260; 198/16/33/352; 263/150/179/5; 157/263, 195/794; 202; 20/5/2; 476; 379; 3,541, 87.6%, 331/195; 1,624/3,338 and 9,471/21,981; δ = 0.36 and 0.26; 95.7 vs 82.7).
  - **README naming:** 120/41 and all conditional shares; broad variant 58.0/3.0.
  - **Commit size:** 211/58.8%/p = 0.008, 155/52.3%/0.948, 167/0.174.
  - **RQ3:** all framework, language, artefact and README shares.
  - **Table 3:** all 60 cells, apart from the two medians in item 2.
  - **Track tests:** H(11) = 19.0, p = 0.062, ε² = 0.02; χ²(33) = 201.1, V = 0.26, 8 of 48 cells below five; 87.5% Latin subjects.
  - **RQ4:** text and Fig. 6 match `credentials_aggregate.json`.
- By hand: Wilson intervals for 30/41 (58.1–84.3) and 4/120 (1.3–8.3); V = √(χ²/n) for 2×k tables; ε² = H/(n−1), which is Tomczak & Tomczak's H/((n²−1)/(n+1)); subtotals 3,201 + 2 + 446, 126 + 56 + 242 + 22, 3,615 + 34, 16 + 22 + 2 + 29 = 69 of 80, 32 + 27 + 3 + 15 = 77, and Table 3 rows summing to 984.
- Everything in the paper is cited and resolves: BibTeX and LaTeX give no warnings, and 61 of 61 entries are used. The abstract has 198 words.

---

## 1. Priority errors (fix before submission)

| # | Line | Problem | Fix |
|---|---|---|---|
| 1 | 214 | "Pooled over all signed and all other commits **of these repositories**, the median changes were 130 and 136 lines." `run_analysis.py` lines 403–404 pool over **all active repositories** (`nmc`), not over the 211 with both kinds. For the 211 repositories, the pooled medians are **129 (signed) and 112 (other)**, so the direction is reversed. | Either write "of all active repositories" (and keep 130/136), or restrict the calculation to the 211 repositories and report 129 and 112. The second option weakens the "not consistently larger" reading, so check the wording of the paragraph and of line 312. |
| 2 | 240, 244 (Table 3) | Median window commits are truncated by `int(sub.window_commits.median())` (`run_analysis.py` l. 451). T1 is really **25.5** (printed 25) and T5 **22.5** (printed 22). The same truncation is in `aggregates/tracks.csv`. | Use `round_half_up` or print one decimal. Lines 355 and 357 (AGENTS.md medians) and 403–404 use `int()` too; they happen to be integers now, but fix them all. |
| 3 | 73, `figures/architecture.tex` | Fig. 1 says "Known in advance: **deadline**, required tool", and the caption says "The event facts **fix the deadline**". Table 1 (l. 104) and l. 127 say that the window is "our inference" and that "we found no official schedule". | Box: "Known in advance: required tool". Caption: "The event facts fix the required tool; the event window is inferred (Section 3.2)". |
| 4 | 355 | "[pending: archived release with DOI]" is printed in the PDF. The public GitHub HEAD (950855e, which matches origin/main) is also **behind the paper**. The committed `facts_paper.json` has `readme_sample.labelled = 0` and lacks `inactive` (1,472/2,592), and `run_analysis.py`, `make_figures.py` and `paper_style.py` are uncommitted. Someone cloning the repository today cannot find the README-validation numbers or the l. 64 numbers. | Commit and push, tag a release, archive it on Zenodo, and put the DOI in. |
| 5 | 327 | "86.2%" is 69/80 = 86.25, and half-up rounding gives **86.3%**. The value is Python's round-half-to-even; the same issue was Round 3 item 1.21. "about 98.0%" gives false precision; "16/20", "22/25", "2/6" and "29/29" break the "933 of 946" style used elsewhere. The sample had 81 READMEs, of which 80 were labelled (`readme_sample.n = 81`), but the text says 80 and then mentions a Chinese one. | "86.3%" (or "86%"); "about 98%"; "16 of 20", and so on; "of 81 sampled READMEs, 80 could be labelled; one, partly in Chinese, …". Also make `make_numbers.py` round half-up for every value, not only for n/N shares. |
| 6 | 179 | "The active repositories hold at most 2,740 distinct author identities". The code counts **window commits only** (`wc_all`); counting all team commits of active repositories gives 2,771. | "…at most 2,740 distinct author identities in their window commits…". |
| 7 | 205, 168 | The odds ratios 3.32 (2.19–5.03) and 29.08 (10.82–78.19) use a **Haldane–Anscombe +0.5 correction**, Woolf intervals, and all 1,057 active repositories as the base, so repositories without a written README count as "not naming". None of this is stated; recomputing without the correction gives 3.35 (2.21–5.09) and 32.33 (11.40–91.68). | Add to §3.6: "Odds ratios for 2×2 tables add 0.5 to each cell and use log-scale (Woolf) intervals." At l. 205, name the base ("over the 1,057 active repositories"). |
| 8 | 340; Fig. 5 | "CI" is defined as confidence interval, but Fig. 5 labels a row "CI workflow" and the axis of the same figure reads "95% Wilson CI". | Relabel the row as "Continuous-integration workflow". |
| 9 | 271 (Table 4 caption) | The list of denominators leaves out the evening batch (row "Active, of the evening batch", N = 1,040). | "…(all repositories, open and not in the batch, the evening batch, or active repositories; …)". |
| 10 | 203 | "Most of them were branches … (18.7%), while authors named 'Codex' (3.1%) and commit signatures (1.5%) were rare." The percentages are of active repositories, but "Most of them" points to the 229; that share is 198/229 = 86.5%. | "Most were branch traces (198 of the 229; 18.7% of active repositories), while…". |

## 2. Statistical reporting and notation

| # | Line | Problem | Fix |
|---|---|---|---|
| 11 | 307 | χ²(3) = 608.2, V = 0.41 is computed with **the batch merged into "22 Sep"** (4 groups, n = 3,647), which the paper never says, while Fig. 2b shows five groups. With five groups: χ²(4) = 638.6, V = 0.42. p is also missing (p < 0.001). | "(χ²(3) = 608.2, p < 0.001, V = 0.41; the batch counted with 22 September)", or switch to the five groups of Fig. 2b. |
| 12 | 229 | χ²(33) with 48 cells implies four language categories, but these are never named. | "…primary language (Python, TypeScript, JavaScript, other) differed…". |
| 13 | 216, 267 vs 168 | §3.6 promises Cramér's V with every χ² test, but the test-file comparison (95.7% vs 82.7%, p < 0.001) and the `.gitignore` comparison (p = 0.287; V = 0.03 in `facts`) have no V. The Mantel–Haenszel p (0.948) is also left out. The logistic model adjusts for **log(1 + window commits)**, not for "the number of window commits". | Add V to both comparisons, and write "after adjusting for log(1 + window commits)". |
| 14 | 192 | "above the 0.19 (95th percentile 0.20) obtained for simulated data" is missing a noun, and the number of simulations (20, `\nullruns`, unused) is not given. | "above the mean silhouette of 0.19 (95th percentile 0.20) in 20 simulations without team structure". |
| 15 | 190 | "The median team made its first window commit 61 minutes…, its last 9 minutes…, and 19 commits" gives three separate medians to one "median team". | "Teams made their first window commit a median of 61 minutes after the start (IQR 43–94) and their last 9 minutes before the deadline, and made a median of 19 commits (IQR 10–35)." |
| 16 | 168, 184, 210, 225, 271 | The same term is written "Wilson 95% confidence intervals", "95% Wilson intervals" and "95% Wilson CI". | Choose one form, e.g. "95% Wilson intervals". |

## 3. Figures and captions

| # | Where | Problem | Fix |
|---|---|---|---|
| 17 | Fig. 1 | "independent recount" contradicts the text's "separate recount" / "written separately" (l. 73, 144), and Round 3 removed "independently" from the abstract. The "Product (RQ3)" and "Exposure (RQ4)" boxes do not match the section titles. | "separate recount"; "Artefacts and READMEs (RQ3)" and "Credentials (RQ4)". |
| 18 | Fig. 2b, caption l. 184 | The n labels count **open** repositories only (41, 755, 1,328, 37, 1,040), not the diamonds (58, 758, 1,754). Diamonds for "22 Sep (other)" and "(batch)" are hidden behind the circles. | Add: "n: open repositories; diamonds coincide with circles where none were archived." |
| 19 | Fig. 4a | The Claude markers at 0.0 and 0.5 are cut in half by the y-axis (Round 3, not yet fixed). | `ax.set_xlim(-1.5, …)` or `clip_on=False`. |
| 20 | Fig. 5 / l. 132 | "Docker Compose file" in the figure, "Compose file" in Methods, "Docker files" at l. 317 against "Dockerfile" elsewhere. | Use "Compose file" and "Dockerfiles" consistently. |

The other captions are accurate. Fig. 3's "Dashed lines mark an even spread and a majority" matches the 20% and 50% labels, and Fig. 6's "a repository can appear in more than one row" explains why the rows sum to 80 against 73 repositories.

## 4. Text: typos, terms, cross-references

| # | Line | Current | Fix |
|---|---|---|---|
| 21 | 81 vs 66, 307 | "data sets" / "dataset" / "Datasets" | "datasets" throughout. |
| 22 | 56 vs 317 | "nearly all of the committed code" and "virtually all of the committed code", same source [1] | Keep one wording (Round 3 item 1.20). |
| 23 | 60 and 93 | "single events through interviews, surveys and project evaluations" appears twice word for word | Rephrase at l. 93. |
| 24 | 100 | "Each repository … began with an organiser commit" is contradicted by 34 repositories that rewrote their history (Table 2). | "Each repository was created with an organiser commit…". |
| 25 | 100/144 | Table 3 (`tab:tracks`) is cited at l. 100, before Table 2 is first cited (l. 144). MDPI requires tables to be cited in numerical order. | Cite Table 3 only in §4.4, or move `tab:validation` earlier. |
| 26 | 129 | "written README" is never defined: it excludes 20 template READMEs, 3 missing and 1 with fewer than 20 letters, and `\minletters` is unused. | "…with a written README, that is, not the two-line template and with at least 20 letters of prose". |
| 27 | 175 | "in three bulk operations: … 56 on 17 September". `facts` shows the 17 September group spans 12:10–18:32, which is not a single operation. "…and only 14 repositories of the batch did" is ambiguous: "did" can attach to "held team commits". | "on three days"; "Of the batch, only 14 became active." |
| 28 | 179 | "…repositories that were closed or barely used before the event started": the batch was barely used *during* the event (Round 3 item 1.3). | "…lies in repositories archived before the event or created in the evening batch." |
| 29 | 258 | "Most are OpenAI API keys" overstates; elsewhere the paper says "strings matching … key formats". | "Most match the OpenAI API key format". |
| 30 | 267 | "The keys **therefore** entered…" follows a sentence about signatures, which does not support it. | Drop "therefore", or move the sentence after the file counts. |
| 31 | 49 | "…of the rest" is ambiguous (Round 3 item 1.8); "Such measurements rarely know" gives measurements a human verb. | "…48.2% of the 2,163 that were open and not in the batch"; "Such studies rarely know". |
| 32 | 310 | "at most about half of the repositories" | "in fewer than half of the repositories". |
| 33 | 90 | "Secrets leak to public GitHub repositories often" | "Secrets often leak to public GitHub repositories". |
| 34 | 136 / 327 | Latin-script Kazakh would be classed as English, but Threats mentions only Kazakh typed with Russian letters. | Add "or with Latin letters" to the threat. |
| 35 | 339–361 | MDPI order puts Abbreviations after Conflicts of Interest, and "Ethics statement" is not an MDPI heading. | Reorder, and move the ethics text into the IRB statement or §3.4. |

British spelling is consistent: I found no -ize/-yze, "behavior", "labeled", "artifact" or "color" in the prose.

## 5. References (rendered bibliography)

1. **"page 496–507" (singular) in about 25 entries**, including [4], [6]–[8], [10], [12], [13], [15]–[17], [22]–[24], [28], [32], [34], [36]–[38], [40], [42]–[44], [47] and [59]. The Crossref-derived `pages` fields use a Unicode "–", so `unsrtnat` does not see a range. [45] and [57] use `--` and print correctly. Fix: replace "–" with "--" in `references.bib`, or in `build_bib.py`.
2. **[8] Kalliamvakou:** the series is printed as "ICSE '14"; the proceedings are MSR 2014.
3. **[13] Imam et al.:** a colon is missing from the title, which should read "The Secret Life of Hackathon Code: Where does it come from and where does it go?".
4. **[16]:** "Game Jams Hackathons and Game Creation Events" needs a comma: "Game Jams, Hackathons and Game Creation Events".
5. **Mixed capitalisation, frozen by `{{…}}`:**
   - [8], [9], [14], [17], [22], [36], [37], [39], [58] and [61] are in sentence case; the rest are in title case.
   - The booktitle of [37] reads "Proceedings of the fifth international workshop on Computing education research workshop".
   - Choose one style, or accept Crossref's as-published casing, but fix the [37] booktitle.
6. [9] and [14] (Empirical Software Engineering) have no article numbers. [17] should use the SEET proceedings title. [45] is the only entry with a location and ISBN.
7. I found no duplicates, and no missing DOI where one exists: [27] and [45] give the preprint DOI plus the venue URL, and [57] has no DOI. Years agree with `reference_audit.md`.

## 6. Reproducibility and data documentation gaps

1. **DATA_CARD cross-reference:** "The paper (Section 4) gives the exact definitions" should say Section 3 (3.2–3.3).
2. **`commits.csv` (15 columns) has no column table.** The card should define:
   - the origin and unit of `minutes_from_start` (minutes from 13:00 UTC+5, committer time) and `author_minutes_from_start`;
   - `in_window` and `is_merge`;
   - `files`, `added` and `deleted`;
   - `code_lines`, including which lock, data and generated files are excluded;
   - `conventional`;
   - the values of `subject_script` (`latin`, `cyrillic`, `kazakh`, `none`);
   - the values of `agent_kind`, including `bot`;
   - `agent_name_only`, `author` and `author_is_bot`.
3. **`repositories.csv` gaps:**
   - `readme_images` is a **count**, not a 0/1 flag. A reader who sums it as a flag gets 84.2% instead of the paper's 21.3%. `readme_words` and `readme_headings` are also counts.
   - `template_found` and `readme_mentions_agent_tool` are not defined.
   - The list separator ";" in `frameworks`, `llm_sdks` and `agent_branch_kinds` is not stated.
   - The card does not say that artefact and trace columns are empty for repositories without commits.
   - `track` must be read as a zero-padded string.
   - `hours_active` counts window hours only.
   - The card should give the mapping of track codes to the names in Table 3.
4. **Not recomputable from the public files:**
   - the share of READMEs with a Kazakh-specific letter (14.2%; no column);
   - the batch rate of 15 per minute against 8, and the archive clusters and waves (only dates are released);
   - every row of Table 2 except the window shifts and author time;
   - all of RQ4 (aggregates only, as the paper says).

   Say this in the DATA_CARD, or add a `readme_any_kazakh_letter` column and minute-level `created_at`.
5. **Figures:** `make_figures.py` reads `facts_paper.json` and `tables/*.csv`, which are identical to `aggregates/`. The figures can therefore be redrawn, but not rebuilt from the record-level public CSVs. Either state this, or let `reproduce_public.py` write a public-only `facts` file that the figure script can read.
6. **`reproduce_public.py` checks a number the paper no longer reports.** It tests "committed in all 5 hours" (44.5%), not the reported "at least four of the five hours" (79.3%). Replace that check, and add checks for items 1, 2 and 7 above and for 1,043/2,163, the χ² and Kruskal–Wallis values, and the silhouette. All of these can be computed from the public data.
7. **Line 329 overstates what `recollection.csv` holds.** The line says "The commit at which each clone ended is released", but the file gives only the default-branch HEAD, while the clones kept every branch and pull-request reference. Either say "the default-branch commit", or release the tips of all references.
8. **The Data availability statement matches the release in content:** pseudonymised data, the pipeline (`src/`, which needs the clones), the plan and deviations (`analysis/analysis_plan.md`, `deviations.md`), credentials as aggregates only, and the OSF link. It still needs the DOI and an up-to-date push (item 4).
