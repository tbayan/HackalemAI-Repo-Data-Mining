"""Result figures (Figs. 2-6), drawn only from analysis/facts_paper.json and tables/*.csv.

Colour rule for the whole paper: blue is the main series (and Codex, the required agent),
orange is Claude Code, vermilion marks exceptions and exposure (repositories archived before
the event, the deadline, key strings still present), grey is context (the organiser batch,
strings only in history). Percentages carry one decimal, as in the text.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

import paper_style as ps

PAPER = Path(__file__).resolve().parent.parent
F = json.loads((PAPER / "analysis" / "facts_paper.json").read_text())
TABLES = PAPER / "tables"
P, Q, R, K = F["rq1"], F["rq2"], F["rq3"], F["rq4"]


def title(ax, text: str) -> None:
    ax.set_title(text, loc="left", fontsize=8.5)


def fig_population() -> None:
    fig, (a, b) = ps.new_figure(ps.FULL, 2.2, ncols=2, gridspec_kw={"width_ratios": [1.15, 1]})
    pre, batch = P["prearchived"]["n"], P["batch"]["n"]
    open_nb = P["open"]["n"] - batch
    act_nb, act_b = P["active_of_open_nonbatch"]["n"], P["batch"]["active"]["n"]
    rows = [("Created by the organisers", [(open_nb, ps.BLUE), (batch, ps.GRAY), (pre, ps.VERMILLION)]),
            ("Active in the event window", [(act_nb, ps.BLUE), (act_b, ps.GRAY), (0, ps.VERMILLION)]),
            ("Active, matched to a track", [(P["matched_track"]["n"], ps.BLUE)])]
    for i, (label, parts) in enumerate(rows):
        left = 0
        for v, colour in parts:
            a.barh(-i, v, left=left, height=0.55, color=colour, edgecolor="white", linewidth=0.6)
            left += v
        a.text(left + 60, -i, f"{left:,}", va="center", fontsize=7.5, color=ps.INK)
    a.set_yticks([0, -1, -2], [r[0] for r in rows])
    a.set_xlim(0, P["total"] * 1.18)
    a.set_xlabel("Repositories")
    ps.thousands(a, "x")
    ps.tidy(a, grid_axis="x")
    a.legend(handles=[Patch(color=ps.BLUE, label="Open, not in batch"), Patch(color=ps.GRAY, label="Evening batch, 22 Sep"),
                      Patch(color=ps.VERMILLION, label="Archived before the event")],
             loc="lower right", fontsize=6.8, handlelength=1.0)
    title(a, "(a) Repositories and activity")

    groups = [("Before\n1 Sep", "before_sep01"), ("1–14\nSep", "sep01_14"), ("15–21\nSep", "sep15_21"),
              ("22 Sep\n(other)", "sep22"), ("22 Sep\n(batch)", "batch")]
    for i, (label, key) in enumerate(groups):
        o, al = P["creation"][key]["open"], P["creation"][key]["all"]
        colour = ps.GRAY if key == "batch" else ps.BLUE
        b.errorbar(i, o["pct"], yerr=[[o["pct"] - o["lo"]], [o["hi"] - o["pct"]]], fmt="o", color=colour, ms=4.5,
                   capsize=2.5, lw=0.9)
        if P["creation"][key]["prearchived"]:
            b.plot(i + 0.18, al["pct"], marker="o", mfc="white", mec=ps.VERMILLION, ms=4.2, ls="none", mew=1)
        b.text(i, o["hi"] + 3, f"n = {o['of']:,}", ha="center", fontsize=6.6, color=ps.INK2)
    b.plot([], [], "o", color=ps.BLUE, ms=4, label="Open during the event")
    b.plot([], [], "o", mfc="white", mec=ps.VERMILLION, ms=4, mew=1, label="Including archived before")
    b.legend(loc="lower left", fontsize=6.6, handlelength=1.0)
    b.set_xticks(range(len(groups)), [g[0] for g in groups])
    b.set_ylim(0, 75)
    b.set_xlim(-0.5, len(groups) - 0.5)
    b.set_ylabel("Active repositories (%)")
    title(b, "(b) Share active by creation date")
    fig.tight_layout(w_pad=2.0)
    ps.save(fig, "fig_population")


def fig_process() -> None:
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
    title(a, "(a) Commits over the event day")

    share = pd.read_csv(TABLES / "last_hour_share.csv").last_hour_share * 100
    b.hist(share, bins=np.arange(0, 105, 5), color=ps.BLUE, edgecolor="white", linewidth=0.5)
    top = b.get_ylim()[1] * 1.22
    b.set_ylim(0, top)
    for xv, text, h in ((20, "even (20%)", 0.98), (50, "majority (50%)", 0.88)):
        b.axvline(xv, color=ps.INK2, lw=0.8, ls=(0, (3, 2)))
        b.text(xv + 1.5, top * h, text, fontsize=6.8, color=ps.INK2, va="top")
    b.set_xlim(0, 100)
    b.set_xlabel("Share of a team's window commits in the last hour (%)")
    b.set_ylabel("Active repositories")
    title(b, "(b) Last-hour share per team")
    fig.tight_layout(w_pad=2.0)
    ps.save(fig, "fig_process")


def fig_traces() -> None:
    T = Q["traces"]
    SR = T["self_report"]
    fig, (a, b) = ps.new_figure(ps.FULL, 2.45, ncols=2, gridspec_kw={"width_ratios": [1, 1]})
    tools = (("codex", ps.BLUE, "Codex (required)", 0.14), ("claude", ps.ORANGE, "Claude Code", -0.14))

    def dots(ax, rows, get, xmax):
        y = np.arange(len(rows))[::-1].astype(float)
        for tool, colour, name, off in tools:
            for yi, (_, key) in zip(y, rows):
                d = get(tool, key)
                ax.errorbar(d["pct"], yi + off, xerr=[[d["pct"] - d["lo"]], [d["hi"] - d["pct"]]], fmt="o",
                            color=colour, ms=3.8, capsize=1.8, lw=0.85, label=name if yi == y[0] else None)
                ax.text(d["hi"] + 1.2, yi + off, f"{d['pct']:.1f}", va="center", fontsize=6.4, color=ps.INK2)
        ax.set_yticks(y, [r[0] for r in rows])
        ax.set_xlim(0, xmax)
        ax.set_ylim(-0.6, len(rows) - 0.4)
        ps.tidy(ax, grid_axis="x")
        ax.axhline(1.5, color=ps.GRID, lw=0.8)

    rows = [("Context file", "file"), ("Branch name", "branch"), ("Commit signature", "signature"),
            ("Author named after the tool", "name"), ("Any tool-specific trace", "specific"),
            ("Any trace incl. AGENTS.md", "any")]
    dots(a, rows, lambda t, k: T[t][k], 62)
    a.set_xlabel(f"Active repositories (%; n = {R['n']:,})")
    a.legend(loc="center right", bbox_to_anchor=(1.0, 0.56), fontsize=6.8, handlelength=1.2, borderaxespad=0.2)
    title(a, "(a) All active repositories")
    dots(b, rows, lambda t, k: SR[f"{t}_strict"][f"{k}_given_mention"], 105)
    b.set_xlabel(f"Repositories whose README names the tool (%; n = {SR['codex_strict']['mention']['n']} and "
                 f"{SR['claude_strict']['mention']['n']})")
    title(b, "(b) README names the tool")
    fig.tight_layout(w_pad=2.5)
    ps.save(fig, "fig_traces")


def fig_product() -> None:
    n = R["n"]
    rows = [("Engineering", "Test files", R["tests"]), ("Engineering", "Dockerfile", R["dockerfile"]),
            ("Engineering", "Docker Compose file", R["compose"]), ("Engineering", "CI workflow", R["ci"]),
            ("Engineering", "Deployment configuration", R["deploy_config"]),
            ("LLM", "Any LLM SDK or API", R["any_llm"]), ("LLM", "OpenAI SDK or API", R["llm_providers"]["OpenAI"]),
            ("README", "Run or setup instructions", R["readme_run_instructions"]), ("README", "Images", R["readme_images"]),
            ("README", "Mentions a coding agent", R["readme_mentions_agent"]),
            ("README", "Link to a deployed app", R["readme_deployed_link"])]
    fig, ax = ps.new_figure(ps.FULL, 2.55)
    ps.tidy(ax, grid_axis="x")
    ypos, y, last = [], 0, None
    for group, label, d in rows:
        if last is not None and group != last:
            y += 0.6
        ypos.append(y)
        ax.errorbar(d["pct"], -y, xerr=[[d["pct"] - d["lo"]], [d["hi"] - d["pct"]]], fmt="o", color=ps.BLUE, ms=4,
                    capsize=2, lw=0.9)
        ax.text(d["hi"] + 1.2, -y, f"{d['pct']:.1f}%  ({d['n']:,} of {d['of']:,})", va="center", fontsize=6.8, color=ps.INK2)
        last = group
        y += 1
    ax.set_yticks([-v for v in ypos], [r[1] for r in rows])
    ax.set_xlim(0, 115)
    ax.set_xticks(range(0, 101, 20))
    ax.set_xlabel("Share of repositories (%, 95% Wilson CI)")
    fig.tight_layout()
    ps.save(fig, "fig_product")


def fig_risk() -> None:
    fig, (a, b) = ps.new_figure(ps.FULL, 1.9, ncols=2, gridspec_kw={"width_ratios": [1.25, 1]})
    names = {"openaiapikey": "OpenAI API key", "curlauthheader": "Auth header in curl", "gcpapikey": "Google Cloud API key",
             "jwt": "JSON Web Token", "curlauthuser": "Credentials in curl", "telegrambotapitoken": "Telegram bot token",
             "stripeaccesstoken": "Stripe access token"}
    rules = K["provider_rules"]
    order = sorted(rules, key=lambda k: rules[k]["repos"])
    y = np.arange(len(order))
    final = [rules[k]["final"] for k in order]
    hist = [rules[k]["repos"] - rules[k]["final"] for k in order]
    a.barh(y, final, height=0.55, color=ps.VERMILLION, label="Still in the final version")
    a.barh(y, hist, left=final, height=0.55, color=ps.LIGHT, label="Only in history")
    for yi, k in zip(y, order):
        a.text(rules[k]["repos"] + 0.8, yi, str(rules[k]["repos"]), va="center", fontsize=7, color=ps.INK2)
    a.set_yticks(y, [names[k] for k in order])
    a.set_xlabel("Active repositories")
    a.set_xlim(0, max(r["repos"] for r in rules.values()) * 1.18)
    ps.tidy(a, grid_axis="x")
    a.legend(loc="lower right", fontsize=6.8, handlelength=1.0)
    title(a, "(a) Strings matching provider key formats")

    files = K["openai_files"]
    parts = [(".env.example", files["env_example"]), (".env", files["env"]), ("Other .env variants", files["env_other"]),
             ("Source or text files", files["source_or_text"])]
    yb = np.arange(len(parts))[::-1]
    b.barh(yb, [v for _, v in parts], height=0.55, color=ps.BLUE)
    for yi, (_, v) in zip(yb, parts):
        b.text(v + 0.5, yi, str(v), va="center", fontsize=7, color=ps.INK2)
    b.set_yticks(yb, [p[0] for p in parts])
    b.set_xlabel("OpenAI key findings (file, line, commit)")
    b.set_xlim(0, max(v for _, v in parts) * 1.2)
    ps.tidy(b, grid_axis="x")
    title(b, "(b) Files that held OpenAI key strings")
    fig.tight_layout(w_pad=2.0)
    ps.save(fig, "fig_risk")


if __name__ == "__main__":
    fig_population()
    fig_process()
    fig_traces()
    fig_product()
    fig_risk()
