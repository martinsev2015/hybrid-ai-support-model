import os
import re
import requests
from dotenv import load_dotenv
from openai import OpenAI
from detoxify import Detoxify
from textblob import TextBlob
from langdetect import detect, LangDetectException

# ============================================================
# CARREGAMENTO DE VARIÁVEIS
# ============================================================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
EMOJI_API_KEY = os.getenv("EMOJI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("Defina OPENAI_API_KEY no .env")
if not OPENAI_MODEL:
    raise RuntimeError("Defina OPENAI_MODEL no .env")
if not EMOJI_API_KEY:
    raise RuntimeError("Defina EMOJI_API_KEY no .env")

client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================================
# CARREGAR BASE DE EMOJIS (UNICODE)
# ============================================================
def carregar_emojis():
    url = f"https://emoji-api.com/emojis?access_key={EMOJI_API_KEY}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

EMOJI_DB = carregar_emojis()

# ============================================================
# PADRÃO DE EXTRAÇÃO DE EMOJIS
# ============================================================
EMOJI_PATTERN = re.compile(
    "[\U0001F300-\U0001FAFF\u2600-\u27BF]"
)

def extrair_emojis(texto):
    return EMOJI_PATTERN.findall(texto)

# ============================================================
# UTIL: detectar apenas emoji
# ============================================================
def contem_apenas_emoji(texto):
    texto = texto.strip()
    if not texto:
        return True

    texto_sem_emoji = re.sub(
        EMOJI_PATTERN,
        "",
        texto
    )

    return texto_sem_emoji.strip() == ""

# ============================================================
# FUNÇÃO: ANALISAR MENSAGEM
# ============================================================
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

    # -------------------------
    # Caso especial: só emoji
    # -------------------------
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

    # -------------------------
    # Idioma
    # -------------------------
    try:
        idioma = detect(texto)
    except LangDetectException:
        idioma = "desconhecido"

    # -------------------------
    # Sentimento (TextBlob)
    # -------------------------
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

    # -------------------------
    # Tradução (para toxicidade)
    # -------------------------
    try:
        texto_en = str(TextBlob(texto).translate(to="en"))
    except Exception:
        texto_en = texto

    toxicidade = Detoxify("original").predict(texto_en)

    # -------------------------
    # Reclamação explícita
    # -------------------------
    reclamacao = any(
        p in texto.lower()
        for p in ["erro", "problema", "falha", "não funciona"]
    )

    # -------------------------
    # Uso excessivo de maiúsculas
    # -------------------------
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

# ============================================================
# FUNÇÃO: GERAR RESPOSTA
# ============================================================
def gerar_resposta(dados, mensagem):

    toxic = dados.get("toxicidade", {}).get("toxicity", 0)
    insult = dados.get("toxicidade", {}).get("insult", 0)
    anger = dados.get("toxicidade", {}).get("anger", 0)

    emocao_emoji = dados.get("emocao_emoji")
    apenas_emoji = dados.get("apenas_emoji", False)

    # -------------------------
    # Escalonamento imediato
    # -------------------------
    if toxic > 0.6 or insult > 0.5 or anger > 0.5:
        return (
            "Percebo que esta situação está te incomodando. "
            "Vou encaminhar seu caso a um atendente humano."
        )

    if apenas_emoji and emocao_emoji == "frustracao":
        return (
            "Percebo que você está frustrado. "
            "Vou encaminhar seu atendimento para um especialista humano."
        )

    # -------------------------
    # Construção do prompt
    # -------------------------
    if dados.get("sentimento") in ["negativo", "muito negativo"]:
        prompt = (
            "O cliente demonstra insatisfação. "
            "Atue como especialista em Google Chrome, "
            "responda de forma empática e objetiva. "
            f"Mensagem do cliente: {mensagem}"
        )

    elif dados.get("reclamacao"):
        prompt = (
            "O cliente relatou um problema no Google Chrome. "
            "Solicite informações adicionais de forma clara e educada. "
            f"Mensagem do cliente: {mensagem}"
        )

    elif emocao_emoji == "confusao":
        prompt = (
            "O cliente demonstra confusão. "
            "Explique de forma simples e didática, "
            "como especialista em Google Chrome. "
            f"Mensagem do cliente: {mensagem}"
        )

    else:
        prompt = (
            "Atenda normalmente como especialista em Google Chrome. "
            f"Mensagem do cliente: {mensagem}"
        )

    resposta = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return resposta.choices[0].message.content.strip()

# ============================================================
# FUNÇÃO: CRITÉRIOS DE ESCALONAMENTO
# ============================================================
def precisa_escalonar(dados, mensagem, historico_erros):

    criterios = []
    texto = mensagem.lower()
    toxicidade = dados.get("toxicidade", {})

    emocao_emoji = dados.get("emocao_emoji")
    apenas_emoji = dados.get("apenas_emoji", False)

    if emocao_emoji == "frustracao":
        criterios.append("emoji de frustração detectado")

    if apenas_emoji and emocao_emoji:
        criterios.append("mensagem apenas emocional (emoji)")

    if toxicidade.get("toxicity", 0) > 0.6:
        criterios.append("mensagem tóxica")
    if toxicidade.get("insult", 0) > 0.5:
        criterios.append("insultos detectados")
    if toxicidade.get("anger", 0) > 0.5:
        criterios.append("raiva detectada")

    if dados.get("maiusculas_excesso"):
        criterios.append("uso excessivo de maiúsculas")

    if "!!!" in mensagem or "???" in mensagem or "!?!?" in mensagem:
        criterios.append("pontuação intensa")

    termos_complexos = [
        "dump", "crash", "log", "debug",
        "código", "customização", "transport"
    ]
    if any(t in texto for t in termos_complexos):
        criterios.append("termo técnico complexo")

    termos_sensiveis = ["senha", "token", "cpf", "chave de acesso"]
    if any(t in texto for t in termos_sensiveis):
        criterios.append("dados sensíveis")

    termos_risco = [
        "cancelar contrato", "reclamar", "procon",
        "ouvidoria", "quero falar com humano", "supervisor"
    ]
    if any(t in texto for t in termos_risco):
        criterios.append("risco comercial")

    if historico_erros >= 2:
        criterios.append("falha recorrente da IA")

    if dados.get("sentimento") == "muito negativo":
        criterios.append("forte insatisfação")

    if dados.get("reclamacao"):
        criterios.append("reclamação explícita")

    return len(criterios) > 0, criterios

# ============================================================
# FLUXO PRINCIPAL
# ============================================================
def fluxo_atendimento():
    print("Atendente IA: Olá! Sou especialista em Google Chrome. Como posso ajudar?")

    historico_erros = 0
    tentativas_ia = 0
    MAX_TENTATIVAS_IA = 2

    while True:
        mensagem = input("Cliente: ")

        if mensagem.lower() in ["sair", "encerrar"]:
            print("Atendente IA: Agradeço o contato. Tenha um bom dia!")
            break

        analise = analisar_mensagem(mensagem)
        resposta = gerar_resposta(analise, mensagem)

        print("Atendente IA:", resposta)

        tentativas_ia += 1

        # Detecta falha da IA a partir da própria resposta
        if any(x in resposta.lower() for x in [
            "não entendi",
            "poderia repetir",
            "não consegui",
            "não sei"
        ]):
            historico_erros += 1

        deve_escalonar, motivos = precisa_escalonar(
            analise, mensagem, historico_erros
        )

        # ============================
        # DECISÃO CONTROLADA
        # ============================

        if deve_escalonar and tentativas_ia < MAX_TENTATIVAS_IA:
            print(
                "Atendente IA: Vou tentar te ajudar de outra forma para resolver o problema."
            )
            continue

        if deve_escalonar and tentativas_ia >= MAX_TENTATIVAS_IA:
            print(
                "\nAtendente IA: Entendo sua situação e quero garantir a melhor ajuda possível."
            )
            print(
                "Atendente IA: Vou encaminhar seu atendimento para um especialista humano."
            )
            print(
                f"Motivos do escalonamento: {', '.join(motivos)}\n"
            )
            break



if __name__ == "__main__":
    fluxo_atendimento()
