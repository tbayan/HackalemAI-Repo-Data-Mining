"""Link the official award list to repositories (pre-registration, Section 4).

Reads only repository names, the frozen track labels and the activity flag (membership of the frozen
predictor file); no predictor value is read. Output: data/prereg/award_matches.csv and a report.
"""
import csv, re, difflib
from collections import defaultdict

CYR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюяәғқңөұүһі",
  ["a","b","v","g","d","e","e","zh","z","i","i","k","l","m","n","o","p","r","s","t","u","f","kh","ts","ch","sh","shch","","y","","e","iu","ia","a","g","q","n","o","u","u","h","i"]))

def norm(s):
    s = "".join(CYR.get(ch, ch) for ch in s.lower())
    return re.sub(r"[^a-z0-9]", "", s)

def team_part(repo):                      # hack-<id>-<team>
    m = re.match(r"hack-[0-9a-f]+-(.*)$", repo)
    return m.group(1) if m else repo

all_repos = [r["name"] for r in csv.DictReader(open("data/repos.csv", encoding="utf-8"))]
frozen = {r["repo"]: r["track"] for r in csv.DictReader(open("data/prereg/jury_predictors.csv", encoding="utf-8"))}  # repo -> track (active repos only)
awards = list(csv.DictReader(open("data/prereg/awards_official.csv", encoding="utf-8")))

by_norm = defaultdict(list)
for r in all_repos:
    by_norm[norm(team_part(r))].append(r)

out = []
for a in awards:
    key = norm(a["team"])
    exact = by_norm.get(key, [])
    cands = exact or [r for r in all_repos
                      if difflib.SequenceMatcher(None, key, norm(team_part(r))).ratio() >= 0.85]
    kind = "exact" if exact else ("fuzzy" if cands else "none")
    act = [r for r in cands if r in frozen]
    in_track = [r for r in act if frozen[r] == a["track"]]
    if len(in_track) == 1:
        repo, status = in_track[0], f"{kind}: active, same track"
    elif len(in_track) > 1:
        repo, status = "", f"{kind}: ambiguous ({len(in_track)} active repos in the track)"
    elif act:
        repo, status = "", f"{kind}: active only in other track(s) " + ";".join(f"{r}[T{frozen[r]}]" for r in act)
    elif cands:
        repo, status = "", f"{kind}: only inactive repo(s) " + ";".join(cands[:3])
    else:
        repo, status = "", "no repository with this name"
    out.append({**{k: a[k] for k in ("track", "place", "team")}, "norm": key,
                "candidates": ";".join(cands[:5]), "repo": repo, "status": status})

with open("data/prereg/award_matches.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in out:
    print(f"T{int(o['track']):<2} {o['place']} {o['team']:<20} -> {o['repo'] or '-':<36} {o['status']}  [{o['candidates']}]")
print("matched:", sum(1 for o in out if o["repo"]), "of", len(out))
