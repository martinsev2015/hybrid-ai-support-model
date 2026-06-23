from openai import OpenAI
import json
import src.config  # garante que load_dotenv() foi chamado antes de criar o cliente

client = OpenAI()

def cliente_pede_humano(mensagem):
    texto = mensagem.lower()

    palavras_chave = [
        "human",
        "agent",
        "representative",
        "person",
        "talk to someone",
        "talk to a person",
        "speak to someone",
        "speak to a human",
        "i want a human",
        "i want to talk to a human",
        "connect me to an agent"
    ]

    for palavra in palavras_chave:
        if palavra in texto:
            return True, f"Explicit request detected: '{palavra}'"

    return False, None