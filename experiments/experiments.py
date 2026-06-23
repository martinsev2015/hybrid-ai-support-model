import pandas as pd
import os
from pathlib import Path
from openai import OpenAI

from src.analise_mensagem import analisar_mensagem
from src.escalonamento import precisa_escalonar
from src.solicitacao_humano import cliente_pede_humano


# =============================================================
# CONFIG
# =============================================================
ROOT = Path(__file__).parent.parent
INPUT_FILE = ROOT / "data/results/results.json"
OUTPUT_FILE = ROOT / "data/results/results.json"
DATASET_LIMIT = 100

client = OpenAI()


# =============================================================
# LLM BASELINE
# =============================================================
def llm_baseline(texto):

    prompt = f"""
You are a technical support assistant.

Given the user message below, decide the best next action.

Actions:
- respond → if you can solve the problem
- clarify → if information is missing
- escalate → if the issue is complex, sensitive, or requires a human

Respond with ONLY one word:
respond
clarify
escalate

User message:
\"\"\"{texto}\"\"\"
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        pred = (
            response
            .choices[0]
            .message
            .content
            .strip()
            .lower()
        )

        if pred not in ["respond", "clarify", "escalate"]:
            return "respond"

        return pred

    except Exception as e:

        print("LLM ERROR:", e)

        return "respond"


# =============================================================
# HYBRID MODEL
# =============================================================
def avaliar_instancia(texto):

    texto = str(texto)

    request_human, _ = cliente_pede_humano(texto)

    if request_human:
        return "escalate"

    dados = analisar_mensagem(texto)

    should_escalate, _ = precisa_escalonar(
        dados,
        texto,
        historico_erros=0
    )

    if should_escalate:
        return "escalate"

    if dados.get("only_emoji"):
        return "clarify"

    if len(texto.split()) < 8:
        return "clarify"

    vague_terms = [
        "not working",
        "doesn't work",
        "help",
        "issue",
        "problem",
        "broken",
        "error",
        "bug",
        "something wrong"
    ]

    texto_lower = texto.lower()

    if (
        any(v in texto_lower for v in vague_terms)
        and len(texto.split()) < 20
    ):
        return "clarify"

    return "respond"


# =============================================================
# LOAD DATASET
# =============================================================
if not os.path.exists(INPUT_FILE):

    raise FileNotFoundError(
        f"{INPUT_FILE} não encontrado."
    )

df = pd.read_json(INPUT_FILE)

print(f"\nDataset carregado: {len(df)} linhas")


# =============================================================
# LIMPEZA
# =============================================================
df = df.dropna(subset=["text"])

df = df.drop_duplicates(subset=["text"])

df = df.head(DATASET_LIMIT)

print(f"Após limpeza: {len(df)} linhas")


# =============================================================
# GARANTIR COLUNAS
# =============================================================
required_columns = [
    "type",
    "expected_action",
    "hybrid_pred",
    "llm_pred"
]

for col in required_columns:

    if col not in df.columns:
        df[col] = None


# =============================================================
# RODAR SOMENTE PREDIÇÕES FALTANTES
# =============================================================

missing_hybrid = df["hybrid_pred"].isna()

print(
    f"\nRodando HYBRID para "
    f"{missing_hybrid.sum()} exemplos..."
)

df.loc[missing_hybrid, "hybrid_pred"] = (
    df.loc[missing_hybrid, "text"]
    .apply(avaliar_instancia)
)


missing_llm = df["llm_pred"].isna()

print(
    f"\nRodando LLM para "
    f"{missing_llm.sum()} exemplos..."
)

df.loc[missing_llm, "llm_pred"] = (
    df.loc[missing_llm, "text"]
    .apply(llm_baseline)
)


# =============================================================
# SALVAR JSON
# =============================================================
df.to_json(
    OUTPUT_FILE,
    orient="records",
    indent=4,
    force_ascii=False
)

print("\nArquivo atualizado com sucesso:")
print(OUTPUT_FILE)


# =============================================================
# DEBUG FINAL
# =============================================================
print("\n==============================")
print("Distribuição HYBRID")
print("==============================")

print(df["hybrid_pred"].value_counts())

print("\n==============================")
print("Distribuição LLM")
print("==============================")

print(df["llm_pred"].value_counts())


# =============================================================
# DATASET FINAL
# =============================================================
print("\n==============================")
print("TOTAL FINAL")
print("==============================")

print(f"Total de exemplos: {len(df)}")
