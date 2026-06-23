from textblob import TextBlob
from langdetect import detect, LangDetectException
from detoxify import Detoxify

from src.emoji_utils import extrair_emojis, contem_apenas_emoji, EMOJI_DB

_detoxify_model = Detoxify("original")

CATEGORIAS_EMOJI = {
    "frustracao": ["face-angry", "face-negative", "face-concerned"],
    "confusao": ["face-skeptical", "face-neutral"],
    "positivo": ["face-smiling", "face-affection"]
}

def detectar_emoji_emocional(texto):
    emojis = extrair_emojis(texto)

    for emoji in emojis:
        meta = next((e for e in EMOJI_DB if e["character"] == emoji), None)
        if not meta:
            continue

        subgrupo = meta.get("subGroup", "")

        for emocao, grupos in CATEGORIAS_EMOJI.items():
            if subgrupo in grupos:
                return emocao

    return None


def analisar_mensagem(texto):

    emocao_emoji = detectar_emoji_emocional(texto)

    if contem_apenas_emoji(texto):
        return {
            "idioma": "desconhecido",
            "sentimento": "neutro",
            "sentimento_valor": 0.0,
            "toxicidade": {},
            "reclamacao": False,
            "maiusculas_excesso": False,
            "emocao_emoji": emocao_emoji,
            "apenas_emoji": True
        }

    try:
        idioma = detect(texto)
    except LangDetectException:
        idioma = "desconhecido"

    sentimento_valor = TextBlob(texto).sentiment.polarity

    if sentimento_valor > 0.4:
        sentimento = "muito positivo"
    elif sentimento_valor > 0.2:
        sentimento = "positivo"
    elif sentimento_valor < -0.4:
        sentimento = "muito negativo"
    elif sentimento_valor < -0.2:
        sentimento = "negativo"
    else:
        sentimento = "neutro"

    toxicidade = _detoxify_model.predict(texto)

    reclamacao = any(
        p in texto.lower()
        for p in ["erro", "problema", "falha", "não funciona"]
    )

    proporcao_maiusculas = sum(c.isupper() for c in texto) / max(len(texto), 1)
    maiusculas_excesso = proporcao_maiusculas > 0.3 and len(texto) > 10

    return {
        "idioma": idioma,
        "sentimento": sentimento,
        "sentimento_valor": sentimento_valor,
        "toxicidade": toxicidade,
        "reclamacao": reclamacao,
        "maiusculas_excesso": maiusculas_excesso,
        "emocao_emoji": emocao_emoji,
        "apenas_emoji": False
    }
