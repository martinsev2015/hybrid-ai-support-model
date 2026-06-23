import pandas as pd
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
input_file = ROOT / "data/raw/augmented_questions.json"
output_file = ROOT / "data/raw/dataset_to_label.csv"

(ROOT / "data/raw").mkdir(parents=True, exist_ok=True)

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

df = df[["text"]]

df["type"] = ""
df["expected_action"] = ""

df.to_csv(output_file, index=False, encoding="utf-8")

print(f"CSV criado com sucesso em: {output_file}")
