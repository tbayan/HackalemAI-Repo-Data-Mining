"""One visual style for every figure in the paper.

- Okabe-Ito colours in a fixed order (validated for colour-vision deficiency on
  white with the dataviz validator; orange and sky blue sit below 3:1 contrast,
  so figures that use them label values directly).
- Liberation Serif, a TrueType font with Times metrics, so figure text matches the paper.
- Sizes follow the arxiv.sty text block (6.5 in wide); fonts 8-9 pt at print size.
- Vector PDF with embedded TrueType fonts (arXiv-safe), plus a PNG preview.
- No titles inside figures: captions live in LaTeX.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import ticker  # noqa: E402

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"

# Okabe-Ito, fixed order. Colour follows the entity, never its rank.
BLUE = "#0072B2"        # primary series
VERMILLION = "#D55E00"  # emphasis (e.g. empty repositories, the deadline)
GREEN = "#009E73"
ORANGE = "#E69F00"      # label directly: contrast 2.25:1 on white
PURPLE = "#CC79A7"
SKY = "#56B4E9"         # label directly: contrast 2.31:1 on white
SERIES = [BLUE, VERMILLION, GREEN, ORANGE, PURPLE, SKY]

GRAY = "#9A9A9A"        # context / de-emphasised data
LIGHT = "#D9D9D9"
TINT = "#EEF3F8"        # background band (e.g. the event window)
INK = "#1A1A1A"
INK2 = "#4D4D4D"
GRID = "#E5E5E5"

FULL = 6.5   # inches, \textwidth of arxiv.sty
HALF = 3.15  # two panels side by side with a small gap


def apply() -> None:
    plt.rcParams.update({
        "font.family": "Liberation Serif",  # TrueType, Times-metric; avoids CFF-in-Type42 embedding issues
        "mathtext.fontset": "stix",
        "font.size": 8.5,
        "axes.labelsize": 8.5,
        "axes.titlesize": 8.5,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.5,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "text.color": INK,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "lines.linewidth": 1.4,
        "legend.frameon": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    })


def new_figure(width: float = FULL, height: float = 2.4, ncols: int = 1, nrows: int = 1, **kwargs):
    apply()
    fig, axes = plt.subplots(nrows, ncols, figsize=(width, height), **kwargs)
    for ax in (axes.flat if hasattr(axes, "flat") else [axes]):
        tidy(ax)
    return fig, axes


def tidy(ax, grid_axis: str = "y") -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)


def thousands(ax, axis: str = "y") -> None:
    fmt = ticker.FuncFormatter(lambda v, _: f"{int(v):,}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def save(fig, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    pdf = FIG_DIR / f"{name}.pdf"
    fig.savefig(pdf)
    fig.savefig(FIG_DIR / f"{name}.png", dpi=300)
    plt.close(fig)
    print(f"saved {pdf.relative_to(FIG_DIR.parent)}")
    return pdf
