"""Phase 7: Bilingual (Kazakh / English) charts for the README and the Threads post.

Six 1080x1350 PNGs in one academic style. Every title and label is given in
both languages, and each page carries the author credit as its footer. Every
number drawn here is computed from data/ at run time and also written to
charts/bilingual/facts.json, so the README and the post can be checked
against it. The only hand-written inputs are the short case descriptions
(CASES) and seven case-label corrections (CASE_FIXES).

Inputs:
  data/hackalem_repos_analysis.csv  per-repo commits (all branches) + case_guess
  data/commit_timestamps.csv        commit times on the default branch
  data/repos.csv, data/commit_counts.csv, data/readmes/  for the cross-checks
"""
from __future__ import annotations

import json
from datetime import timedelta, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "charts" / "bilingual"

ASTANA = timezone(timedelta(hours=5))  # Kazakhstan is UTC+5 year-round
EVENT_START = pd.Timestamp("2026-09-23 13:00", tz=ASTANA)
EVENT_END = pd.Timestamp("2026-09-23 18:00", tz=ASTANA)

# --- style -------------------------------------------------------------------
W, H, DPI = 1080, 1350, 100
MARGIN = 0.055  # left/right page margin, figure fraction

BG = "#FFFFFF"
INK = "#1F1F1F"
INK2 = "#555555"
MUTED = "#8A8A8A"
GRID = "#E6E6E6"
AXIS = "#C8C8C8"
BLUE = "#4C72B0"  # same blue as plotting.PALETTE[0]
RED = "#C44E52"  # "empty" emphasis; pair validated for colour-blind separation
RAMP = ["#2B4C7E", "#4C72B0", "#7896C6", "#9DB4DA"]  # ordinal, validated
WINDOW_TINT = "#EEF2F8"

NBSP = "\u00a0"  # keeps "3 649" on one line when captions wrap
TOTAL_CHARTS = 6
AUTHOR = "Dr. Talgar Bayan"
REPO_URL = "github.com/tbayan/HackalemAI-Repo-Data-Mining"
DATA_LINE = "Дерек / Data: github.com/BAITC-Hacks — ашық реполар / public repos"

# --- the 12 official cases ----------------------------------------------------
# (code, sector_kk, sector_en, partner_kk, partner_en, bar_kk, bar_en, task_kk, task_en)
CASES = [
    ("01", "Энергетика", "Energy", "Самұрық-Қазына", "Samruk-Kazyna",
     "Энергетика · Самұрық-Қазына", "Energy · Samruk-Kazyna",
     "Ауа райы деректері арқылы жел электр станциясының қуатын болжайтын AI-агент",
     "Agentic AI that forecasts wind-farm power output from weather data"),
    ("02", "Қаржы", "Finance", "Freedom", "Freedom",
     "Қаржы · Freedom", "Finance · Freedom",
     "«Ақша графы»: транзакциялар желісінен ұйымдасқан топтың құрылымын табу (AML)",
     "“Money Graph”: rebuild an organised group from a transaction network (AML)"),
    ("03", "Басқару", "Management", "Halyk Bank (1-кейс)", "Halyk Bank (case 1)",
     "Басқару · Halyk Bank", "Management · Halyk Bank",
     "«Career Quest»: қызметкерге дағды мен даму жолын ұсынатын AI-бағыттаушы",
     "“Career Quest”: an AI guide linking employee skills to growth steps"),
    ("04", "Телекоммуникация", "Telecom", "Beeline", "Beeline",
     "Телекоммуникация · Beeline", "Telecom · Beeline",
     "Қай абонентке қандай тариф ұсынуды шешетін агент (таза ARPU өсімі)",
     "Agent deciding which subscribers get which tariff offer (net ARPU gain)"),
    ("05", "Логистика", "Logistics", "Электрокомплект (ekt.kz)", "Elektrokomplekt (ekt.kz)",
     "Логистика · ekt.kz", "Logistics · ekt.kz",
     "Қойманы толықтыру үшін жеткізушіге тапсырысты автоматты есептеу",
     "Automatic supplier orders to replenish stock, approved by a manager"),
    ("06", "Креативті индустрия", "Creative industries", "Firebird", "Firebird",
     "Креативті индустрия · Firebird", "Creative industries · Firebird",
     "«#79-lite»: іс-шараға 3 мердігерге дейін таңдап, себебін түсіндіру",
     "“#79-lite”: pick up to 3 event contractors and explain the choice"),
    ("07", "Білім беру", "Education", "AI Sana", "AI Sana",
     "Білім беру · AI Sana", "Education · AI Sana",
     "Challenge Hub: бизнес мәселесін студенттерге арналған тапсырмаға айналдыру",
     "Challenge Hub: turn a business problem into a task for student teams"),
    ("08", "Инновация", "Innovation", "Самұрық-Қазына", "Samruk-Kazyna",
     "Инновация · Самұрық-Қазына", "Innovation · Samruk-Kazyna",
     "«Хаттама»: жиналыс аудиосынан (қаз/орыс/аралас) хаттама мен тапсырмалар",
     "“Khattama”: minutes and action items from Kazakh/Russian/mixed meeting audio"),
    ("09", "Коммуникация", "Communications", "Halyk Bank (2-кейс)", "Halyk Bank (case 2)",
     "Коммуникация · Halyk Bank", "Communications · Halyk Bank",
     "«Voice Router»: сақтандыру колл-орталығында қоңырау бағыттайтын дауыстық AI",
     "“Voice Router”: a voice AI that routes calls in an insurance contact centre"),
    ("10", "Сауда", "Trade", "Электрокомплект (ekt.kz)", "Elektrokomplekt (ekt.kz)",
     "Сауда · ekt.kz", "Trade · ekt.kz",
     "ekt.kz каталогы бойынша AI-кеңесші: тауар, аналог, баға, қалдық, себет",
     "AI shopping assistant for ekt.kz: products, analogues, prices, stock, cart"),
    ("11", "Арнайы трек", "Special track", "Қазақтелеком", "Kazakhtelecom",
     "Оргқұрылым талдауы · Қазақтелеком", "Org-structure analysis · Kazakhtelecom",
     "Қайта ұйымдастыруға дейінгі және кейінгі құжаттарды салыстыратын агент",
     "Agent comparing org-structure documents before and after a reorganisation"),
    ("12", "Арнайы трек", "Special track", "Astana Innovations", "Astana Innovations",
     "«5 сағатқа әкім» · Astana Innovations", "“Akim for 5 hours” · Astana Innovations",
     "«5 сағатқа әкім»: бюджетті 5 бағыт пен 5 ауданға бөлетін қала симуляторы",
     "“Akim for 5 hours”: city simulator splitting a budget over 5 areas and districts"),
]

# Seven repos whose case_guess contradicts their own README (read by hand on
# 2026-09-24): repo -> (case code in the CSV, correct case code).
CASE_FIXES = {
    "hack-d68591cd-singularity": ("10", "11"),  # OrgDiff: before/after reorganisation docs
    "hack-e23c8ea3-qadam-ai": ("10", "07"),  # business problem -> task for student teams
    "hack-4f7b4401-techmind": ("10", "03"),  # Career Space: skills vs next grade
    "hack-f84ee748-chicks": ("10", "12"),  # akim-site/: budget + districts city game
    "hack-aa88eec9-irtida": ("09", "03"),  # Career Quest, Halyk Bank track
    "hack-8e42af59-rdm-code": ("05", "07"),  # Alem Practice, track "Образование"
    "hack-a791087a-winx": ("04", "12"),  # 100-unit budget over 5 Astana districts
}


# --- helpers ------------------------------------------------------------------
def n(value: float) -> str:
    """3649 -> '3 649': Kazakh/SI thousands separator, non-breaking."""
    return f"{int(value):,}".replace(",", NBSP)


def pct(part: float, whole: float, digits: int = 0) -> str:
    return f"{part / whole * 100:.{digits}f}%"


def setup_fonts() -> None:
    for family in ("Noto Sans", "DejaVu Sans"):
        try:
            font_manager.findfont(FontProperties(family=family), fallback_to_default=False)
        except ValueError:
            continue
        plt.rcParams["font.family"] = family
        plt.rcParams["axes.unicode_minus"] = False
        return
    raise RuntimeError("Need a font with Kazakh Cyrillic glyphs (Noto Sans or DejaVu Sans)")


class Page:
    """One 1080x1350 chart page: bilingual header, plot area, credit footer."""

    def __init__(self, index: int, title_kk: str, title_en: str):
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
        self.fig.patch.set_facecolor(BG)
        self.renderer = self.fig.canvas.get_renderer()
        self.index = index
        y = 1 - 0.034
        self.fig.text(MARGIN, y, "HackAlem AI · Астана / Astana · 23.09.2026",
                      fontsize=12.5, color=MUTED, va="center")
        self.fig.text(1 - MARGIN, y, f"{index}/{TOTAL_CHARTS}", fontsize=12.5,
                      color=MUTED, va="center", ha="right")
        y -= 0.022
        y = self.block(title_kk, y, size=24, color=INK, weight="bold")
        y = self.block(title_en, y - 0.004, size=17.5, color=INK2)
        self.header_bottom = y - 0.012
        self.fig.add_artist(plt.Line2D([MARGIN, 1 - MARGIN], [self.header_bottom] * 2,
                                       color=GRID, linewidth=1))

    def wrap(self, text: str, size: float, weight: str = "normal", width: float | None = None) -> str:
        max_px = (width or (1 - 2 * MARGIN)) * W
        prop = FontProperties(size=size, weight=weight)
        lines, cur = [], ""
        for word in text.split(" "):
            trial = f"{cur} {word}".strip()
            w_px = self.renderer.get_text_width_height_descent(trial, prop, ismath=False)[0]
            if w_px <= max_px or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
        return "\n".join(lines)

    def block(self, text: str, y_top: float, size: float, color: str, weight: str = "normal",
              x: float = MARGIN, width: float | None = None) -> float:
        """Draw wrapped text with its top at y_top; return the y just below it."""
        t = self.fig.text(x, y_top, self.wrap(text, size, weight, width), fontsize=size,
                          color=color, fontweight=weight, va="top", linespacing=1.3)
        return y_top - t.get_window_extent(self.renderer).height / H

    def block_up(self, text: str, y_bottom: float, size: float, color: str,
                 weight: str = "normal") -> float:
        """Draw wrapped text with its bottom at y_bottom; return the y just above it."""
        t = self.fig.text(MARGIN, y_bottom, self.wrap(text, size, weight), fontsize=size,
                          color=color, fontweight=weight, va="bottom", linespacing=1.3)
        return y_bottom + t.get_window_extent(self.renderer).height / H

    def footer(self, note: str | None = None) -> float:
        """Author credit, data line and optional note from the bottom; return their top y."""
        y = 0.022
        self.fig.text(MARGIN, y, f"Талдау / Analysis: {AUTHOR}", fontsize=12.5, color=INK2,
                      fontweight="bold", va="bottom")
        self.fig.text(1 - MARGIN, y, REPO_URL, fontsize=11, color=MUTED, ha="right",
                      va="bottom")
        y = self.block_up(DATA_LINE, y + 0.026, size=10.5, color=MUTED)
        if note:
            y = self.block_up(note, y + 0.004, size=10.5, color=MUTED)
        self.fig.add_artist(plt.Line2D([MARGIN, 1 - MARGIN], [y + 0.016] * 2,
                                       color=GRID, linewidth=1))
        return y + 0.016

    def axes(self, left: float, bottom: float, right: float, top: float):
        ax = self.fig.add_axes([left, bottom, right - left, top - bottom])
        ax.set_facecolor(BG)
        for side in ("top", "right", "left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=INK2, labelsize=13, length=0)
        return ax

    def save(self, name: str) -> None:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / name
        self.fig.savefig(path, dpi=DPI, facecolor=BG)
        plt.close(self.fig)
        print(f"Saved chart -> {path}")


def value_grid(ax, axis: str) -> None:
    ax.grid(axis=axis, color=GRID, linewidth=1)
    ax.set_axisbelow(True)


# --- data ---------------------------------------------------------------------
def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    repos = pd.read_csv(DATA_DIR / "hackalem_repos_analysis.csv")
    repos["case"] = repos["case_guess"].str.extract(r"^(\d{2})\b", expand=False)
    for repo, (old, new) in CASE_FIXES.items():
        row = repos["repo"] == repo
        assert repos.loc[row, "case"].eq(old).all() and row.any(), f"unexpected label for {repo}"
        repos.loc[row, "case"] = new

    ts = pd.read_csv(DATA_DIR / "commit_timestamps.csv", parse_dates=["committed_at"])
    ts["local"] = ts["committed_at"].dt.tz_convert(ASTANA)
    return repos, ts


def compute_facts(repos: pd.DataFrame, ts: pd.DataFrame) -> dict:
    total = len(repos)
    any_commit = int((repos["participant_commits"] > 0).sum())
    in_window = repos[repos["commits_13_18_local"] > 0]
    matched = in_window.dropna(subset=["case"])
    case_counts = matched["case"].value_counts()

    bins = [-1, 0, 5, 10, 20, 50, 100, float("inf")]
    labels = ["0", "1–5", "6–10", "11–20", "21–50", "51–100", "101+"]
    levels = (pd.cut(repos["participant_commits"], bins, labels=labels)
              .value_counts().reindex(labels).astype(int))

    window_ts = ts[(ts["local"] >= EVENT_START) & (ts["local"] < EVENT_END)]
    hourly = window_ts["local"].dt.hour.value_counts().sort_index()
    per_10min = window_ts.groupby(window_ts["local"].dt.floor("10min")).size()
    hours = in_window["hours_with_commits_of_5"].value_counts().reindex(range(1, 6), fill_value=0)

    # Cross-check the table's hour counts against our own main-branch timestamps.
    main_hours = window_ts.groupby("name")["local"].agg(lambda s: s.dt.hour.nunique())
    own_hours = in_window["repo"].map(main_hours).fillna(0)
    last_hour = window_ts[window_ts["local"].dt.hour == 17]["name"]

    meta = pd.read_csv(DATA_DIR / "repos.csv", parse_dates=["updated_at"])
    updated = meta["updated_at"].dt.tz_convert(ASTANA)
    archived_after = updated[(updated >= EVENT_END) & (updated < EVENT_END + pd.Timedelta("1h"))]
    team_names = repos["repo"].str.replace(r"^hack-[0-9a-f]{8}-", "", regex=True)
    main_counts = pd.read_csv(DATA_DIR / "commit_counts.csv")["commit_count"]

    return {
        "repos_total": total,
        "repos_zero_commits": total - any_commit,
        "repos_any_commit": any_commit,
        "repos_commit_in_window": len(in_window),
        "repos_commits_only_outside_window": any_commit - len(in_window),
        "repos_matched_to_case": len(matched),
        "repos_case_unclear": len(in_window) - len(matched),
        "case_counts": {c: int(case_counts.get(c, 0)) for c, *_ in CASES},
        "case_label_fixes": len(CASE_FIXES),
        "commit_levels_all_repos": {k: int(v) for k, v in levels.items()},
        "median_commits_repos_with_any": float(
            repos.loc[repos["participant_commits"] > 0, "participant_commits"].median()),
        "median_window_commits_active_repos": float(in_window["commits_13_18_local"].median()),
        "window_commits_all_branches": int(repos["commits_13_18_local"].sum()),
        "window_commits_main_branch": len(window_ts),
        "window_commits_main_by_hour": {f"{h:02d}:00": int(v) for h, v in hourly.items()},
        "peak_10min_start": per_10min.idxmax().strftime("%H:%M"),
        "peak_10min_commits": int(per_10min.max()),
        "hours_active_distribution": {int(k): int(v) for k, v in hours.items()},
        "repos_active_4plus_hours": int(hours.loc[4:].sum()),
        "repos_active_all_5_hours": int(hours.loc[5]),
        "repos_main_commit_in_last_hour": int(last_hour[last_hour.isin(in_window["repo"])].nunique()),
        "hours_table_matches_main_branch": int((own_hours == in_window["hours_with_commits_of_5"]).sum()),
        "repos_archived_18_to_19": len(archived_after),
        "archive_first": archived_after.min().strftime("%H:%M"),
        "archive_last": archived_after.max().strftime("%H:%M"),
        "team_names_on_multiple_repos": int((team_names.value_counts() > 1).sum()),
        "readmes_downloaded": len(list((DATA_DIR / "readmes").glob("*.md"))),
        "readmes_missing": len(pd.read_csv(DATA_DIR / "readme_failures.csv")),
        "repos_over_300_main_commits": int((main_counts > 300).sum()),
    }


# --- charts -------------------------------------------------------------------
def chart_funnel(f: dict) -> None:
    total = f["repos_total"]
    p = Page(1, f"{n(total)} репоның қаншасында код жазылды?",
             f"How many of the {total:,} team repos actually got code?")
    zero = f["repos_zero_commits"]
    cap_top = p.footer()
    stages = [
        (total, "Автоматты ашылған репо", "Repos auto-created at registration", None),
        (f["repos_any_commit"], "Кемінде 1 коммит бар", "At least one team commit",
         (zero, f"0 коммит / 0 commits: {n(zero)} ({pct(zero, total)})")),
        (f["repos_commit_in_window"], "Жарыс уақытында коммит (13:00–18:00)",
         "Committed during the 5-hour event (13:00–18:00)",
         (f["repos_commits_only_outside_window"],
          f"–{n(f['repos_commits_only_outside_window'])}: коммит тек басқа уақытта / "
          f"only at other times")),
        (f["repos_matched_to_case"], "12 кейстің біріне сәйкестендірілді",
         "Matched to one of the 12 cases",
         (f["repos_case_unclear"], f"–{f['repos_case_unclear']}: кейсі анық емес / case unclear")),
    ]
    top, bottom = p.header_bottom - 0.03, cap_top + 0.03
    row_h = (top - bottom) / len(stages)
    for i, (value, kk, en, rest) in enumerate(stages):
        y_row = top - i * row_h
        y = p.block(kk, y_row, size=17, color=INK, weight="bold")
        y = p.block(en, y - 0.002, size=13.5, color=INK2)
        bar_h = 0.026
        bar_y = y - 0.012 - bar_h
        full_w = 1 - 2 * MARGIN - 0.2
        w = full_w * value / total
        p.fig.add_artist(plt.Rectangle((MARGIN, bar_y), w, bar_h, color=RAMP[i], linewidth=0))
        if rest:
            rest_value, rest_label = rest
            if i == 1:  # the big "empty" block, drawn as its own pale segment
                p.fig.add_artist(plt.Rectangle((MARGIN + w + 0.003, bar_y), full_w - w - 0.003,
                                               bar_h, color="#F3D9DA", linewidth=0))
                p.fig.text(MARGIN + w + 0.012, bar_y + bar_h / 2, rest_label, fontsize=13,
                           color="#7D2A2D", va="center")
            else:
                p.fig.text(MARGIN + w + 0.012, bar_y + bar_h / 2, rest_label, fontsize=12,
                           color=MUTED, va="center")
        p.fig.text(MARGIN + full_w + 0.02, bar_y + bar_h / 2,
                   f"{n(value)}  ·  {pct(value, total)}", fontsize=16, color=INK,
                   fontweight="bold", va="center")
    p.save("01_funnel.png")


def chart_commit_levels(f: dict) -> None:
    total = f["repos_total"]
    levels = f["commit_levels_all_repos"]
    p = Page(2, "Әр репоға қанша коммит түсті?", "How many commits did each repo get?")
    cap_top = p.footer(note="Коммиттер барлық тармақтан, автоматты алғашқы коммитсіз / "
                         "Team commits on all branches, excluding the auto-created first commit")
    ax = p.axes(0.13, cap_top + 0.11, 1 - MARGIN, p.header_bottom - 0.06)
    keys = list(levels.keys())
    vals = [levels[k] for k in keys]
    ax.bar(range(len(keys)), vals, width=0.5, color=[RED] + [BLUE] * (len(keys) - 1),
           linewidth=0)
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.015, f"{n(v)}\n{pct(v, total)}", ha="center",
                va="bottom", fontsize=13.5, color=INK, linespacing=1.15)
    ax.set_xticks(range(len(keys)), keys)
    ax.tick_params(axis="x", labelsize=15, colors=INK, pad=8)
    ax.set_ylim(0, max(vals) * 1.15)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: n(v)))
    value_grid(ax, "y")
    ax.axhline(0, color=AXIS, linewidth=1)
    ax.set_ylabel("Репо саны / Number of repos", fontsize=14, color=INK2, labelpad=10)
    ax.set_xlabel("Командалық коммит саны / Number of team commits", fontsize=14,
                  color=INK2, labelpad=12)
    p.save("02_commit_levels.png")


def chart_timeline(f: dict, ts: pd.DataFrame) -> None:
    p = Page(3, "23 қыркүйек: коммиттер уақыт бойынша",
             "23 September: team commits over the day")
    by_hour = f["window_commits_main_by_hour"]
    cap_top = p.footer(note="main тармағындағы коммит уақыты, 10 минуттық аралық / "
                         "Commit times on the main branch, 10-minute bins")
    day = ts[(ts["local"] >= pd.Timestamp("2026-09-23 11:00", tz=ASTANA))
             & (ts["local"] < pd.Timestamp("2026-09-23 19:00", tz=ASTANA))]
    bins = pd.date_range("2026-09-23 11:00", "2026-09-23 18:50", freq="10min", tz=ASTANA)
    series = day.groupby(day["local"].dt.floor("10min")).size().reindex(bins, fill_value=0)
    x_mid = [(t - bins[0]).total_seconds() / 3600 + 11 + 1 / 12 for t in series.index]

    ax = p.axes(0.13, cap_top + 0.15, 1 - MARGIN, p.header_bottom - 0.03)
    ax.axvspan(13, 18, color=WINDOW_TINT, linewidth=0)
    ax.fill_between(x_mid, series.values, color=BLUE, alpha=0.12, linewidth=0)
    ax.plot(x_mid, series.values, color=BLUE, linewidth=2.2, solid_joinstyle="round")
    top = series.max() * 1.3
    ax.axvline(13, color=MUTED, linewidth=1)
    ax.axvline(18, color=MUTED, linewidth=1)
    ax.text(13.08, top * 0.98, "13:00 старт / start", ha="left", va="top", fontsize=13,
            color=INK2)
    ax.text(18.08, top * 0.98, "18:00\nдедлайн\ndeadline", ha="left", va="top", fontsize=13,
            color=INK2)
    peak_i = int(series.values.argmax())
    peak_end = (series.index[peak_i] + pd.Timedelta("10min")).strftime("%H:%M")
    ax.scatter([x_mid[peak_i]], [series.values[peak_i]], s=70, color=BLUE, zorder=3,
               edgecolor=BG, linewidth=2)
    ax.annotate(f"{n(series.values[peak_i])} коммит / commits\n{f['peak_10min_start']}–{peak_end}",
                (x_mid[peak_i], series.values[peak_i]), xytext=(-10, 8),
                textcoords="offset points", ha="right", va="bottom", fontsize=13, color=INK)
    # Hourly totals as a row under the time axis, one number per event hour;
    # offset in points so the row keeps its place whatever the axes height.
    row = {"xycoords": ("data", "axes fraction"), "xytext": (0, -36),
           "textcoords": "offset points", "va": "top"}
    ax.annotate("Сағатына / Per hour:", (12.9, 0), ha="right", fontsize=12.5, color=INK2, **row)
    for hour in range(13, 18):
        ax.annotate(n(by_hour[f"{hour:02d}:00"]), (hour + 0.5, 0), ha="center", fontsize=13.5,
                    color=INK, fontweight="bold", **row)
    ax.set_ylim(0, top)
    ax.set_xlim(11, 19)
    ax.set_xticks(range(11, 20), [f"{h}:00" for h in range(11, 20)])
    ax.tick_params(axis="x", labelsize=13, pad=8)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: n(v)))
    value_grid(ax, "y")
    ax.axhline(0, color=AXIS, linewidth=1)
    ax.set_ylabel("10 минуттағы коммит / Commits per 10 min", fontsize=14, color=INK2,
                  labelpad=10)
    ax.set_xlabel("Астана уақыты (UTC+5) / Astana time (UTC+5)", fontsize=13.5, color=INK2,
                  labelpad=40)
    p.save("03_timeline.png")


def chart_hours_active(f: dict) -> None:
    dist = f["hours_active_distribution"]
    active = f["repos_commit_in_window"]
    p = Page(4, "Командалар 5 сағаттың қаншасында коммит жасады?",
             "In how many of the 5 event hours did teams commit?")
    cap_top = p.footer(note="Сағаттар: 13, 14, 15, 16, 17 · барлық тармақ / Hours 13–17 · all branches")
    ax = p.axes(0.13, cap_top + 0.12, 1 - MARGIN, p.header_bottom - 0.06)
    keys = list(range(1, 6))
    vals = [dist[k] for k in keys]
    ax.bar(keys, vals, width=0.5, color=BLUE, linewidth=0)
    for k, v in zip(keys, vals):
        ax.text(k, v + max(vals) * 0.015, f"{n(v)}\n{pct(v, active)}", ha="center",
                va="bottom", fontsize=14, color=INK, linespacing=1.15)
    ax.set_xticks(keys, [f"{k} сағат\n{k} hour{'s' if k > 1 else ''}" for k in keys])
    ax.tick_params(axis="x", labelsize=14, colors=INK, pad=8)
    ax.set_ylim(0, max(vals) * 1.18)
    value_grid(ax, "y")
    ax.axhline(0, color=AXIS, linewidth=1)
    ax.set_ylabel("Репо саны / Number of repos", fontsize=14, color=INK2, labelpad=10)
    ax.set_xlabel("Коммит болған сағат саны / Hours with at least one commit", fontsize=14,
                  color=INK2, labelpad=12)
    p.save("04_hours_active.png")


def chart_cases_explained(f: dict) -> None:
    p = Page(5, "12 кейс: командалар не құрастырды?", "The 12 cases: what did teams build?")
    cap_top = p.footer(note="Сипаттамалар командалардың README-лері бойынша қысқартылды / "
                         "Short descriptions summarised from team READMEs")
    top, bottom = p.header_bottom - 0.016, cap_top + 0.004
    row_h = (top - bottom) / len(CASES)
    badge_w = 0.05
    text_x = MARGIN + badge_w + 0.02
    counts = f["case_counts"]
    bold = FontProperties(size=14, weight="bold")
    for i, (code, s_kk, s_en, p_kk, p_en, _, _, t_kk, t_en) in enumerate(CASES):
        y = top - i * row_h
        p.fig.add_artist(FancyBboxPatch((MARGIN, y - 0.03), badge_w, 0.027,
                                        boxstyle="round,pad=0,rounding_size=0.006",
                                        color=BLUE, linewidth=0))
        p.fig.text(MARGIN + badge_w / 2, y - 0.0165, code, fontsize=14, color=BG,
                   fontweight="bold", ha="center", va="center")
        sector = f"{s_kk} / {s_en}"
        partner = p_kk if p_kk == p_en else f"{p_kk} / {p_en}"
        if "ekt.kz" in p_en:
            partner = "ekt.kz (Электрокомплект)"
        elif p_en.startswith("Halyk Bank"):
            case_no = p_en[-2]
            partner = f"Halyk Bank · {case_no}-кейс / case {case_no}"
        p.fig.text(text_x, y, sector, fontsize=14, color=INK, fontweight="bold", va="top")
        sector_w = p.renderer.get_text_width_height_descent(sector, bold, ismath=False)[0] / W
        p.fig.text(text_x + sector_w, y - 0.001, f"  ·  {partner}", fontsize=13, color=INK2,
                   va="top")
        p.fig.text(1 - MARGIN, y - 0.001, f"{counts[code]} команда / teams", fontsize=11.5,
                   color=MUTED, ha="right", va="top")
        p.fig.text(text_x, y - 0.0215, t_kk, fontsize=13, color=INK, va="top")
        p.fig.text(text_x, y - 0.0405, t_en, fontsize=12, color=INK2, va="top")
    p.save("05_cases_explained.png")


def chart_cases_ranked(f: dict) -> None:
    counts = f["case_counts"]
    unclear = f["repos_case_unclear"]
    p = Page(6, "Қай кейсті көбірек таңдады?", "Which cases did teams choose?")
    ranked = sorted(CASES, key=lambda c: counts[c[0]], reverse=True)
    cap_top = p.footer(note=f"Тағы {unclear} репоның кейсі анық емес / {unclear} more repos: case unclear · "
                         f"{f['case_label_fixes']} белгі қолмен түзетілді / labels corrected by hand")
    top, bottom = p.header_bottom - 0.02, cap_top + 0.015
    row_h = (top - bottom) / len(ranked)
    bar_x0, bar_x1 = 0.53, 1 - MARGIN - 0.07
    max_v = max(counts.values())
    for i, (code, *_rest) in enumerate(ranked):
        bar_kk, bar_en = _rest[4], _rest[5]
        y_mid = top - (i + 0.5) * row_h
        p.fig.text(MARGIN, y_mid + 0.004, f"{code}  {bar_kk}", fontsize=13.5, color=INK,
                   va="bottom")
        p.fig.text(MARGIN, y_mid + 0.001, f"      {bar_en}", fontsize=11.5, color=INK2,
                   va="top")
        w = (bar_x1 - bar_x0) * counts[code] / max_v
        p.fig.add_artist(plt.Rectangle((bar_x0, y_mid - 0.009), w, 0.018, color=BLUE,
                                       linewidth=0))
        p.fig.text(bar_x0 + w + 0.01, y_mid, str(counts[code]), fontsize=14, color=INK,
                   fontweight="bold", va="center")
    p.fig.add_artist(plt.Line2D([bar_x0, bar_x0], [bottom, top], color=AXIS, linewidth=1))
    p.save("06_cases_ranked.png")


def main() -> None:
    setup_fonts()
    repos, ts = load()
    facts = compute_facts(repos, ts)
    chart_funnel(facts)
    chart_commit_levels(facts)
    chart_timeline(facts, ts)
    chart_hours_active(facts)
    chart_cases_explained(facts)
    chart_cases_ranked(facts)
    (OUT_DIR / "facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    print(json.dumps(facts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
