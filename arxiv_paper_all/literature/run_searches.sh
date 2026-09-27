#!/usr/bin/env bash
# Run every query in queries.txt through DataCite (arXiv DOIs) and Crossref.
# Raw results go to notes/raw_results.md for screening; each search is logged in search_log.csv.
cd "$(dirname "$0")"
P=../../.venv/bin/python
OUT=notes/raw_results.md
echo "# Raw search results ($(date -I))" > "$OUT"
grep -v '^#' queries.txt | while IFS='|' read -r group query; do
  query=$(echo "$query" | xargs)
  { echo; echo "## [$group] $query"; echo "### DataCite (arXiv)"; timeout 60 $P lookup.py datacite "$query" 2>&1
    echo "### Crossref"; timeout 60 $P lookup.py crossref "$query" 2>&1; } >> "$OUT"
  sleep 1
done
echo "done: $(grep -c '^## ' "$OUT") queries"
