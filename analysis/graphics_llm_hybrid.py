import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ==========================================
# UPDATED DATA (100 INSTANCES)
# ==========================================

metrics = {
    "Metric": [
        "Decision Accuracy",
        "Clarification Accuracy",
        "Escalation Accuracy",
        "PRR"
    ],
    "Hybrid": [
        61.0,
        45.45,
        54.55,
        26.0
    ],
    "LLM": [
        62.0,
        96.97,
        39.39,
        3.0
    ]
}

df = pd.DataFrame(metrics)

# ==========================================
# PLOT
# ==========================================

x = range(len(df))

width = 0.35

fig, ax = plt.subplots(figsize=(10, 5))

bars1 = ax.bar(
    [i - width/2 for i in x],
    df["Hybrid"],
    width,
    label="Hybrid"
)

bars2 = ax.bar(
    [i + width/2 for i in x],
    df["LLM"],
    width,
    label="LLM"
)

# ==========================================
# VALUE LABELS WITH %
# ==========================================

for bar in bars1:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2,
        height + 1,
        f"{height:.1f}%",
        ha='center',
        va='bottom',
        fontsize=9
    )

for bar in bars2:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2,
        height + 1,
        f"{height:.1f}%",
        ha='center',
        va='bottom',
        fontsize=9
    )

# ==========================================
# LABELS
# ==========================================

ax.set_ylabel("Percentage (%)")
ax.set_title("Hybrid Model vs LLM Baseline")
ax.set_xticks(list(x))
ax.set_xticklabels(df["Metric"], rotation=10)

ax.set_ylim(0, 110)

ax.legend()

# ==========================================
# SAVE
# ==========================================

plt.tight_layout()

plt.savefig(
    ROOT / "figures/comparison_metrics.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
