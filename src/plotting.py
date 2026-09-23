"""Shared chart styling for Instagram/Threads-ready square PNG exports.

Light, academic/professional theme: white background, muted "seaborn deep"
style palette, charcoal text — legible and print-friendly rather than
neon/dark.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns

# Square format that renders cleanly as an Instagram/Threads post.
FIGSIZE_INCHES = (10.8, 10.8)
DPI = 100  # 10.8in * 100dpi = 1080px square

PALETTE = ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD",
           "#937860", "#DA8BC3", "#8C8C8C", "#B0B0B0"]

BG_COLOR = "#FFFFFF"
FG_COLOR = "#222222"
GRID_COLOR = "#DDDDDD"
SUBTITLE_COLOR = "#5A5A5A"


def new_square_figure(title: str, subtitle: str | None = None):
    """Create a styled 1080x1080 figure/axes pair, light themed for print/social."""
    plt.rcParams.update({
        "font.size": 16,
        "font.family": "sans-serif",
        "text.color": FG_COLOR,
        "axes.labelcolor": FG_COLOR,
        "xtick.color": FG_COLOR,
        "ytick.color": FG_COLOR,
    })
    fig, ax = plt.subplots(figsize=FIGSIZE_INCHES, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, alpha=0.9)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.suptitle(title, fontsize=26, fontweight="bold", color=FG_COLOR, y=0.97)
    if subtitle:
        ax.set_title(subtitle, fontsize=15, color=SUBTITLE_COLOR, pad=16)
    return fig, ax


def save(fig, path: str) -> None:
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(path, dpi=DPI, facecolor=fig.get_facecolor())
    print(f"Saved chart -> {path}")
    plt.close(fig)
