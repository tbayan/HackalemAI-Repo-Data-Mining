# Paper: HackAlem AI repository study

Everything for the paper lives here: the LaTeX source, the figures and the code that makes them, the analyses, the literature review, the internal reviews and the checks. The derived public dataset is in `../public_data_generated/`.

## Layout

| Folder | Contents |
|---|---|
| `latex/` | `main.tex` (the whole paper); `references.bib` (generated); `numbers.tex` (generated, never edit); `event_macros.tex` (sourced event facts), `method_macros.tex` (method constants), `lit_macros.tex` (numbers quoted from the literature); vendored `arxiv.sty` |
| `analysis/` | `run_analysis.py` (every statistic) → `facts_paper.json`; `make_numbers.py` → `latex/numbers.tex`; `analysis_plan.md`, `deviations.md`; `reproduce_public.py` (headline numbers from the public data alone) |
| `figure_code/` | `paper_style.py` (one style for every figure) and `make_figures.py` (Figs. 2–6) |
| `figures/` | Generated PDFs and PNG previews; `architecture.tex` (Fig. 1, TikZ) |
| `tables/` | CSV tables behind the figures |
| `prereg/` | Pre-registration of the jury-outcome analysis and the script that freezes its predictors |
| `literature/` | Search log, screening table, abstracts read, `build_bib.py`, `reference_audit.md` |
| `reviews/` | The two internal reviews, the editor's assessment and decision, and the response to reviewers |
| `versions/` | Frozen earlier versions (v1 of 26 September 2026) |
| `writing/` | Style guide (with reporting conventions), banned words, allowed literals, claim ledger |
| `checks/` | Banned-word lint, literal-number check, citation check, reference audit, independent recount |

## Rebuild

```bash
# 1. from the clones (private; needs data/clones): features
python src/extract_commits.py; python src/extract_stack.py; python src/readme_features.py
# 2. independent recount, analysis, macros, figures, public data
python arxiv_paper_all/checks/recompute_core.py
python arxiv_paper_all/analysis/run_analysis.py
python arxiv_paper_all/analysis/make_numbers.py
(cd arxiv_paper_all/figure_code && python make_figures.py)
python src/export_public_data.py
python arxiv_paper_all/analysis/reproduce_public.py      # also runs from the public data alone
# 3. paper
cd arxiv_paper_all/latex && make check && make pdf
python ../checks/audit_references.py                    # network: DOI and URL audit of references.bib
```

`make check` must pass before a draft is shared:
- **Banned words:** no word or phrase from `writing/banned_words.txt` appears.
- **Numbers:** every data number in the prose is a macro; any other literal is listed in `writing/allowed_literals.txt`.
- **Citations:** every reference is marked verified, has a DOI or URL, and is cited.

## Rules

See `writing/style_guide.md`:
- no number without a source;
- no claim without evidence (`writing/claim_ledger.md`);
- plain wording;
- only references whose abstract we have read.

## Credits

`latex/arxiv.sty` is from [kourgeorge/arxiv-style](https://github.com/kourgeorge/arxiv-style) (MIT licence).
