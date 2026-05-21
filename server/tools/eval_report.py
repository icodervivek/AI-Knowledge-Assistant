import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
from core.evaluator import compute_metrics

os.makedirs("exports", exist_ok=True)

metrics = compute_metrics()

labels = ["Recall@K", "Citation Coverage", "Answer Grounding"]
values = [
    metrics["recall_at_k"],
    metrics["citation_coverage"],
    metrics["answer_grounding"]
]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(labels, values, color=["#6366f1", "#8b5cf6", "#a78bfa"], width=0.5)

ax.set_ylim(0, 100)
ax.set_ylabel("Score (%)")
ax.set_title(f"RAG Evaluation Metrics  |  Total Queries: {metrics['total_queries']}")

for bar, val in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        f"{val}%",
        ha="center", fontsize=12, fontweight="bold"
    )

plt.tight_layout()
plt.savefig("exports/eval_report.png")
print("Report saved to exports/eval_report.png")
print(f"Metrics: {metrics}")
