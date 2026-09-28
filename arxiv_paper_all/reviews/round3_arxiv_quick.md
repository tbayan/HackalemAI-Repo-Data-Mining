# Round 3: quick arXiv pre-posting check

Reviewer role: cs.SE/cs.AI arXiv reader, quick final pass (about 15 minutes).
Checked: `latex/main.tex` (line numbers below refer to it), rendered `main.pdf` (built 02:51, same time as main.tex), `analysis/facts_paper.json`, `analysis/run_analysis.py` (only to see what a statistic is), `latex/references.bib`, `literature/reference_audit.md`, `literature/notes/abstracts*.md`.

**Decision: fix first.** There is one false statement (L323, README-rule errors) and several citations that support their sentences only in part. Everything else is minor wording. About an hour of edits, with no new analysis except two derived counts for L63 and optional CIs for two odds ratios.

---

## 1. Citation–claim support (Introduction, Related work, Discussion)

Supported as written (no action): baumann2026swechat (L55, L313), li2025aidev, robbes2026agenticmuch (22.20–28.66%, 128,018, larger commits), agarwal2026aiides + he2026cursor (L83), chatlatanagulchai, openai2026agentsmd, tufano2024chatgpt, nolte2020, mcintosh2021, imam2021/mahmoud2022 (22,183 Devpost), halmans2026hackrep, kalliamvakou2014, hoess2025, peng2023, barke2023, liang2024, zhou2026, gama2025, chen2026, sajja2024, waseem2025, prather2023, denny2024, claes2018, edwards2009, kazerouni2017, kuutila2020, saghi2025, sinha2015, basak2023secretbench, basak2023tools (88% / 46%), krause2022 (L89), huang2024, perry2023, gao2026, zhao2025, deng2026, claudecode2026attribution, ralph2020, halmans (L332).

Not supported, or only partly supported:

| Line | Sentence (short) | Problem | Fix |
|---|---|---|---|
| L83 | "other agents read the same file" | **No citation.** Methods L134 repeats it, also uncited. The whole Codex-specific vs. shared-AGENTS.md split rests on it. | Cite a source: e.g. gloaguen2026agentsmd, which evaluates AGENTS.md across several coding agents, or the agents.md spec / another vendor's docs as grey literature. Otherwise say "is designed to be read by several agents" and cite the spec. |
| L83 | "in a benchmark such files tended to lower task success [gloaguen]" | The abstract in notes says context files "do not generally improve task success rates, while increasing inference cost by over 20%". "Tended to lower" is stronger. Also, two settings were used, not one benchmark. | "in benchmark experiments such files did not generally improve task success and raised inference cost by over 20%~\cite{gloaguen2026agentsmd}". |
| L83 | "All of these studies observe agents in projects whose developers chose their tools freely" | This sentence also covers SWE-bench, SWE-agent and Gloaguen, which are benchmarks and observe no developers. | "All of these field studies observe …" or "The mining studies above observe …". |
| L57 | "a study cannot tell how many such repositories it misses~\cite{robbes2026heuristics}" | The abstract says only that the paper "documents the promises, perils, and heuristics". It does not state this point. | If the full text discusses unsigned or undetectable agent use, cite that section (e.g. `\cite[Sec.~X]{…}`). Otherwise attach the citation to a weaker clause: "trace-based detection has known blind spots~\cite{robbes2026heuristics}". |
| L310 | "This is the partial observability that Robbes et al.\ describe~\cite{robbes2026heuristics}; a known required tool shows its size and its direction in one setting." | Same problem: "partial observability" does not appear in the abstract. "Its size and its direction" is also vague (see §5). | "Robbes et al.\ list the perils of detecting agents from traces~\cite{robbes2026heuristics}; a required tool shows how large one such blind spot can be in one setting." |
| L55 | "…co-author trailers in commit messages, branch names, pull requests and context files…~\cite{li2025aidev,robbes…,robbes…,chatlatanagulchai…}" | None of the four abstracts mentions **branch names** as a trace. | Check the Robbes heuristics full text. If branch names are not there, drop "branch names" from this cited list, or move it to your own Methods (L134). |
| L57 | denominator unknown "…which samples drawn from project listings or from detected agent activity cannot contain~\cite{kalliamvakou2014perils,baltes2022sampling}" | Partly supported. Kalliamvakou shows that most GitHub projects are personal or inactive, and Baltes shows that random sampling is rare. Neither says that listing-based samples cannot contain never-used repositories. That part is your own argument. | Keep the claim uncited as your argument and cite for the general sampling-frame point: "…cannot contain; how the sampling frame is drawn shapes any rate computed from it~\cite{baltes2022sampling}, and most GitHub repositories are personal or inactive~\cite{kalliamvakou2014perils}." |
| L80 | "representative samples are rare in software engineering research~\cite{baltes2022sampling}" | The notes say "random sampling is rare". Random and representative are not the same thing. | "random or representative samples are rare". |
| L89 | "Secrets leak … often and remain there" | "Remain there" is not in the Meli abstract, which gives pervasiveness and thousands of new secrets per day. | Drop "and remain there", or cite the specific Meli result on removal. |
| L92 | AI-at-hackathon studies describe experiences "rather than the output of a whole event" | Chen et al. scored all submitted projects on functionality, UI/UX and code readability, so they did study outputs. | "…rather than the repositories of every registered team". |
| L307 | "withdrawn or duplicate registrations and the allocation of limited seats, which the news reports describe~\cite{qumash…,ulys…}" | Read literally, the news reports describe all three causes. L97 shows they describe queues and limited seats only. | "The allocation of limited seats, which news reports describe~\cite{…}, and withdrawn or duplicate registrations are possible reasons." |
| L310 | "Estimates such as those of Robbes et al.~\cite{robbes2026agenticmuch}, which combine several traces, are less exposed" | The cited paper does not show this. It is your inference. | "…may be less exposed". |
| L313 | "Language models support Kazakh less well than high-resource languages~\cite{togmanov2025kazmmlu}" | KazMMLU reports that even the best models "struggle … in Kazakh **and Russian**". So it does not show that Russian is better supported, which is exactly what the next clause implies ("push teams … towards Russian or English"). | "Language models still perform poorly on Kazakh benchmarks~\cite{togmanov2025kazmmlu}, which may push teams towards English…". Either drop Russian from the mechanism or cite a source that compares Kazakh with Russian and English. |
| L313 | Recommendations "consistent with earlier recommendations~\cite{meli2019git,krause2022pushed,basak2023tools}" | Partly supported. Basak recommends choosing detectors by secret type and updating vendor rules, not templates, push protection or short-lived keys. Meli evaluates mitigations; Krause recommends platform support. | Keep meli and krause, drop basak here, and soften: "…follow the direction of earlier recommendations for prevention at commit time and support from platforms~\cite{meli2019git,krause2022pushed}". |

Outside the requested scope, but a reference error: `ralph2020standards` lists **"Davide Taibi" twice** (bib L288; rendered ref [60]). Delete the duplicate.

---

## 2. Numbers vs. facts_paper.json, and internal consistency

All headline numbers in the abstract, introduction, Table 4 and the conclusion match the JSON and agree with each other. I checked 29.0 / 33.0 / 48.2, 1,043/2,163, 19.2 pp, 21.7 / 46.3 / 24.9, 4/120 and 30/41 (Wilson CIs recomputed by hand: 1.3–8.3 and 58.1–84.3), 446 = 126+56+242+22, 3,201+2+446 = 3,649, 229+260 = 489, 3,102/3,541 = 87.6%, 77 = 32+27+3+15, V and ε² recomputed from χ², H and n. Problems found:

1. **L323 (false statement).** "Its errors lay in READMEs it called Kazakh (16/20 …) or mixed (2/6 …)". The JSON has `agree_english = 22/25`, so 3 of the 11 disagreements are in READMEs the rule called English (0 Russian + 3 English + 4 Kazakh + 4 mixed = 11 = 80 − 69). Fix: "Its errors lay in READMEs it called English (22/25 confirmed), Kazakh (16/20; the others were Russian) or mixed (2/6)." Also check what the three English errors were. If they were Russian, the Russian share is slightly understated too.
2. **L207 odds ratios.** "Naming a tool and leaving its traces go together (odds ratio 3.32 … 29.08)". The code computes the OR against **any** trace (for Codex this includes AGENTS.md), with a +0.5 correction, over all 1,057 active repositories. The mention shares use the 1,033 written READMEs. The text does not say which trace, and the CIs are computed (`assoc.lo/hi`) but not reported. Fix: "(odds ratio for naming the tool and any trace of it, including AGENTS.md for Codex: 3.32, 95% CI …; Claude Code 29.08, 95% CI …)".
3. **L216.** "Signed commits more often had conventional-commit subjects (48.7% against 43.1% of non-merge window commits)". 43.1% is the share among **unsigned** non-merge commits; all non-merge commits give 43.8%. Fix: "(48.7% of signed against 43.1% of other non-merge window commits)".
4. **L216.** "Over all such commits the medians were 130 and 136 changed lines". It is unclear whether "such" means all window commits or the commits in the 211 repositories. Name the set.
5. **Fig. 5 (L225).** It shows "Mentions a coding agent 24.9% (257 of 1,033)". This measure (`readme_mentions_agent`, a different regex) is never defined or mentioned in the text, and it sits beside the strict naming shares of 11.6% and 4.0% in §5.3. A reader will read these as contradictory. Define it in §4.2 and mention it in §5.4, or drop the bar.
6. **L168.** "three planned tests of the association between AGENTS.md and activity". The third test is test files, which is not activity. Fix: "…between AGENTS.md and activity or test files".
7. **L132.** "agreed with the label for 933 of 946 … We read every disagreement and corrected 7 labels." It is unclear whether 933/946 is measured before or after the corrections. State which (Table 2 L161 has the same ambiguity).
8. Minor: L97 "Each repository … began with an organiser commit titled 'Initial commit'". 34 repositories rewrote their history (Table 2), so write "was created with".

---

## 3. Equations and statistics

- **Last-hour share** s_i = ℓ_i / c_i (L127): correct, and an even spread gives 20%. Say whether the interval is half-open, [17:00, 18:00), consistent with the 13:00–18:00 window.
- **ε² = H/(n−1)** (L168): correct. Tomczak & Tomczak's ε²_R = H / ((n²−1)/(n+1)) simplifies to H/(n−1). Check: 19.0/983 = 0.019 ≈ 0.02. ✓
- **Wilson 95% CIs**: correct. Two recomputed by hand match.
- **Cramér's V**: correct. √(201.1/(984·3)) = 0.26 and √(14.9/2161) = 0.08 ✓. Expected-count cells are reported ✓. Small gap: the "all repositories" χ² (L307, df = 3) merges the 22 Sep batch with the other 22 Sep repositories, unlike Fig. 2b, which shows five groups, and gives no p. Add "(22 September pooled; p < 0.001)".
- **Cliff's δ / Mann–Whitney**: correctly used. Say "Holm-adjusted" once for all three p-values rather than only for the first.
- **Mantel–Haenszel OR** (L267): correctly described (stratified by LLM use). Fine.
- **Wilcoxon signed-rank** on per-repository medians (L168, L216): correct design.
- **Logistic regression** (L216): the covariate is log(1 + window commits). Say "log" in the text.
- **κ**: never named. Write "Cohen's κ" at first use (L132).
- **Silhouette / clustering (L194) — interpretation problem.** The method is not stated: k-means with k = 2 on hourly shares, and a null of 20 multinomial resamples of the pooled profile. More importantly, the observed silhouette of 0.30 is **above** the null's 95th percentile (0.20, in the JSON). So the comparison "against 0.19 for simulated data without team structure" shows more structure than chance, not less. "Weak" rests on the absolute value only, and the 0.26–0.50 "weak structure" convention comes from Kaufman & Rousseeuw (1990), not from the 1987 paper. Rewrite: "k-means with two clusters on the hourly shares separated a late group of 323 teams. The silhouette (0.30) exceeded that of simulated data without team structure (mean 0.19, 95th percentile 0.20) but is low in absolute terms, so we read the profiles as a continuum with a late tail rather than as distinct types."

---

## 4. Three sentences most likely to be read as overclaiming

1. **L65 (Contribution 2):** "it measures what the trace heuristics used in agent-adoption studies recover when the intended tool is known". "Recover" implies recall, but compliance is unknown, and L207 itself says the shares are "not the recall of the traces over all users". The same problem appears in L310, "shows its size".
   *Rewrite:* "Second, it reports how often the trace heuristics used in agent-adoption studies detect a tool that every team was required to use, and how detection differs between a tool that signs its commits by default and one that seldom does."
2. **L63 (and L181):** "The organisers' actions account for most of the gap between repositories and activity". This is causal wording for an inference. The organisers created the batch, but its repositories may have gone unused because those registrants were never admitted. And "most" is 1,472 of 2,592 inactive repositories, about 57%. L181's "closed or barely used before the event started" is also confusing, because the batch was barely used at all, not only before the event.
   *Rewrite L63:* "More than half of the repositories without event-time work (1,472 of 2,592) had been archived by the organisers before the event or belonged to a batch of 1,040 created the evening before, of which only 14 became active." Generate 1,472 and 2,592 as macros. *Rewrite L181:* "…thus lies in repositories that were archived before the event or created in the evening batch."
3. **L310:** "The loss is tool-specific." … "Adoption estimates that rest on commit signatures **will** therefore count tools that sign by default more completely…". These are general claims from one event and 120 + 41 self-selected READMEs.
   *Rewrite:* "Detection differed sharply between tools. … Adoption estimates that rest on commit signatures can therefore count tools that sign by default more completely than tools that do not."

Also worth softening:
- L48: "reproduced the core counts independently". It was the same author with a separate script, so write "reproduced the core counts with separately written code".
- L316: "the measures above **would** reduce the exposure", which is untested. Write "could".
- L194: "The teams therefore form a continuum rather than types" (see §3).

---

## 5. Readability for a first-time arXiv reader

1. **The abstract omits RQ3 and RQ4**, yet the keywords include "credential leakage". Add one sentence, e.g. "OpenAI key strings reached the public history of 5.8% of active repositories, mostly through committed `.env` and `.env.example` files."
2. **"Open" repositories** are first used in §5.1 (and implicitly as "the rest" in the abstract) but never defined. Define them in §4.1 next to "archived before the event": open = not archived before the event.
3. **"The earlier table"** (Table 2, L158) is mentioned in §4.2 only as the source of the track labels. Readers will not know why commit counts are compared with it. Add one clause in §4.4.
4. **Undefined terms:**
   - "conventional-commit subjects" (L216): add "(e.g. `feat: …`, Conventional Commits)".
   - "pull-request references" (L134, L144): add "(`refs/pull/*`, which GitHub keeps for every pull request)".
   - Gitleaks' "generic" vs "provider-specific" rules (L139, L258): one clause each.
   - "hours with commits" (Table 2): the number of the five clock hours with at least one commit.
5. **L216 mixes exploratory and planned analyses** in one paragraph ("Two further comparisons were exploratory … In the planned comparison …"). Split it at "In the planned comparison".
6. **L310, "its size and its direction"**: it is unclear what the direction is. See the rewrite in §1.
7. **The time-use literature (L86: Claes, Edwards, Kazerouni, Kuutila, Saghi) and the Copilot productivity studies are never used again.** Either connect §5.2 (last-hour share) to them in one sentence of the Discussion, or cut them. The author asked for no redundancy.
8. The RQs (L61) are not signposted in the Results. Add "(RQ1)" to "(RQ4)" to the headings of §5.1–5.5. §5.2 and §5.3 together form RQ2.
9. **Float placement**: Table 3 falls on the Discussion page and Table 4 after §6.1 starts. Consider `[p]` or moving the tables up so each lands next to its text.
10. L127: "between 18:00–20:00" should read "between 18:00 and 20:00".
