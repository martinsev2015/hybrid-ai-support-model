import pandas as pd
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

ROOT = Path(__file__).parent.parent

# =========================================================
# LOAD JSON RESULTS
# =========================================================

df = pd.read_json(ROOT / "data/results/results.json")

print(f"\nTotal instances loaded: {len(df)}")

# =========================================================
# REMOVE EMPTY LABELS
# =========================================================

df = df.dropna(subset=["expected_action"])
df = df[df["expected_action"].astype(str).str.strip() != ""]

print(f"Labeled instances: {len(df)}")

# =========================================================
# VALIDATE REQUIRED COLUMNS
# =========================================================

required_cols = ["hybrid_pred", "llm_pred"]

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Coluna '{col}' não encontrada no dataset.")

# =========================================================
# GROUND TRUTH
# =========================================================

y_true = df["expected_action"]

# =========================================================
# FUNCTION TO EVALUATE MODEL
# =========================================================

def evaluate_model(name, y_true, y_pred):

    print("\n====================================")
    print(f"RESULTS: {name}")
    print("====================================")

    acc = accuracy_score(y_true, y_pred)
    print(f"\nDecision Accuracy (DA): {acc:.4f}")

    print("\n--- Classification Report ---")
    print(classification_report(y_true, y_pred, digits=4))

    labels = ["respond", "clarify", "escalate"]

    cm = confusion_matrix(y_true, y_pred, labels=labels)

    cm_df = pd.DataFrame(
        cm,
        index=[f"true_{x}" for x in labels],
        columns=[f"pred_{x}" for x in labels]
    )

    print("\n--- Confusion Matrix ---")
    print(cm_df)

    if "type" in df.columns:
        print("\n--- Accuracy by Request Type ---")

        for request_type in df["type"].dropna().unique():

            subset = df[df["type"] == request_type]

            if len(subset) == 0:
                continue

            acc_type = accuracy_score(
                subset["expected_action"],
                subset[name]
            )

            print(f"{request_type}: {acc_type:.4f} ({len(subset)} samples)")

    clarify_subset = df[df["expected_action"] == "clarify"]

    if len(clarify_subset) > 0:
        ca = accuracy_score(
            clarify_subset["expected_action"],
            clarify_subset[name]
        )
        print(f"\nClarification Accuracy (CA): {ca:.4f}")

    escalate_subset = df[df["expected_action"] == "escalate"]

    if len(escalate_subset) > 0:
        ea = accuracy_score(
            escalate_subset["expected_action"],
            escalate_subset[name]
        )
        print(f"Escalation Accuracy (EA): {ea:.4f}")

    premature = df[
        (df[name] == "respond") &
        (df["expected_action"] != "respond")
    ]

    prr = len(premature) / len(df)

    print(f"Premature Response Rate (PRR): {prr:.4f}")

    return acc, prr


# =========================================================
# RUN EVALUATIONS
# =========================================================

acc_hybrid, prr_hybrid = evaluate_model(
    "hybrid_pred",
    y_true,
    df["hybrid_pred"]
)

acc_llm, prr_llm = evaluate_model(
    "llm_pred",
    y_true,
    df["llm_pred"]
)

# =========================================================
# COMPARISON SUMMARY
# =========================================================

print("\n====================================")
print("FINAL COMPARISON")
print("====================================")

print(f"\nHybrid Accuracy: {acc_hybrid:.4f}")
print(f"LLM Accuracy:    {acc_llm:.4f}")

print(f"\nHybrid PRR: {prr_hybrid:.4f}")
print(f"LLM PRR:    {prr_llm:.4f}")

# =========================================================
# SAVE ERROR ANALYSIS
# =========================================================

errors_hybrid = df[df["expected_action"] != df["hybrid_pred"]]
errors_llm = df[df["expected_action"] != df["llm_pred"]]

errors_hybrid.to_json(
    ROOT / "data/results/error_analysis_hybrid.json",
    orient="records",
    indent=4,
    force_ascii=False
)

errors_llm.to_json(
    ROOT / "data/results/error_analysis_llm.json",
    orient="records",
    indent=4,
    force_ascii=False
)

print("\nError analysis saved:")
print(ROOT / "data/results/error_analysis_hybrid.json")
print(ROOT / "data/results/error_analysis_llm.json")
