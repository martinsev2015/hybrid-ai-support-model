import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent
input_file = ROOT / "data/raw/questions.json"
output_file = ROOT / "data/raw/augmented_questions.json"

PREFIXES = [
    "Hi, I need help.",
    "Can someone help me?",
    "I'm having an issue.",
    "Please help.",
    "This is really frustrating.",
    "I don't understand what's happening.",
]

SUFFIXES = [
    "Any suggestions?",
    "What should I do?",
    "How can I fix this?",
    "Is there a solution?",
    "This started recently.",
    ""
]

SHORT_VERSIONS = [
    "It is not working",
    "This is broken",
    "Something is wrong",
    "Why is this happening?",
    "Need help with this"
]

def generate_variations(title, text):
    variations = []

    variations.append({
        "title": title,
        "text": f"{random.choice(PREFIXES)} {text[:150]} {random.choice(SUFFIXES)}"
    })

    variations.append({
        "title": title,
        "text": random.choice(SHORT_VERSIONS)
    })

    variations.append({
        "title": title,
        "text": f"This is very frustrating. {text[:120]} It keeps happening and I need urgent help."
    })

    variations.append({
        "title": title,
        "text": f"{title}. {text[:100]}"
    })

    return variations


with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

augmented_data = []

for item in data:
    title = item.get("title", "")
    text = item.get("text", "")

    augmented_data.append({
        "title": title,
        "text": text
    })

    variations = generate_variations(title, text)
    augmented_data.extend(variations)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(augmented_data, f, indent=4, ensure_ascii=False)

print(f"Dataset aumentado salvo em: {output_file}")
print(f"Total de exemplos: {len(augmented_data)}")
