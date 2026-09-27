# Build the paper and run the checks.
#   make numbers  regenerate numbers.tex from the facts file
#   make pdf      pdflatex + bibtex + pdflatex x2
#   make check    banned words, literal numbers, citations
#   make all      numbers, check, pdf
PY ?= ../../.venv/bin/python

.PHONY: all numbers pdf check clean

all: numbers check pdf

numbers:
	$(PY) ../analysis/make_numbers.py

pdf: numbers
	pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
	-bibtex main > /dev/null
	pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
	pdflatex -interaction=nonstopmode -halt-on-error main.tex | grep -E "Warning|Error" || true
	@echo "built main.pdf"

check:
	$(PY) ../checks/lint_banned_words.py
	$(PY) ../checks/check_numbers.py
	$(PY) ../checks/check_citations.py

clean:
	rm -f *.aux *.log *.bbl *.blg *.out *.toc main.pdf
