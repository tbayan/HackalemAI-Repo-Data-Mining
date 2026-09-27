"""Result figures (Figs. 2-6), drawn only from analysis/facts_paper.json and tables/*.csv."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportion_confint

import paper_style as ps

PAPER = Path(__file__).resolve().parent.parent
F = json.loads((PAPER / "analysis" / "facts_paper.json").read_text())
TABLES = PAPER / "tables"


def wilson(k: int, n: int) -> tuple[float, float, float]:
    lo, hi = proportion_confint(k, n, method="wilson")
    return 100 * k / n, 100 * lo, 100 * hi


def fig_participation() -> None:
    fig, (a, b) = ps.new_figure(ps.FULL, 2.15, ncols=2, gridspec_kw={"width_ratios": [1.05, 1]})
    stages = [("Repositories created", F["repos_total"]), ("With team commits", F["repos_with_commits"]),
              ("Active in event window", F["repos_active"]), ("Matched to a track", F["repos_matched_track"])]
    y = np.arange(len(stages))[::-1]
    a.barh(y, [v for _, v in stages], height=0.52, color=ps.BLUE)
    for yi, (_, v) in zip(y, stages):
        a.text(v + 60, yi, f"{v:,} ({100 * v / F['repos_total']:.1f}%)", va="center", fontsize=7.5, color=ps.INK)
    a.set_yticks(y, [s for s, _ in stages])
    a.set_xlim(0, F["repos_total"] * 1.42)
    a.set_xlabel("Repositories")
    ps.thousands(a, "x")
    ps.tidy(a, grid_axis="x")
    a.set_title("(a) From provisioning to activity", loc="left", fontsize=8.5)

    reg = F["registration"]
    batch = F["batch"]
    other22 = (reg["sep22"]["n"] - batch["n"], reg["sep22"]["active"] - batch["active"])
    groups = [("Before\n1 Sep", reg["before_sep01"]["n"], reg["before_sep01"]["active"]),
              ("1–14\nSep", reg["sep01_14"]["n"], reg["sep01_14"]["active"]),
              ("15–21\nSep", reg["sep15_21"]["n"], reg["sep15_21"]["active"]),
              ("22 Sep\n(other)", other22[0], other22[1]),
              ("22 Sep\n(batch)", batch["n"], batch["active"])]
    for i, (label, n, k) in enumerate(groups):
        p, lo, hi = wilson(k, n)
        colour = ps.VERMILLION if "batch" in label else ps.BLUE
        b.errorbar(i, p, yerr=[[p - lo], [hi - p]], fmt="o", color=colour, ms=4.5, capsize=2.5, lw=0.9)
        b.text(i, hi + 3, f"n={n:,}", ha="center", fontsize=6.8, color=ps.INK2)
    b.set_xticks(range(len(groups)), [g[0] for g in groups])
    b.set_ylim(0, 75)
    b.set_xlim(-0.5, len(groups) - 0.5)
    b.set_ylabel("Active repositories (%)")
    b.set_title("(b) Share active by repository creation date", loc="left", fontsize=8.5)
    fig.tight_layout(w_pad=2.0)
    ps.save(fig, "fig_participation")


def fig_rhythm() -> None:
    fig, (a, b) = ps.new_figure(ps.FULL, 2.2, ncols=2, gridspec_kw={"width_ratios": [1.35, 1]})
    tl = pd.read_csv(TABLES / "timeline_10min.csv")
    x = 11 + (tl.minutes_after_11 + 5) / 60
    a.axvspan(13, 18, color=ps.TINT, lw=0)
    a.fill_between(x, tl.commits, color=ps.BLUE, alpha=0.15, lw=0)
    a.plot(x, tl.commits, color=ps.BLUE, lw=1.3)
    a.axvline(18, color=ps.VERMILLION, lw=0.9)
    a.text(18.07, tl.commits.max() * 0.97, "Deadline\n18:00", fontsize=7, color=ps.INK2, va="top")
    a.text(13.07, tl.commits.max() * 0.97, "Start 13:00", fontsize=7, color=ps.INK2, va="top")
    a.set_xlim(11, 19)
    a.set_xticks(range(11, 20), [f"{h}:00" for h in range(11, 20)])
    a.set_ylabel("Team commits per 10 min")
    a.set_xlabel("Local time (UTC+5), 23 September 2026")
    ps.thousands(a)
    a.set_title("(a) Commits over the event day (all branches)", loc="left", fontsize=8.5)

    clusters = F["rhythm_clusters"]
    hours = [13, 14, 15, 16, 17]
    width = 0.38
    names = ["Steady", "Late surge"]
    colours = [ps.BLUE, ps.VERMILLION]
    for i, c in enumerate(clusters):
        vals = [c[f"h{h}"] for h in hours]
        b.bar(np.arange(5) + (i - 0.5) * width, vals, width=width, color=colours[i],
              label=f"{names[i]} ({c['size']:,} teams, {c['pct']:.0f}%)")
    b.set_xticks(range(5), [f"{h}:00" for h in hours])
    b.set_ylabel("Share of a team's commits (%)")
    b.set_xlabel("Hour of the event")
    b.legend(loc="upper left", fontsize=7)
    b.set_ylim(0, 70)
    b.set_title("(b) Two work-rhythm clusters", loc="left", fontsize=8.5)
    fig.tight_layout(w_pad=2.0)
    ps.save(fig, "fig_rhythm")


def fig_footprint() -> None:
    n = F["stack_n"]
    rows = [
        ("Engineering", "Test files", F["has_tests"]),
        ("Engineering", "Dockerfile", F["has_dockerfile"]),
        ("Engineering", "Docker Compose file", F["has_compose"]),
        ("Engineering", "CI workflow", F["has_ci"]),
        ("Engineering", "Deployment config", F["has_deploy_config"]),
        ("LLM use", "Any LLM SDK", F["any_llm_sdk"]),
        ("LLM use", "OpenAI SDK", {"n": F["llm_providers"]["OpenAI"]["n"]}),
        ("Agent footprint", "Any agent context file", F["any_agent_file"]),
        ("Agent footprint", "AGENTS.md", F["agents_md"]),
        ("Agent footprint", "CLAUDE.md", F["claude_md"]),
        ("Agent footprint", "Pull-request refs", F["repos_pr_refs"]),
        ("Agent footprint", "Agent-signed commits", F["repos_agent_signed"]),
        ("Agent footprint", "Agent-named branch", F["repos_agent_branch"]),
    ]
    fig, ax = ps.new_figure(ps.FULL, 2.9)
    ps.tidy(ax, grid_axis="x")
    colours = {"Engineering": ps.BLUE, "LLM use": ps.GREEN, "Agent footprint": ps.VERMILLION}
    ypos, y = [], 0
    last_group = None
    for group, label, d in rows:
        if group != last_group and last_group is not None:
            y += 0.6
        ypos.append(y)
        p, lo, hi = wilson(d["n"], n)
        ax.errorbar(p, -y, xerr=[[p - lo], [hi - p]], fmt="o", color=colours[group], ms=4, capsize=2, lw=0.9)
        ax.text(hi + 1.2, -y, f"{p:.1f}%  ({d['n']:,})", va="center", fontsize=7, color=ps.INK2)
        last_group = group
        y += 1
    ax.set_yticks([-v for v in ypos], [r[1] for r in rows])
    ax.set_xlim(0, 100)
    ax.set_xlabel(f"Share of the {n:,} repositories with team commits (%, 95% Wilson CI)")
    for group, colour in colours.items():
        ax.plot([], [], "o", color=colour, label=group, ms=4)
    ax.legend(loc="lower right", fontsize=7, ncol=3)
    fig.tight_layout()
    ps.save(fig, "fig_footprint")


def fig_language() -> None:
    fig, ax = ps.new_figure(ps.FULL, 1.55)
    ps.tidy(ax, grid_axis="")
    readme_n = F["readme_written_n"]
    commits_n = F["team_commits_total"]
    bars = [
        (f"README files (n={readme_n:,})", [("Russian", F["readme_russian"]["n"], ps.BLUE),
                                             ("English", F["readme_english"]["n"], ps.GREEN),
                                             ("Kazakh", F["readme_kazakh"]["n"], ps.VERMILLION),
                                             ("Mixed", F["readme_mixed"]["n"], ps.GRAY)], readme_n),
        (f"Commit messages (n={commits_n:,})", [("Latin", F["commit_script_latin"]["n"], ps.GREEN),
                                                 ("Cyrillic", F["commit_script_cyrillic"]["n"], ps.BLUE),
                                                 ("Kazakh letters", F["commit_script_kazakh"]["n"], ps.VERMILLION)], commits_n),
    ]
    for i, (label, parts, total) in enumerate(bars):
        left = 0
        for name, k, colour in parts:
            w = 100 * k / total
            ax.barh(-i, w, left=left, height=0.55, color=colour, edgecolor="white", linewidth=0.8)
            if w >= 15:
                ax.text(left + w / 2, -i, f"{name} {w:.1f}%", ha="center", va="center", fontsize=7, color="white")
            left += w
        small = ", ".join(f"{n_} {100 * k / total:.1f}%" for n_, k, _ in parts if 100 * k / total < 15)
        ax.text(101, -i, small, va="center", fontsize=7, color=ps.INK2)
    ax.set_yticks([0, -1], [b[0] for b in bars])
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=c, label=n) for n, c in [("Russian / Cyrillic", ps.BLUE), ("English / Latin", ps.GREEN),
                                                         ("Kazakh", ps.VERMILLION), ("Mixed", ps.GRAY)]]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=4, fontsize=7, handlelength=1.2)
    fig.tight_layout()
    ps.save(fig, "fig_language")


def fig_security() -> None:
    fig, (a, b) = ps.new_figure(ps.FULL, 1.9, ncols=2, gridspec_kw={"width_ratios": [1.25, 1]})
    names = {"openaiapikey": "OpenAI API key", "curlauthheader": "Auth header in curl", "gcpapikey": "Google Cloud API key",
             "jwt": "JSON Web Token", "curlauthuser": "Credentials in curl", "telegrambotapitoken": "Telegram bot token",
             "stripeaccesstoken": "Stripe access token"}
    tot, fin = F["provider_rules_repos"], F["provider_rules_final"]
    order = sorted(tot, key=tot.get)
    y = np.arange(len(order))
    final = [fin.get(k, 0) for k in order]
    hist = [tot[k] - fin.get(k, 0) for k in order]
    a.barh(y, final, height=0.55, color=ps.VERMILLION, label="Still in final version")
    a.barh(y, hist, left=final, height=0.55, color=ps.LIGHT, label="Only in history")
    for yi, k in zip(y, order):
        a.text(tot[k] + 0.8, yi, str(tot[k]), va="center", fontsize=7, color=ps.INK2)
    a.set_yticks(y, [names[k] for k in order])
    a.set_xlabel("Repositories")
    a.set_xlim(0, max(tot.values()) * 1.18)
    ps.tidy(a, grid_axis="x")
    a.legend(loc="lower right", fontsize=7)
    a.set_title("(a) Provider-specific secret patterns", loc="left", fontsize=8.5)

    files = F["openai_key_files"]
    parts = [(".env.example", files["env_example"]), (".env", files["env"]),
             ("Other .env variants", files["env_other"]), ("Source or text files", files["other"])]
    yb = np.arange(len(parts))[::-1]
    b.barh(yb, [v for _, v in parts], height=0.55, color=ps.BLUE)
    for yi, (_, v) in zip(yb, parts):
        b.text(v + 0.5, yi, str(v), va="center", fontsize=7, color=ps.INK2)
    b.set_yticks(yb, [p[0] for p in parts])
    b.set_xlabel("OpenAI key occurrences")
    b.set_xlim(0, max(v for _, v in parts) * 1.2)
    ps.tidy(b, grid_axis="x")
    b.set_title("(b) Files holding OpenAI keys", loc="left", fontsize=8.5)
    fig.tight_layout(w_pad=2.0)
    ps.save(fig, "fig_security")


if __name__ == "__main__":
    fig_participation()
    fig_rhythm()
    fig_footprint()
    fig_language()
    fig_security()
