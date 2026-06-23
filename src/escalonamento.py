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
