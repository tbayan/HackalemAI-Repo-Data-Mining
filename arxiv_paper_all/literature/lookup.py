"""Look up candidate references and log every search.

Usage:
  python lookup.py crossref "How bad can it git secret leakage"
  python lookup.py doi 10.1145/3415230          (metadata for one DOI)
  python lookup.py abstract 10.1145/3415230     (abstract via Semantic Scholar)
  python lookup.py openalex "vibe coding"        (main search; add a year filter: FROM=2024 python lookup.py openalex ...)
  python lookup.py arxiv "vibe coding"           (arXiv API; returns HTTP 406 from this machine as of 2026-09-24)
  python lookup.py dblp "..."                    (dblp; its API is behind a bot check as of 2026-09-24)

Each call appends a row to search_log.csv (date, source, query, hits) so the
review can be reported and repeated. Results are printed for screening; nothing
is added to references.bib automatically.
"""
from __future__ import annotations

import csv
import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "search_log.csv"
UA = {"User-Agent": "hackalem-lit-review/1.0 (mailto:talgar.bayan@gmail.com)"}


def get_json(url: str, attempts: int = 5) -> dict:
    """GET JSON, waiting and retrying when the service rate-limits (HTTP 429)."""
    import time
    import urllib.error
    for attempt in range(attempts):
        req = urllib.request.Request(url, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code != 429 or attempt == attempts - 1:
                raise
            wait = int(err.headers.get("Retry-After") or 35) + 2
            print(f"(rate-limited; waiting {wait}s)", file=sys.stderr)
            time.sleep(wait)


def log(source: str, query: str, hits: int) -> None:
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "source", "query", "hits"])
        w.writerow([date.today().isoformat(), source, query, hits])


def arxiv(query: str, n: int = 8) -> None:
    import xml.etree.ElementTree as ET
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": f'all:"{query}"', "max_results": n, "sortBy": "relevance"})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entries = root.findall("a:entry", ns)
    log("arxiv", query, len(entries))
    for e in entries:
        authors = [a.findtext("a:name", namespaces=ns) for a in e.findall("a:author", ns)]
        title = " ".join(e.findtext("a:title", namespaces=ns).split())
        print(f"- {e.findtext('a:published', namespaces=ns)[:10]} | arXiv | {title}")
        print(f"    {', '.join(authors[:6])}{' et al.' if len(authors) > 6 else ''}")
        print(f"    id: {e.findtext('a:id', namespaces=ns)}")


def openalex(query: str, n: int = 10) -> None:
    import os
    params = {"search": query, "per-page": n, "sort": "relevance_score:desc",
              "mailto": "talgar.bayan@gmail.com"}
    if os.environ.get("FROM"):
        params["filter"] = f"from_publication_date:{os.environ['FROM']}-01-01"
    data = get_json("https://api.openalex.org/works?" + urllib.parse.urlencode(params))
    log("openalex" + (f">={os.environ['FROM']}" if os.environ.get("FROM") else ""), query,
        data["meta"]["count"])
    for w in data["results"]:
        venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "-"
        authors = [a["author"]["display_name"] for a in w.get("authorships", [])]
        ids = w.get("ids", {})
        print(f"- {w.get('publication_year')} | {venue} | {w.get('title')} | cited {w.get('cited_by_count')}")
        print(f"    {', '.join(authors[:5])}{' et al.' if len(authors) > 5 else ''}")
        print(f"    doi: {ids.get('doi', '-')}")


def datacite(query: str, n: int = 8) -> None:
    """DataCite holds the DOIs arXiv registers (10.48550/arXiv.*): use it to confirm preprints."""
    data = get_json("https://api.datacite.org/dois?" + urllib.parse.urlencode(
        {"query": query, "page[size]": n, "client-id": "arxiv.content"}))
    log("datacite-arxiv", query, data["meta"]["total"])
    for d in data["data"]:
        a = d["attributes"]
        authors = [c.get("name", "") for c in a.get("creators", [])]
        print(f"- {a.get('publicationYear')} | arXiv | {(a.get('titles') or [{}])[0].get('title')}")
        print(f"    {'; '.join(authors[:5])}{' et al.' if len(authors) > 5 else ''}")
        print(f"    doi: {a.get('doi')}")


def abstract(value: str) -> None:
    url = ("https://api.semanticscholar.org/graph/v1/paper/DOI:" + urllib.parse.quote(value)
           + "?fields=title,year,venue,abstract,citationCount")
    it = get_json(url)
    log("semanticscholar", value, 1)
    print(f"{it.get('year')} | {it.get('venue')} | {it.get('title')} | cited {it.get('citationCount')}")
    print(it.get("abstract") or "(no abstract available)")


def dblp(query: str, n: int = 8) -> None:
    url = "https://dblp.org/search/publ/api?" + urllib.parse.urlencode({"q": query, "format": "json", "h": n})
    hits = get_json(url)["result"]["hits"]
    log("dblp", query, int(hits.get("@total", 0)))
    for hit in hits.get("hit", []):
        info = hit["info"]
        authors = info.get("authors", {}).get("author", [])
        authors = [a["text"] for a in (authors if isinstance(authors, list) else [authors])]
        print(f"- {info.get('year')} | {info.get('venue')} | {info.get('title')}")
        print(f"    {', '.join(authors[:6])}{' et al.' if len(authors) > 6 else ''}")
        print(f"    doi: {info.get('doi', '-')}  dblp: {info.get('key')}")


def crossref(query: str, n: int = 6) -> None:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": query, "rows": n})
    items = get_json(url)["message"]["items"]
    log("crossref", query, len(items))
    for it in items:
        year = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])]
        print(f"- {year} | {(it.get('container-title') or ['-'])[0]} | {(it.get('title') or ['-'])[0]}")
        print(f"    {', '.join(authors[:6])}{' et al.' if len(authors) > 6 else ''}")
        print(f"    doi: {it.get('DOI')}")


def doi(value: str) -> None:
    it = get_json("https://api.crossref.org/works/" + urllib.parse.quote(value))["message"]
    log("crossref-doi", value, 1)
    year = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
    authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])]
    print(f"{year} | {(it.get('container-title') or ['-'])[0]} | {(it.get('title') or ['-'])[0]}")
    print(f"authors: {', '.join(authors)}")
    print(f"type: {it.get('type')}  publisher: {it.get('publisher')}  doi: {it.get('DOI')}")


if __name__ == "__main__":
    {"dblp": dblp, "crossref": crossref, "doi": doi, "arxiv": arxiv, "abstract": abstract, "openalex": openalex, "datacite": datacite}[sys.argv[1]](" ".join(sys.argv[2:]))
