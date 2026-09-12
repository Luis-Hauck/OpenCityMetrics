# Assistente Agrícola Telegram Bot (MVP)

Este é um PoC/MVP (Proof of Concept / Minimum Viable Product) de um assistente agrícola no Telegram. O objetivo é permitir que agricultores registrem dados do dia a dia (despesas, colheitas) de forma sem atrito, através de mensagens de texto ou áudio natural.

## Tecnologias Utilizadas

- **Python 3.12+**
- **pyTelegramBotAPI**: Para interação com a API do Telegram utilizando métodos assíncronos (`AsyncTeleBot`).
- **pymongo**: Driver oficial assíncrono para conexão com o MongoDB.
- **pytest & pytest-asyncio**: Para a suíte de testes.

## Arquitetura do Projeto

O código está estruturado para separar as responsabilidades e facilitar a evolução futura:

- `database.py`: Gerencia a conexão com o banco de dados (MongoDB) e as operações de CRUD (Create, Read, Update, Delete) assíncronas para as coleções:
  - `usuarios`: Registra os usuários do Telegram.
  - `propriedades`: Registra os dados da fazenda/propriedade.
  - `eventos`: Registra as ações do dia a dia (ex: despesa, colheita).
- `main.py`: Contém a lógica principal do bot do Telegram.
  - **Fluxo de Onboarding**: Captura novos usuários pelo comando `/start` e coleta dados via botões interativos (`InlineKeyboardMarkup`).
  - **Fluxo de Escuta Passiva**: Fica ouvindo mensagens de texto e áudio de usuários cadastrados, processa o texto simulando uma IA, pede confirmação, e salva no banco.
- `user_states` (Memória Temporária): Em `main.py`, utilizamos um dicionário simples chamado `user_states` para guardar as etapas de quem está fazendo o onboarding, ou para guardar temporariamente os dados de uma despesa extraída enquanto aguardamos o clique no botão "Sim, registrar". **Em um ambiente de produção**, essa memória em RAM deve ser substituída por um banco chave-valor rápido, como o **Redis**, para não perder o estado caso o servidor do bot reinicie.

## Como a "Inteligência Artificial" funciona agora?

Na versão atual (MVP), não há uma chamada real a uma IA cara ou complexa.
A função `simular_ia_extracao()` em `main.py` atua como um "Mock". Ela recebe o texto, tenta encontrar um número no meio dele (ex: "gastei R$ 250 com adubo" -> extrai 250), e retorna um JSON fingindo ser a IA estruturando o dado.

### Próximos Passos (Integração Real com OpenAI):
Para evoluir isso em um ambiente real:
1. **Transcrição de Áudio**: Se a mensagem for voz, baixar o arquivo e enviar para a API da OpenAI (modelo `Whisper`) para transformar o áudio em texto.
2. **Extração de Dados (Function Calling)**: Enviar o texto para a API da OpenAI (modelo `GPT-4o-mini` ou similar). Utilizar a funcionalidade de *Structured Outputs* (ou *Function Calling*) para forçar o LLM a ler o texto ("gastei 250 de semente de milho") e retornar um JSON rígido e padronizado: `{"tipo": "despesa", "valor": 250.00, "categoria": "insumo"}`.
3. Substituir o `simular_ia_extracao` pela chamada HTTP real utilizando `httpx` ou a biblioteca `openai` do Python.

## Como Executar Localmente

1. **Requisitos**: Tenha o [Poetry](https://python-poetry.org/) instalado e o MongoDB rodando localmente (ou uma URI do MongoDB Atlas).
2. **Configuração**:
   - Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base).
   - Insira o token do seu bot em `TELEGRAM_BOT_TOKEN`. (Pegue isso com o @BotFather no Telegram).
   - Configure o `MONGODB_URI` (por padrão, usa o localhost:27017).
3. **Rodar**:
   ```bash
   poetry install
   poetry run python -m telegram_bot.main
   ```
4. **Testes**:
   ```bash
   poetry run pytest tests/
   ```
