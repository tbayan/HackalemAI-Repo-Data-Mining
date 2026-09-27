"""Fetch abstracts for screened references so they can be read before citing.

Tries Crossref, then DataCite (arXiv DOIs), then OpenAlex. Writes notes/abstracts_2.md.
Usage: python fetch_abstracts.py key1 key2 ...   (keys from screening.csv)
"""
from __future__ import annotations

import csv
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "hackalem-lit-review/1.0 (mailto:talgar.bayan@gmail.com)"}


def get(url: str) -> dict | None:
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except Exception as err:  # noqa: BLE001
            if "429" in str(err):
                time.sleep(20)
                continue
            return None
    return None


def clean(text: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def abstract_for(doi: str) -> tuple[str, str]:
    d = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    if d and d["message"].get("abstract"):
        return "crossref", clean(d["message"]["abstract"])
    if doi.lower().startswith("10.48550"):
        d = get("https://api.datacite.org/dois/" + urllib.parse.quote(doi.lower()))
        if d:
            for desc in d["data"]["attributes"].get("descriptions", []):
                if desc.get("descriptionType") == "Abstract":
                    return "datacite", clean(desc["description"])
    d = get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi) + "?mailto=talgar.bayan@gmail.com")
    if d and d.get("abstract_inverted_index"):
        idx = d["abstract_inverted_index"]
        words = sorted((pos, w) for w, positions in idx.items() for pos in positions)
        return "openalex", " ".join(w for _, w in words)
    return "none", "(no abstract found)"


def main() -> None:
    rows = {r["key"]: r for r in csv.DictReader((HERE / "screening.csv").open(encoding="utf-8"))}
    out = ["# Abstracts, batch 2 (fetched for reading before citing)\n"]
    for key in sys.argv[1:]:
        r = rows[key]
        src, text = abstract_for(r["doi_or_url"])
        out.append(f"## {key} ({r['year']}, {r['venue']}) [{src}]\n**{r['title']}**\n\n{text}\n")
        print(f"{key}: {src}")
        time.sleep(0.4)
    import os
    (HERE / "notes" / os.environ.get("ABSTRACTS_OUT", "abstracts_2.md")).write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
