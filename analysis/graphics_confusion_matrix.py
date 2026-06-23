import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import confusion_matrix

ROOT = Path(__file__).parent.parent

df = pd.read_json(ROOT / "data/results/results.json")

df = df.dropna(subset=["expected_action"])

df = df[
    df["expected_action"].astype(str).str.strip() != ""
]

# =========================================================
# LABELS
# =========================================================

labels = ["respond", "clarify", "escalate"]

# =========================================================
# HYBRID CONFUSION MATRIX
# =========================================================

cm_hybrid = confusion_matrix(
    df["expected_action"],
    df["hybrid_pred"],
    labels=labels
)

# =========================================================
# LLM CONFUSION MATRIX
# =========================================================

cm_llm = confusion_matrix(
    df["expected_action"],
    df["llm_pred"],
    labels=labels
)

# =========================================================
# GLOBAL FONT CONFIG
# =========================================================

plt.rcParams.update({
    "font.size": 16,
    "axes.titlesize": 22,
    "axes.labelsize": 18,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16
})

# =========================================================
# CREATE FIGURE (VERTICAL LAYOUT)
# =========================================================

fig, axes = plt.subplots(2, 1, figsize=(10, 16))

# =========================================================
# HYBRID MATRIX
# =========================================================

ax = axes[0]

im1 = ax.imshow(cm_hybrid, cmap="Blues")

ax.set_title("Hybrid Model", pad=15)

ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))

ax.set_xticklabels(labels)
ax.set_yticklabels(labels)

ax.set_xlabel("Predicted", labelpad=10)
ax.set_ylabel("True", labelpad=10)

for i in range(len(labels)):
    for j in range(len(labels)):
        ax.text(
            j,
            i,
            str(cm_hybrid[i, j]),
            ha="center",
            va="center",
            fontsize=18,
            color="black",
            fontweight="bold"
        )

cbar1 = fig.colorbar(im1, ax=ax, fraction=0.046)
cbar1.ax.tick_params(labelsize=14)

# =========================================================
# LLM MATRIX
# =========================================================

ax = axes[1]

im2 = ax.imshow(cm_llm, cmap="Blues")

ax.set_title("LLM Baseline", pad=15)

ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))

ax.set_xticklabels(labels)
ax.set_yticklabels(labels)

ax.set_xlabel("Predicted", labelpad=10)
ax.set_ylabel("True", labelpad=10)

for i in range(len(labels)):
    for j in range(len(labels)):
        ax.text(
            j,
            i,
            str(cm_llm[i, j]),
            ha="center",
            va="center",
            fontsize=18,
            color="black",
            fontweight="bold"
        )

cbar2 = fig.colorbar(im2, ax=ax, fraction=0.046)
cbar2.ax.tick_params(labelsize=14)

# =========================================================
# ADJUST LAYOUT
# =========================================================

plt.tight_layout(pad=4.0)

# =========================================================
# SAVE FIGURE
# =========================================================

output_path = ROOT / "figures/confusion_matrix_comparison.png"

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print("\nConfusion matrix saved:")
print(output_path)

# =========================================================
# PRINT MATRICES
# =========================================================

print("\nHybrid Confusion Matrix:")
print(pd.DataFrame(
    cm_hybrid,
    index=[f"true_{l}" for l in labels],
    columns=[f"pred_{l}" for l in labels]
))

print("\nLLM Confusion Matrix:")
print(pd.DataFrame(
    cm_llm,
    index=[f"true_{l}" for l in labels],
    columns=[f"pred_{l}" for l in labels]
))

plt.show()
