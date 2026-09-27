# Editor's assessment: repository and paper (27 September 2026)

Written before reading the two reviewer reports, so that the three views are independent.

## 1. What the repository does well

1. **A census, not a sample.** The organisers created one repository for every registration, and we mirrored all 3,649 of them, including the 2,395 that never received a team commit. Datasets built from project listings, such as HackRep, contain only projects someone chose to list, so they cannot show the step from registration to code. Our data can.
2. **A controlled setting that occurs naturally.** Every team had the same five-hour window and the same agent requirement, and started from the same template. Few field datasets hold this many conditions constant across about a thousand teams.
3. **Complete, checked collection.** We have mirror clones with every branch and pull-request reference. Default-branch commit counts from the clones equal the GitHub API's for all 3,649 repositories. A separate audit of 402 repositories found template commits made by a second organiser account.
4. **Numbers come from the data.**
   - Every number in the text is a macro generated from `facts_paper.json`.
   - A lint rejects literal numbers in the prose.
   - A claim ledger records the evidence for each claim.
   - The analysis plan was written before the statistical tests.
   - Seeds are fixed.

   Few empirical papers can show this degree of reproducibility.
5. **Checks on wording and references.** The banned-word lint, citation check and new reference audit all run from one command.
6. **Careful ethics.**
   - Secret scanning uses redacted output, and keys were never tested.
   - Only aggregates are reported, and identifiers are hashed.
   - The paper states that we are not affiliated with the organisers.
7. **Two measurement findings that apply beyond this event.**
   - Organiser template commits can come from more than one account.
   - Agent signatures in commits reflect each tool's defaults: Claude signs commits by default and Codex does not, yet Codex was the required tool.

   The second is the most general scientific finding in the project.

## 2. Gaps in the repository

| # | Gap | Why it matters | Effort |
|---|---|---|---|
| G1 | `public_data_generated/` is empty, but the paper says a derived dataset is released | The paper's own claim is not yet true; this must be done before the arXiv upload | M |
| G2 | The README language rule has no hand labels yet (90-README sample, labelling in progress) | RQ5 depends on it; Table 3 has a pending cell | S (user) |
| G3 | No outcome variable: we cannot say which repositories were good | Without it the paper describes but cannot explain; the winners list (1 Oct) fixes this | M |
| G4 | No baseline from events without agents | Statements like "tests were common for a five-hour event" have no comparison; HackRep (Zenodo, CC BY 4.0, 2.5 GB) makes a pre-agent baseline possible | L |
| G5 | Track labels were checked by one person | Fine for arXiv; a journal will ask for agreement on a sample | S |
| G6 | Tests are counted as present, not as run or passing | "Tests in 76.9%" can be misread as a quality claim | M |
| G7 | `check_figures.py` (planned in M4) was never written | Figure labels are not checked against the facts file | S |
| G8 | Top-level `README.md` files describe the earlier Threads analysis, not the paper pipeline | Readers of the release need one entry point | S |
| G9 | Nothing from `arxiv_paper_all/` or the new `src/` scripts is committed | The release, the DOI and reproducibility depend on it | S |

## 3. Reference audit (done 27 September 2026)

Script: `checks/audit_references.py`; report: `literature/reference_audit.md`. It works independently of the script that built the bibliography.

- **39 entries, 0 failed, 0 mismatched.**
  - 31 DOIs resolve at doi.org, and title, first author, author count and year agree with Crossref or DataCite.
  - 2 papers are peer-reviewed at venues without DOIs: SWE-bench at ICLR 2024, and Krause et al. at USENIX Security 2023. Their arXiv DOIs are verified and their venue pages resolve.
  - 6 are grey literature (event site, four news reports, Gitleaks), and each URL returns HTTP 200.
- **Upgraded from preprints to peer-reviewed versions** (same titles and authors, confirmed in Crossref):
  - Zhou et al.: ICGJ 2026, 10.1145/3833089.3833091.
  - Gama et al.: ICSE-SEET 2026, 10.1145/3786580.3786992.
  - Sajja et al.: *Big Data and Cognitive Computing* 8(12):188, 10.3390/bdcc8120188. BDCC has already published on generative AI in hackathons.
  - Chatlatanagulchai et al.: *ACM TOSEM* 2026, 10.1145/3840295.
- **Still arXiv-only, 9 of 39:**
  - Peng 2023; AIDev (Li 2025); Gloaguen 2026 (ICLR 2026 workshop, non-archival); SWE-chat 2026; Waseem 2025; Zhao 2025; Gao 2026; Deng 2026; Chen 2026.
  - These are the newest papers in the area and cannot be replaced yet. A journal version should check them again before submission.
- **Fixed during the audit:** a parser bug in `check_citations.py`, which read one-line Crossref entries only by accident, and "Projects?: Identifying" in the Nolte title.
- **Not covered by the metadata audit:** whether each source supports the sentence that cites it. Reviewer 1 is checking that separately.

## 4. The paper as it stands

Measurements:
- About 5,300 words before the references.
- The abstract has 215 words and 13 numbers. MDPI caps abstracts at about 200 words.
- 83 Results sentences, 29.6 words on average; 16 of them contain six or more numbers.
- 39 references, 28 of them from 2024–2026.

Observations:
1. **There is no thesis.** The paper answers seven parallel questions, and a reader finishes it with a list of facts but no argument. The strongest candidate for a thesis: when organisers create a repository for every registration, the repositories form a census; the census shows the gap between registering and taking part, and what repository traces can and cannot tell us about software built with agents under a deadline.
2. **RQ7 (tracks) does not stand as a question.** The main test is null (p = 0.062), and the rest of it is Table 2. Fold it into the RQ3 context.
3. **Table 2 mixes setting and results.** It sits in the event section but carries result columns (repositories, commits, tests, Python).
4. **Repetition.**
   - The AI-use statement appears in both Methods and the ethics section.
   - The Conclusion repeats numbers from the Abstract.
   - The RQ denominators are stated in the definitions paragraph and again in the Results.
5. **Crowded sentences.** Many Results sentences stack three or four statistics. EMSE, TOSEM and BDCC papers usually end each RQ with a short boxed answer and move secondary numbers into a table.
6. **Links between RQs are missing.** Each RQ is analysed alone, so the story does not connect. Joint analyses would link them:
   - Were keys committed in agent-signed commits?
   - Did the late-surge cluster ship fewer tests?
   - Did teams with context files write English READMEs?
7. **Units are not yet uniform.**
   - "three per cent" appears in words next to % signs.
   - Some intervals are written "95% CI a–b", others just "(a–b)".
   - Medians appear with CIs in some places and IQRs in others.
   - The style guide asks for whole percentages in figures, but the figures use one decimal. The guide should follow the figures.
8. **Figures.**
   - The style is consistent: Okabe–Ito palette and one font.
   - Fig. 5 has only two bars.
   - Vermillion means "agent footprint" in Fig. 4, "late surge" in Fig. 3 and "still in the final version" in Fig. 6.
   - Fig. 2a gives shares of all repositories, while the text gives the track match as a share of active repositories.
9. **Length and depth.** Q1 journal articles usually run 8,000–12,000 words, with a longer discussion of implications and a comparison with prior results.
10. **Ethics statement.** Many journals ask for an ethics approval or exemption statement even for public data. With an affiliation, the university's exemption route should be checked.

## 5. Venues

Fit only. Quartiles and speeds must be checked on JCR or Scopus and on the journal pages before choosing.

- **MDPI BDCC.** It has published the Sajja et al. hackathon paper and is fast. It fits if the paper is framed around a big-data census and AI use.
- **MDPI MAKE.** It fits if the extension adds machine learning: predicting jury outcomes from repository traces, or LLM versus rule-based extraction.
- **Empirical Software Engineering (Springer).** The best subject fit for an MSR study; slower.
- **Journal of Systems and Software; Information and Software Technology (Elsevier).** Good fit for empirical software engineering.
- **IEEE Access.** Fast and broad.
- **ACM TOSEM.** A high bar. It published Agent READMEs, which is close in subject.
- **Dataset papers:** *Scientific Data*, *Data in Brief*, MDPI *Data*, or the MSR Data and Tool Showcase track. HackRep appeared in that track.
