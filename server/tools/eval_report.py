import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from core.evaluator import compute_metrics

os.makedirs("exports", exist_ok=True)

metrics = compute_metrics()

# ── Colors from frontend palette.ts ──────────────────────────────────────────
C_GREEN       = "#1d5037"
C_GREEN_MID   = "#245f43"
C_GREEN_LIGHT = "#e8f0eb"
C_NAVY        = "#1a3d5c"
C_NAVY_MID    = "#1e4a70"
C_CREAM       = "#f2ece0"
C_SIDEBAR     = "#e8e2d3"
C_DIVIDER     = "#ddd8cc"
C_TEXT        = "#1a1a18"
C_GRAY        = "#6b6860"
C_MUTED       = "#a8a49c"

# ── Data ─────────────────────────────────────────────────────────────────────
pct_labels = ["Recall @ K", "Citation\nCoverage", "Answer\nGrounding"]
pct_values = [
    metrics["recall_at_k"],
    metrics["citation_coverage"],
    metrics["answer_grounding"],
]
pct_colors = [C_GREEN, C_NAVY, C_GREEN_MID]

latency     = metrics["avg_latency_ms"]
total       = metrics["total_queries"]

# ── Figure layout: wide left panel (3 bars) + narrow right panel (latency) ──
fig = plt.figure(figsize=(12, 5.5), facecolor=C_CREAM)
fig.subplots_adjust(left=0.07, right=0.97, top=0.82, bottom=0.14, wspace=0.35)

gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1], figure=fig)
ax1 = fig.add_subplot(gs[0])   # percentage metrics
ax2 = fig.add_subplot(gs[1])   # latency

# ── Shared style ─────────────────────────────────────────────────────────────
for ax in [ax1, ax2]:
    ax.set_facecolor(C_CREAM)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C_DIVIDER)
    ax.spines["bottom"].set_color(C_DIVIDER)
    ax.tick_params(colors=C_GRAY, labelsize=10)
    ax.yaxis.label.set_color(C_GRAY)

# ── Left panel: 3 percentage bars ────────────────────────────────────────────
bars1 = ax1.bar(pct_labels, pct_values, color=pct_colors,
                width=0.45, zorder=3, edgecolor="white", linewidth=0.8)

ax1.set_ylim(0, 118)          # extra headroom so 100% labels don't clip title
ax1.set_ylabel("Score (%)", fontsize=11, color=C_GRAY)
ax1.set_yticks([0, 20, 40, 60, 80, 100])
ax1.yaxis.grid(True, color=C_DIVIDER, linewidth=0.6, zorder=0)
ax1.set_axisbelow(True)
ax1.tick_params(axis="x", labelsize=11)

for bar, val in zip(bars1, pct_values):
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2.5,
        f"{val:.1f}%",
        ha="center", va="bottom",
        fontsize=13, fontweight="bold", color=C_TEXT
    )

# ── Right panel: latency bar ──────────────────────────────────────────────────
latency_bar_max = max(latency * 1.4, 500)
bars2 = ax2.bar(["Avg Latency"], [latency], color=C_NAVY_MID,
                width=0.45, zorder=3, edgecolor="white", linewidth=0.8)

ax2.set_ylim(0, latency_bar_max)
ax2.set_ylabel("Time (ms)", fontsize=11, color=C_GRAY)
ax2.yaxis.grid(True, color=C_DIVIDER, linewidth=0.6, zorder=0)
ax2.set_axisbelow(True)
ax2.tick_params(axis="x", labelsize=11)

ax2.text(
    bars2[0].get_x() + bars2[0].get_width() / 2,
    latency + latency_bar_max * 0.03,
    f"{latency} ms",
    ha="center", va="bottom",
    fontsize=13, fontweight="bold", color=C_TEXT
)

# ── Title ─────────────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.93,
    "RAG Evaluation Metrics",
    ha="center", va="center",
    fontsize=16, fontweight="bold", color=C_TEXT
)
fig.text(
    0.5, 0.885,
    f"Total Queries Evaluated: {total}",
    ha="center", va="center",
    fontsize=11, color=C_GRAY
)

# Thin green accent line under title
line = plt.Line2D([0.07, 0.97], [0.865, 0.865],
                  transform=fig.transFigure,
                  color=C_GREEN, linewidth=1.5)
fig.add_artist(line)

# ── Save ─────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "exports", "eval_report.png")
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=C_CREAM)
print(f"Report saved to exports/eval_report.png")
print(f"Metrics: {metrics}")
