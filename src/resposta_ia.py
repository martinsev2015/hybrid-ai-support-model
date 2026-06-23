from src.config import client, OPENAI_MODEL

def gerar_resposta(dados, mensagem):

    toxic = dados.get("toxicidade", {}).get("toxicity", 0)
    insult = dados.get("toxicidade", {}).get("insult", 0)
    anger = dados.get("toxicidade", {}).get("anger", 0)

    emocao_emoji = dados.get("emocao_emoji")
    apenas_emoji = dados.get("apenas_emoji", False)

    if toxic > 0.6 or insult > 0.5 or anger > 0.5:
        return (
            "I understand this situation may be frustrating. "
            "I will escalate your request to a human agent for further assistance."
        )

    if apenas_emoji and emocao_emoji == "frustration":
        return (
            "I can see that you're feeling frustrated. "
            "I will transfer your request to a human specialist."
        )

    if dados.get("sentimento") in ["negative", "very negative"]:
        prompt = (
            "The customer is dissatisfied. "
            "Respond as a Microsoft Edge specialist in an empathetic and helpful way. "
            f"Customer message: {mensagem}"
        )

    elif dados.get("reclamacao"):
        prompt = (
            "The customer reported an issue with Microsoft Edge. "
            "Ask for additional details clearly and politely before providing a solution. "
            f"Customer message: {mensagem}"
        )

    elif emocao_emoji == "confusion":
        prompt = (
            "The customer seems confused. "
            "Explain the solution in a simple and clear way as a Microsoft Edge specialist. "
            f"Customer message: {mensagem}"
        )

    else:
        prompt = (
            "Act as a Microsoft Edge technical support specialist. "
            "Provide a clear and direct solution if possible. "
            "If the request is unclear, ask for more details before answering. "
            f"Customer message: {mensagem}"
        )

    resposta = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return resposta.choices[0].message.content.strip()
