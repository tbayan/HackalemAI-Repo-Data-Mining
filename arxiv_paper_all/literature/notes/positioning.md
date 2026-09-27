# Positioning: what is already known, and what this study adds

Based on the searches in `../search_log.csv` (24 keyword queries plus targeted lookups, 2026-09-24)
and the abstracts in `abstracts.md`. Claims marked **safe** are supported by what we found; claims
marked **not safe** must not appear in the paper.

## What prior work has done

| Line of work | Closest papers | What they studied | Scale / method |
|---|---|---|---|
| Hackathons on GitHub | HackRep (Halmans et al., MSR 2026); McIntosh & Hardin (SIGCSE 2021); Nolte et al. (CSCW 2020) | Many hackathons, repositories linked from project listings; continuation, team composition, geography | 100,356 repos across many events; self-selected (only listed projects) |
| Generative AI in hackathons | Zhou, Serebrenik & Nolte (2026); Gama et al. (2025); Chen et al. (2026); Sajja et al. (2024) | What participants use GenAI for; novices and vibe coding; educational value | Interviews at one event; 31 participants / 9 teams; month-long online event with surveys; one case study |
| Coding agents in the wild | Li, Zhang & Hassan (AIDev, 2025); Agarwal, He & Vasilescu (MSR 2026); MSR 2026 agentic-PR papers | Agent-authored pull requests in open-source projects | 456k PRs, 61k repos; mostly established projects and professional developers |
| Agent context files | Chatlatanagulchai et al. (2025); Gloaguen et al. (2026); Treude et al. (2026) | Structure, content and usefulness of AGENTS.md / CLAUDE.md | 2,303 files in 1,925 repos; benchmark ablations |
| Secrets and AI-built software | Meli et al. (NDSS 2019); Basak et al. (MSR 2023); Gao et al. (2026, LLM API keys in iOS apps); Deng et al. (2026, vibe-coded apps) | Secret leakage in public repos; LLM key leakage; vulnerabilities in vibe-coded apps | Large scans of GitHub; 444 iOS apps; 9,041 apps / 200 audited |

## What this study adds (the "good parts")

1. **A complete population, not a self-selected sample.** Every registration received a repository, so we observe teams that never pushed code as well as those that did. Datasets built from project listings (e.g. HackRep) only contain projects someone chose to list, so they cannot measure the participation funnel. **Safe.**
2. **One event, one fixed five-hour window, agent use required.** All active teams worked under the same deadline and the same tooling requirement. This lets us study time use and agent footprints across about a thousand teams. The GenAI-in-hackathon studies above are qualitative and cover 9 teams to one event's worth of interviewees. **Safe**, as a scale and design difference, not a quality judgement.
3. **A different population from agent-PR studies.** Mostly students and early-career developers building new projects in five hours, in Kazakhstan, documenting in Kazakh, Russian and English. The agent-PR literature studies established open-source projects. **Safe.** Do not claim "first study in Central Asia" without a dedicated search.
4. **Security hygiene where LLM API keys were part of the task.** Teams were given OpenAI resources and had to call LLM APIs. We can report how often secret-like strings and `.env` files reached public history. This links the secret-leakage literature with the new LLM-key work. **Safe once M2 results exist.**
5. **Validity lessons for mining organiser-created repositories.** Template commits from two organiser accounts, commits on non-default branches, repository ≠ team ≠ person. **Safe** (documented).

## Claims to avoid (or to reword)

| Tempting claim | Why not | Use instead |
|---|---|---|
| "The first vibe-coding hackathon" | Chen et al. (2026) and Gama et al. (2025) already study vibe-coding hackathons | "an agent-assisted hackathon at a scale of several thousand registrations" |
| "The first study of GenAI in hackathons" | Zhou et al. (2026), Sajja et al. (2024), Gama et al. (2025) | "to our knowledge, the first repository-level study of a complete hackathon population in which AI-agent use was required" (keep hedged; re-check before submission) |
| "The largest hackathon ever / world record" | Guinness result pending | "organised as an official Guinness World Records attempt; result pending" |
| "Teams used AI to write X% of code" | Code authorship cannot be attributed from git data | "agent configuration files appear in N repositories" |

## Still to search before writing Related Work
- Hackathon time use and deadline effects (commit timing near deadlines; student procrastination studies).
- Software engineering / computing education research in Central Asia or Kazakhstan (for point 3; no claim until searched).
- Technology choices of student or hackathon projects (for RQ3).
- Multilingual documentation on GitHub (for RQ5).
