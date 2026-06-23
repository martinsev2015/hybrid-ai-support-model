import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
input_file = ROOT / "data/raw/dataset_high_interaction.json"
output_file = ROOT / "data/raw/questions.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

questions_list = []

for item in data:
    title = item.get("title", "")
    question_text = item.get("question", {}).get("text", "")

    questions_list.append({
        "title": title,
        "text": question_text
    })

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(questions_list, f, indent=4, ensure_ascii=False)

print(f"Arquivo '{output_file}' gerado com sucesso!")
