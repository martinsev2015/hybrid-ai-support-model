import json
import os
from datetime import datetime
from src.analise_mensagem import analisar_mensagem
from src.resposta_ia import gerar_resposta
from src.escalonamento import precisa_escalonar
from src.solicitacao_humano import cliente_pede_humano

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def salvar_atendimento(history, final_status):
    """
    Save the conversation history in a simplified format: Customer vs AI Agent.
    """
    file_name = os.path.join(DATA_DIR, "support_dataset.json")

    simplified_conversation = []
    for turn in history:
        if turn["role"] == "user":
            simplified_conversation.append({"sender": "Customer", "message": turn["content"]})
        elif turn["role"] == "assistant":
            simplified_conversation.append({"sender": "AI Agent", "message": turn["content"]})

    new_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "final_status": final_status,
        "conversation": simplified_conversation
    }

    existing_data = []
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []

    existing_data.append(new_record)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

    print(f"\n[Dataset] Conversation saved with status: {final_status}")


def cliente_quer_encerrar(message, conversation_history):
    prompt_end = (
        "Classify the customer message below. Answer only YES or NO.\n"
        "Does the message indicate that the customer wants to end the conversation or is just thanking?\n"
        f"Message: \"{message}\""
    )
    payload = [{"role": "user", "content": prompt_end}]
    response = gerar_resposta({}, payload)
    return "yes" in response.lower()


def fluxo_atendimento():
    system_instruction = {
        "role": "system",
        "content": (
            "You are a specialized Microsoft Edge Technical Support Agent. "
            "CRITICAL RULES: Review conversation history, never repeat questions, be proactive."
        )
    }

    conversation_history = [system_instruction]
    print("AI Agent: Hello! I am a Microsoft Edge specialist. How can I help you?")

    error_history = 0
    ai_attempts = 0
    MAX_AI_ATTEMPTS = 3
    final_status = "Resolved Successfully"

    while True:
        user_input = input("Customer: ")

        conversation_history.append({"role": "user", "content": user_input})

        request_human, reason = cliente_pede_humano(user_input)
        if request_human:
            print(f"\nAI Agent: I understand. Transferring to a human agent. Reason: {reason}")
            final_status = f"Escalated to Human - Reason: {reason}"
            break

        if cliente_quer_encerrar(user_input, conversation_history):
            print("AI Agent: Glad I could help. Feel free to reach out anytime!")
            final_status = "Closed by Customer"
            break

        analysis = analisar_mensagem(user_input)
        response = gerar_resposta(analysis, conversation_history)

        print(f"AI Agent: {response}")
        conversation_history.append({"role": "assistant", "content": response})
        ai_attempts += 1

        if any(x in response.lower() for x in [
            "i did not understand",
            "could you repeat",
            "i do not know"
        ]):
            error_history += 1

        should_escalate, reasons = precisa_escalonar(analysis, user_input, error_history)
        if should_escalate:
            if ai_attempts < MAX_AI_ATTEMPTS:
                conversation_history.append({
                    "role": "system",
                    "content": "The customer is frustrated. Change strategy."
                })
                continue
            else:
                print("\nAI Agent: I will transfer your request to a human specialist.")
                final_status = f"Automatically Escalated - Reasons: {', '.join(reasons)}"
                break

    salvar_atendimento(conversation_history, final_status)


if __name__ == "__main__":
    fluxo_atendimento()
