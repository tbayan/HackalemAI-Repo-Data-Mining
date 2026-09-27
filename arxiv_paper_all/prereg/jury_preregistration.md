# Pre-registration: repository features and jury decisions at HackAlem AI (Astana, 23 September 2026)

**Registration type:** secondary data analysis. The structure follows the template of Van den Akker et al. (2021), *Meta-Psychology*, doi:10.15626/MP.2020.2625.
**Author:** Talgar Bayan (talgar.bayan@gmail.com). Independent researcher, not affiliated with the organisers.
**Written:** 27 September 2026, during the jury's review period (24–28 September) and before any finalist or winner has been announced.
**Frozen predictor file:** `data/prereg/jury_predictors.csv` (private; it contains repository names), SHA-256
`9332945fb024e544c1f40bd37ec1bebf6a9fcf68ad6193a1af30a202449aba0b`. The file is produced by `freeze_predictors.py`, which is attached.

---

## 1. Study information

**Context.** HackAlem AI was a five-hour, in-person hackathon held in Astana on 23 September 2026, in which teams were required to use OpenAI Codex. Before the event, the organisers created public GitHub repositories for registered teams in the organisation `BAITC-Hacks` (3,649 in total). They archived most of them at the deadline, and some in bulk before the event. We mirrored all 3,649 repositories. According to the event website (hackalem.ai, read 27 September 2026), jury members and technical experts review the submitted projects from 24 to 28 September. Finalists present their solutions to the jury at Demo Day on 29 September, where the winners are announced, and prizes are presented on 1 October at the Digital Bridge forum. The website does not say how many teams win, or whether winners are chosen per track.

**Research question.** Within a track, which features of a team's repository are associated with the jury's decision to give it an award?

**Hypotheses.** Each hypothesis is tested within track (Section 5). H1 and H2 are directional. H3–H5 are two-sided, because we have no basis for a direction.

- **H1 (amount of work).** Awarded repositories have more event-window commits than other active repositories in the same track.
- **H2 (a product the jury can try).** Awarded repositories link to a deployed application more often than other active repositories in the same track.
- **H3 (artefacts that agents make cheap).** Test files, a Dockerfile and README length are associated with awards. Our conjecture is that coding agents make these artefacts cheap to produce, so they may distinguish awarded teams little or not at all. We state in advance how we will decide that an association is negligible (Section 5.4).
- **H4 (agent traces).** An `AGENTS.md` file, agent-signed commits, and branches created by Codex are associated with awards.
- **H5 (timing).** The share of a team's event-window commits made in the last hour is associated with awards.

## 2. Data

**Population.** The analysis uses the 1,057 *active* repositories, meaning those with at least one team commit between 13:00 and 18:00 local time (UTC+5) on 23 September 2026, counted on committer timestamps across all branches, without the organisers' template commit. Of these, 984 have a track label (12 tracks); 73 could not be assigned a track and are excluded from the within-track analyses.

**Predictors (all fixed before this registration).** They are measured from the final state of each repository and from its commit history.

| Variable | Definition | Used in |
|---|---|---|
| `window_commits` | Team commits in the event window (all branches, deduplicated by SHA) | H1 |
| `deployed_link` | README contains a link to a deployed application (URL pattern rule) | H2 |
| `tests` | Repository contains test files (file-name and folder rules) | H3 |
| `dockerfile` | Repository contains a Dockerfile | H3 |
| `readme_words` | Words in the root README after removing code blocks and markup | H3 |
| `agents_md` | Repository contains a file named `AGENTS.md` | H4 |
| `agent_signed` | At least one commit carries an agent co-author trailer, a "generated with" line, or an agent account | H4 |
| `codex_branch` | At least one branch name starts with `codex` | H4 |
| `last_hour_share` | Share of the team's event-window commits made between 17:00 and 18:00 | H5 |
| `hours_active`, `pre_event_commits`, `llm_sdk`, `claude_md`, `deploy_config` | Covariates and exploratory variables | Sections 5.3 and 5.5 |

**Outcome (to be collected after the announcements).**
- **Primary outcome, `awarded`:** 1 if the organisers' official announcement lists the team among the prize winners of its track (any place or prize), and 0 for every other active repository in that track.
- **Secondary outcome, `finalist`:** 1 if an official list of finalists or Demo Day presenters names the team. It is used only if such a list is published. The website speaks of *submitted* projects, but submissions are not visible to us. Some active repositories may therefore never have been submitted, which dilutes every comparison towards no difference. We report this as a limitation.
- **Sources:** only official organiser channels, that is, the event website and the organisers' official social media and press releases. News reports are used only to locate an official list.

## 3. Prior knowledge of the data

The author has computed and inspected every predictor above while writing a descriptive study of the repositories. That work is not yet public and contains no outcome information. At the time of writing, the author has seen no list of finalists or winners and no statement about which teams were successful. The author will not search for outcome information before this registration is time-stamped. The predictor file is frozen, and its hash is given above.

## 4. Linking the outcome to repositories

1. Take the team names, and the project names if given, from the official lists.
2. **Normalise every name:** lower case, remove everything except letters and digits, and transliterate Cyrillic to Latin with one fixed table. Normalise the team-name part of each repository name, `hack-<id>-<team>`, in the same way.
3. **Exact match after normalisation:** a match.
4. **No exact match:** propose candidates with a string similarity of at least 0.85. The author confirms or rejects each candidate *by name and track only*, without looking at any predictor value.
5. **Several repositories match one team:** prefer the active repository in the announced track. If it is still ambiguous, exclude the team and report it.
6. Report the number of awarded teams, the number matched, and the reasons for each non-match.

## 5. Analysis plan

### 5.1 Primary tests (one per predictor; nine tests)
H1: `window_commits`. H2: `deployed_link`. H3: `tests`, `dockerfile`, `readme_words`. H4: `agents_md`, `agent_signed`, `codex_branch`. H5: `last_hour_share`.

**The test statistic** is the stratified difference between awarded and other active repositories, computed within each track and averaged with weights equal to the number of awarded repositories in the track:
- for binary predictors, the difference in proportions;
- for continuous predictors, the difference in mean within-track percentile rank (mid-ranks for ties).

**The p-value** comes from a permutation test that shuffles `awarded` *within track* 10,000 times (seed 2026), as p = (1 + number of permuted |T| ≥ observed |T|) / (1 + 10,000). H1 and H2 use the one-sided version in the stated direction.

**Multiplicity.** Holm correction across the nine primary tests, family-wise α = 0.05.

### 5.2 Effect sizes (reported for every predictor, whatever its p-value)
- **Binary predictors:** the Mantel–Haenszel odds ratio stratified by track, with a 95% confidence interval (Robins–Breslow–Greenland variance).
- **Continuous predictors:** a stratified Cliff's δ, the average of within-track δ weighted by (awarded × other) pairs, with a 95% bootstrap interval (10,000 resamples within track, seed 2026).

### 5.3 Secondary model (exploratory)
A conditional logistic regression of `awarded`, stratified by track, on all nine primary predictors plus `hours_active`, with `window_commits` log-transformed as log(1 + x). If separation occurs, a Firth-penalised version is used. The results are reported as adjusted odds ratios with 95% intervals and are labelled exploratory.

### 5.4 How results will be read
- **An association** is reported when the Holm-adjusted p < 0.05.
- **A negligible association** is claimed (the H3 conjecture) only if the whole 95% interval lies inside the equivalence bounds: odds ratio 0.5–2.0 for binary predictors, Cliff's δ −0.15 to 0.15 for continuous ones.
- **Otherwise** we say the data cannot distinguish the two, and we will not read a large p-value as evidence of no association.

### 5.5 Robustness checks (reported alongside the primary results)
1. Repeat the primary tests without repositories that had commits before 13:00 (`pre_event_commits > 0`).
2. Replace `window_commits` with `hours_active` for H1.
3. Repeat with the `finalist` outcome, if a finalist list is published.
4. Treat unmatched awarded teams as missing (the primary analysis), and also as non-awarded (sensitivity).

### 5.6 When the analysis is not run as confirmatory
Suppose fewer than 20 awarded repositories can be matched across all tracks, or no track-level award list is published (for example, if only overall winners are named). Then no hypothesis tests are reported: we report only descriptive comparisons with intervals, labelled as such. If only overall winners are named, track enters the secondary model as a covariate instead of as a stratum.

## 6. Reporting and ethics
- Results are reported in aggregate, by predictor and by track. We do not publish a list that links winning teams to repository features.
- The repositories and the award lists are public. No personal data beyond public team names are used, and the names are used only for linking.
- Any deviation from this plan is reported in the paper, with its reason.

## 7. Files attached to the registration
- `jury_preregistration.md` (this document)
- `freeze_predictors.py` (builds the frozen predictor table)
- `jury_predictors.sha256` (hash of the frozen table)
