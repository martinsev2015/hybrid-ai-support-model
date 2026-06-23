import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).parent.parent

df = pd.read_json(ROOT / "data/results/results.json")

df = df.dropna(subset=["expected_action", "type"])

df = df[
    df["expected_action"].astype(str).str.strip() != ""
]

# =========================================================
# COMPUTE ACCURACY BY REQUEST TYPE
# =========================================================

request_types = ["clear", "ambiguous", "complex"]

hybrid_acc = []
llm_acc = []

for req_type in request_types:

    subset = df[df["type"].str.lower() == req_type]

    if len(subset) == 0:
        hybrid_acc.append(0)
        llm_acc.append(0)
        continue

    h_acc = accuracy_score(
        subset["expected_action"],
        subset["hybrid_pred"]
    )

    l_acc = accuracy_score(
        subset["expected_action"],
        subset["llm_pred"]
    )

    hybrid_acc.append(h_acc * 100)
    llm_acc.append(l_acc * 100)

# =========================================================
# CREATE BAR CHART
# =========================================================

x = range(len(request_types))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))

bars1 = ax.bar(
    [i - width/2 for i in x],
    hybrid_acc,
    width,
    label="Hybrid Model"
)

bars2 = ax.bar(
    [i + width/2 for i in x],
    llm_acc,
    width,
    label="LLM Baseline"
)

# =========================================================
# LABELS
# =========================================================

ax.set_ylabel("Accuracy (%)")
ax.set_xlabel("Request Type")
ax.set_title("Accuracy by Request Type")

ax.set_xticks(list(x))
ax.set_xticklabels([
    "Clear",
    "Ambiguous",
    "Complex"
])

ax.set_ylim(0, 110)

ax.legend()

# =========================================================
# VALUE LABELS WITH %
# =========================================================

for bar in bars1:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2,
        height + 1,
        f"{height:.2f}%",
        ha="center",
        va="bottom",
        fontsize=9
    )

for bar in bars2:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2,
        height + 1,
        f"{height:.2f}%",
        ha="center",
        va="bottom",
        fontsize=9
    )

# =========================================================
# SAVE FIGURE
# =========================================================

plt.tight_layout()

plt.savefig(
    ROOT / "figures/request_type_accuracy.png",
    dpi=300,
    bbox_inches="tight"
)

print("\nGraph saved:")
print(ROOT / "figures/request_type_accuracy.png")

plt.show()
