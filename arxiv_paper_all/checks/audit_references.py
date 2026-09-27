"""Audit every entry of latex/references.bib against the registries, independently of how it was built.

For each entry with a DOI:
  - resolve the DOI at doi.org (must redirect);
  - fetch the registry record (Crossref; DataCite for arXiv DOIs 10.48550/*);
  - compare title, first author, author count and year with the bib entry.
For each peer-reviewed entry at a venue without DOIs (ICLR, USENIX): check the arXiv DOI
given in its note against DataCite, and fetch the venue URL.
For each entry without a DOI (grey literature): fetch the URL and record the HTTP status.
For each arXiv preprint: search Crossref and OpenAlex by title for a peer-reviewed
version with its own DOI, so the preprint can be replaced if one exists.

Writes literature/reference_audit.md and literature/reference_audit.csv. Network access needed.
Usage: python checks/audit_references.py
"""
from __future__ import annotations

import csv
import difflib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
BIB = PAPER / "latex" / "references.bib"
OUT_MD = PAPER / "literature" / "reference_audit.md"
OUT_CSV = PAPER / "literature" / "reference_audit.csv"
UA = {"User-Agent": "hackalem-reference-audit/1.0 (mailto:talgar.bayan@gmail.com)"}


# ------------------------------------------------------------------ bib parsing
def parse_bib(text: str) -> list[dict]:
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        i, depth = m.end(), 1
        while depth and i < len(text):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[m.end():i - 1]
        fields, j = {}, 0
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            if fm.start() < j:
                continue
            k = fm.end()
            if k < len(body) and body[k] == "{":
                d, s = 0, k
                while k < len(body):
                    d += {"{": 1, "}": -1}.get(body[k], 0)
                    k += 1
                    if d == 0:
                        break
                value = body[s + 1:k - 1]
            else:
                e = re.match(r"[^,\n]*", body[k:]).end()
                value = body[k:k + e]
                k += e
            fields[fm.group(1).lower()] = value.strip()
            j = k
        entries.append({"type": m.group(1).lower(), "key": m.group(2), **fields})
    return entries


def norm(s: str) -> str:
    s = re.sub(r"\\[a-zA-Z]+|[{}`'\"]", "", s or "").lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def bib_authors(entry: dict) -> list[str]:
    raw = entry.get("author", "")
    out = []
    for a in re.split(r"\s+and\s+", raw):
        a = a.strip()
        if not a:
            continue
        out.append(a.split(",")[0].strip() if "," in a else a.split()[-1])
    return out


# ------------------------------------------------------------------ network
def get_json(url: str, attempts: int = 4):
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return None
            if err.code != 429 or attempt == attempts - 1:
                raise
            time.sleep(int(err.headers.get("Retry-After") or 20) + 2)
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
            time.sleep(5)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def doi_resolves(doi: str) -> str:
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request("https://doi.org/" + urllib.parse.quote(doi), headers=UA, method="HEAD")
    try:
        opener.open(req, timeout=30)
        return "200 (no redirect)"
    except urllib.error.HTTPError as err:
        return f"{err.code} -> {err.headers.get('Location', '')[:80]}" if err.code in (301, 302, 303, 307, 308) else f"HTTP {err.code}"
    except Exception as err:  # noqa: BLE001
        return f"error: {err}"


def url_status(url: str) -> str:
    req = urllib.request.Request(url, headers={**UA, "User-Agent": "Mozilla/5.0 (reference check)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return f"HTTP {r.status}"
    except urllib.error.HTTPError as err:
        return f"HTTP {err.code}"
    except Exception as err:  # noqa: BLE001
        return f"error: {type(err).__name__}"


def registry_record(doi: str) -> dict | None:
    if doi.lower().startswith("10.48550/"):
        d = get_json("https://api.datacite.org/dois/" + urllib.parse.quote(doi))
        if not d:
            return None
        a = d["data"]["attributes"]
        return {"source": "DataCite", "title": (a.get("titles") or [{}])[0].get("title", ""),
                "authors": [c.get("familyName") or c.get("name", "").split(",")[0] for c in a.get("creators", [])],
                "year": a.get("publicationYear"), "venue": "arXiv"}
    d = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    if not d:
        return None
    it = d["message"]
    title = (it.get("title") or [""])[0]
    if it.get("subtitle"):
        title += " " + it["subtitle"][0]
    return {"source": "Crossref", "title": title,
            "authors": [a.get("family", a.get("name", "")) for a in it.get("author", [])],
            "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "venue": (it.get("container-title") or [""])[0]}


def published_versions(title: str) -> list[str]:
    """Peer-reviewed records whose title closely matches an arXiv preprint's title."""
    found = []
    q = urllib.parse.urlencode({"query.bibliographic": norm(title), "rows": 8})
    for it in (get_json("https://api.crossref.org/works?" + q) or {}).get("message", {}).get("items", []):
        t = (it.get("title") or [""])[0]
        if it.get("type") in ("journal-article", "proceedings-article", "book-chapter") and sim(t, title) >= 0.9:
            found.append(f"Crossref {it.get('type')}: {t} | {(it.get('container-title') or [''])[0]} | doi {it.get('DOI')}")
    q = urllib.parse.urlencode({"filter": f"title.search:{norm(title)}", "per-page": 5, "mailto": "talgar.bayan@gmail.com"})
    for w in (get_json("https://api.openalex.org/works?" + q) or {}).get("results", []):
        if sim(w.get("title") or "", title) < 0.9:
            continue
        for loc in w.get("locations", []):
            src = (loc.get("source") or {})
            if src.get("type") in ("journal", "conference") and "arxiv" not in (src.get("display_name") or "").lower():
                found.append(f"OpenAlex {src.get('type')}: {src.get('display_name')} | doi {w.get('doi')}")
    return sorted(set(found))


# ------------------------------------------------------------------ main
def main() -> int:
    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    rows = []
    for e in entries:
        doi = e.get("doi", "").strip()
        row = {"key": e["key"], "type": e["type"], "doi": doi, "year_bib": e.get("year", ""),
               "title_bib": re.sub(r"[{}]", "", e.get("title", ""))}
        if doi:
            row["doi_org"] = doi_resolves(doi)
            rec = registry_record(doi)
            if rec is None:
                row.update(status="FAIL", note="DOI not found in registry")
            else:
                ba, ra = bib_authors(e), rec["authors"]
                t = sim(e.get("title", ""), rec["title"])
                first = bool(ba and ra and norm(ba[0]) == norm(ra[0]))
                year_ok = str(rec["year"]) == e.get("year", "")
                n_ok = len(ba) == len(ra)
                problems = [p for p, ok in [(f"title {t:.2f}", t >= 0.95), ("first author", first),
                                            (f"year {rec['year']}", year_ok), (f"authors {len(ba)} vs {len(ra)}", n_ok)] if not ok]
                row.update(registry=rec["source"], title_registry=rec["title"], venue=rec["venue"],
                           title_sim=f"{t:.2f}", status="ok" if not problems else "CHECK",
                           note="; ".join(problems))
            if doi.lower().startswith("10.48550/"):
                try:
                    pv = published_versions(e.get("title", ""))
                except Exception as err:  # noqa: BLE001
                    pv = [f"search error: {err}"]
                row["published_version"] = " || ".join(pv)
        elif e["type"] == "inproceedings" and re.search(r"doi:(10\.48550/\S+)", e.get("note", "")):
            pre = re.search(r"doi:(10\.48550/\S+)", e["note"]).group(1).rstrip("}.,")
            rec = registry_record(pre)
            t = sim(e.get("title", ""), rec["title"]) if rec else 0.0
            first = bool(rec and bib_authors(e) and norm(bib_authors(e)[0]) == norm(rec["authors"][0]))
            row["url_status"] = url_status(e.get("url", ""))
            row.update(doi=pre, registry="DataCite (preprint)", title_registry=rec["title"] if rec else "",
                       title_sim=f"{t:.2f}", venue=e.get("booktitle", ""),
                       status="venue" if t >= 0.95 and first and row["url_status"] == "HTTP 200" else "CHECK",
                       note="peer-reviewed venue without DOIs; preprint DOI and venue page checked")
        else:
            row["url_status"] = url_status(e.get("url", "")) if e.get("url") else "no url"
            row.update(status="grey", note="no DOI (grey literature)")
        rows.append(row)
        print(f"{row['key']}: {row['status']} {row.get('note', '')}", flush=True)
        time.sleep(0.4)

    cols = ["key", "type", "status", "note", "doi", "doi_org", "registry", "title_sim", "year_bib", "venue",
            "title_bib", "title_registry", "url_status", "published_version"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    n = {s: sum(r["status"] == s for r in rows) for s in ("ok", "venue", "CHECK", "FAIL", "grey")}
    lines = [f"# Reference audit ({time.strftime('%Y-%m-%d')})", "",
             f"Entries: {len(rows)}; DOI registry match ok: {n['ok']}; peer-reviewed venue without DOIs: {n['venue']}; "
             f"to check: {n['CHECK']}; failed: {n['FAIL']}; grey literature: {n['grey']}.", "",
             "| Key | Status | Registry | Title sim. | doi.org | Note | Published version found |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['key']} | {r['status']} | {r.get('registry', '')} | {r.get('title_sim', '')} | "
                     f"{r.get('doi_org', r.get('url_status', ''))[:40]} | {r.get('note', '')} | {r.get('published_version', '')} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD.relative_to(PAPER)} and {OUT_CSV.relative_to(PAPER)}")
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
