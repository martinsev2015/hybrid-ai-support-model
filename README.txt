================================================================================
 App_chat — Agente de Suporte Técnico com IA e Escalonamento Híbrido
================================================================================

Projeto de mestrado que implementa um agente conversacional para suporte técnico
ao Microsoft Edge. O sistema combina um modelo híbrido (regras + análise de NLP)
com um baseline de LLM puro (GPT) para decidir automaticamente entre responder,
pedir esclarecimento ou escalonar para um atendente humano.

--------------------------------------------------------------------------------
FLUXO PRINCIPAL
--------------------------------------------------------------------------------

  1. Entrada da mensagem do cliente
          ↓
  2. Análise automática
       - Sentimento (TextBlob)
       - Idioma (langdetect)
       - Toxicidade (Detoxify)
       - Emoção via emoji (Emoji API)
          ↓
  3. Decisão lógica (modelo híbrido)
       - Pedido explícito de humano?  → escalate
       - Critérios de escalonamento?  → escalate
       - Mensagem ambígua/curta?      → clarify
       - Caso padrão                  → respond
          ↓
  4. Geração de resposta (OpenAI GPT)
          ↓
  5. Escalonamento / Encerramento / Próximo passo

--------------------------------------------------------------------------------
ESTRUTURA DO PROJETO
--------------------------------------------------------------------------------

  App_chat/
  ├── src/                  # Código core do agente
  │   ├── main.py           # Fluxo principal de atendimento
  │   ├── analise_mensagem.py
  │   ├── resposta_ia.py
  │   ├── escalonamento.py
  │   ├── solicitacao_humano.py
  │   ├── emoji_utils.py
  │   └── config.py
  │
  ├── experiments/          # Avaliação dos modelos
  │   ├── experiments.py    # Roda predições hybrid + LLM sobre o dataset
  │   └── metrics.py        # Calcula DA, CA, EA, PRR e matrizes de confusão
  │
  ├── analysis/             # Geração de gráficos
  │   ├── graphics_accuracy_by_request.py
  │   ├── graphics_confusion_matrix.py
  │   └── graphics_llm_hybrid.py
  │
  ├── scripts/              # Pipeline de dados
  │   ├── scraper.py        # Coleta perguntas do Microsoft Q&A (Selenium)
  │   ├── dataset_generator.py   # Extrai títulos/textos do dataset bruto
  │   ├── dataset_generator2.py  # Gera variações aumentadas
  │   ├── csv_generator.py       # Converte JSON aumentado para CSV de anotação
  │   └── clean_dataset.py       # Limpeza e deduplicação do CSV
  │
  ├── tests/
  │   └── test_chat_agent.py
  │
  ├── data/
  │   ├── raw/              # Dados originais e aumentados
  │   ├── processed/        # dataset_clean.csv, support_dataset.json
  │   ├── results/          # results.json, error_analysis_*.json
  │   └── fine_tuning/      # Arquivos .jsonl para fine-tuning
  │
  ├── figures/              # Gráficos gerados
  ├── .env                  # Variáveis de ambiente (não versionar)
  └── README.txt

--------------------------------------------------------------------------------
PRÉ-REQUISITOS
--------------------------------------------------------------------------------

  - Python 3.9+
  - Conta na OpenAI (API Key)
  - Conta na Emoji API (https://emoji-api.com)
  - Google Chrome + ChromeDriver instalado (apenas para scraper.py)

--------------------------------------------------------------------------------
INSTALAÇÃO
--------------------------------------------------------------------------------

  1. Crie e ative um ambiente virtual:

       python -m venv .venv
       source .venv/bin/activate          # macOS/Linux
       .venv\Scripts\activate             # Windows

  2. Instale as dependências:

       pip install openai python-dotenv textblob langdetect detoxify \
                   pandas scikit-learn matplotlib requests selenium \
                   webdriver-manager

  3. Configure o arquivo .env na raiz do projeto:

       OPENAI_API_KEY=sk-...
       OPENAI_MODEL=gpt-4.1-mini
       EMOJI_API_KEY=...

--------------------------------------------------------------------------------
COMO EXECUTAR
--------------------------------------------------------------------------------

  Rodar o agente de suporte (chat interativo):

      python -m src.main

  Rodar experimentos (gera predições no dataset):

      python -m experiments.experiments

  Calcular métricas:

      python -m experiments.metrics

  Gerar gráficos (executar da raiz do projeto):

      python analysis/graphics_llm_hybrid.py
      python analysis/graphics_confusion_matrix.py
      python analysis/graphics_accuracy_by_request.py

--------------------------------------------------------------------------------
PIPELINE DE DADOS (ordem de execução)
--------------------------------------------------------------------------------

  1. scripts/scraper.py            → data/raw/dataset_high_interaction.json
  2. scripts/dataset_generator.py  → data/raw/questions.json
  3. scripts/dataset_generator2.py → data/raw/augmented_questions.json
  4. scripts/csv_generator.py      → data/raw/dataset_to_label.csv
       (anotar manualmente as colunas "type" e "expected_action")
  5. scripts/clean_dataset.py      → data/processed/dataset_clean.csv
  6. experiments/experiments.py    → data/results/results.json
  7. experiments/metrics.py        → exibe métricas no terminal
  8. analysis/*.py                 → figures/

--------------------------------------------------------------------------------
MÉTRICAS AVALIADAS
--------------------------------------------------------------------------------

  DA  — Decision Accuracy       Acurácia geral da decisão
  CA  — Clarification Accuracy  Acurácia nos casos que exigem clarificação
  EA  — Escalation Accuracy     Acurácia nos casos de escalonamento
  PRR — Premature Response Rate Taxa de respostas prematuras indevidas

--------------------------------------------------------------------------------
NOTAS
--------------------------------------------------------------------------------

  - O arquivo .env nunca deve ser versionado (adicione ao .gitignore).
  - O support_dataset.json é gerado automaticamente em data/processed/ a cada
    conversa concluída via src/main.py.
  - Os scripts de análise devem ser executados a partir da raiz do projeto para
    que os caminhos relativos (data/, figures/) funcionem corretamente.

================================================================================
