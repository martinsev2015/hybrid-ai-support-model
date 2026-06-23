import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent

df = pd.read_csv(
    ROOT / "data/raw/dataset_to_label.csv",
    engine="python",
    on_bad_lines="skip"
)

df = df[df["text"].notna()]
df = df[df["text"].str.strip() != ""]

df = df[df["text"].str.len() > 20]

def is_truncated(text):
    text = text.strip()
    return (
        text.endswith("...") or
        text.endswith("..") or
        len(text.split()) < 5
    )

df = df[~df["text"].apply(is_truncated)]

df = df.drop_duplicates(subset=["text"])

df = df.reset_index(drop=True)

df.to_csv(ROOT / "data/processed/dataset_clean.csv", index=False)

print(f"Dataset limpo salvo com {len(df)} exemplos.")
