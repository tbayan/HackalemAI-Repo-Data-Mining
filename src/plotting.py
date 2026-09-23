"""Shared chart styling for Instagram/Threads-ready square PNG exports."""
from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns

# Square format that renders cleanly as an Instagram/Threads post.
FIGSIZE_INCHES = (10.8, 10.8)
DPI = 100  # 10.8in * 100dpi = 1080px square

PALETTE = ["#6C63FF", "#FF6584", "#43D9AD", "#FFB347", "#4EA5D9", "#FF5C5C",
           "#8CD867", "#B983FF", "#FFD93D", "#3AAFA9"]

BG_COLOR = "#0F1220"
FG_COLOR = "#F5F5F7"
GRID_COLOR = "#33344A"


def new_square_figure(title: str, subtitle: str | None = None):
    """Create a styled 1080x1080 figure/axes pair, dark themed for social media."""
    plt.rcParams.update({
        "font.size": 16,
        "text.color": FG_COLOR,
        "axes.labelcolor": FG_COLOR,
        "xtick.color": FG_COLOR,
        "ytick.color": FG_COLOR,
    })
    fig, ax = plt.subplots(figsize=FIGSIZE_INCHES, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.suptitle(title, fontsize=26, fontweight="bold", color=FG_COLOR, y=0.97)
    if subtitle:
        ax.set_title(subtitle, fontsize=15, color="#B4B6C9", pad=16)
    return fig, ax


def save(fig, path: str) -> None:
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(path, dpi=DPI, facecolor=fig.get_facecolor())
    print(f"Saved chart -> {path}")
    plt.close(fig)
