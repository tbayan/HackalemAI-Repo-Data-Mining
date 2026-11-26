# Revision 1 (BDCC review, November 2026)

Scripts for the analyses added in the first revision of the paper. Each one reads the private files in `data/` and the clones, writes aggregates only, and first reproduces published values before computing anything new. They are exploratory and listed as deviations 34–39 in `../deviations.md`.

| Script | Output | What it computes |
|---|---|---|
| `revision_numbers.py` | `revision_numbers.json` | Team commits around 13:00 and 18:00; the window-dependent measures with the start moved (end fixed at 18:00) and with the whole window shifted; the evening batch and repositories created after registration closed; repeated team names; trace shares without the batch; READMEs changed by agent-signed commits (checked by a second route) and README length by agent trace |
| `jury_revision.py` | `jury_revision.json` | The registered jury tests, run with the registered code, among repositories that look like a finished submission (a team commit in 17:00–18:00 and a written README with run or setup instructions), and H1 with the window start moved |
| `llm_validation_sample.py` | (private sheet and key) | A stratified random sample of 60 coded repositories (5 per track, seed 20261126, pilot repositories excluded) for blind hand coding, with the same input the model received |
| `llm_validation_full_readmes.py` | (private companion page) | The full cleaned README and file list of each sampled repository, for the items whose excerpt does not show the method |
| `llm_validation_agreement.py` | `llm_validation_agreement.json` | Agreement between the model's coding and the author's blind coding: raw agreement, Cohen's kappa with a bootstrap interval, track-weighted agreement and confusion matrices |

Run from the repository root, for example `python analysis/revision_r1/revision_numbers.py .`. The hand-coding sheet, its key and the companion page link repositories to their names and are not released.
