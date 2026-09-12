import os
import asyncio
import json
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from .database import get_usuario, create_propriedade, create_usuario, create_evento

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    # Use a dummy token for test environments if not set
    TOKEN = "123456789:dummy_token"

bot = AsyncTeleBot(TOKEN)

# Dicionário em memória para guardar os estados temporários dos usuários.
# No fluxo de onboarding, guarda em qual etapa o usuário está (ex: escolhendo hectares).
# No fluxo de escuta, guarda o ID do evento pendente até a confirmação.
# Em produção, para não perder os dados se o bot reiniciar, isso poderia ser salvo no Redis.
user_states = {}

# --- Mock da IA ---
async def simular_ia_extracao(mensagem: str) -> dict:
    """
    Função mock para simular a extração de dados usando IA (ex: OpenAI GPT-4).

    Para o MVP, tenta extrair um valor numérico simples da mensagem para não
    retornar sempre um valor fixo. Se não achar, usa 150.00 como fallback.

    Futuramente, aqui será feita a chamada real à API da OpenAI:
    1. Enviar `mensagem` (texto ou áudio transcrito) para o LLM.
    2. Usar 'Function Calling' ou 'JSON Mode' do OpenAI para garantir que
       o LLM retorne o JSON estruturado contendo 'tipo', 'valor', e 'categoria'.
    """
    await asyncio.sleep(1)  # Simula o tempo de processamento de rede/IA

    # Tenta achar um número na mensagem para fingir que a IA extraiu do texto do usuário
    valor = 150.00
    palavras = mensagem.replace(',', '.').split()
    for p in palavras:
        try:
            # Pega o primeiro número que achar, ignorando cifrões (ex: R$100 -> 100)
            limpo = p.replace('R$', '').replace('R', '').replace('$', '')
            valor = float(limpo)
            break
        except ValueError:
            continue

    return {
        "tipo": "despesa",
        "dados": {
            "valor": valor,
            "categoria": "insumo", # Em prod, a IA classificaria a categoria com base no texto
            "descricao_original": mensagem
        }
    }


# --- Fluxo 1: Onboarding ---
@bot.message_handler(commands=['start'])
async def start_handler(message):
    user_id = message.from_user.id
    usuario = await get_usuario(user_id)

    if usuario:
        await bot.reply_to(message, f"Olá {usuario.get('nome')}! Já te conheço. Pode me mandar seus gastos e colheitas.")
    else:
        # Iniciar fluxo de cadastro
        markup = InlineKeyboardMarkup()
        markup.row_width = 3
        markup.add(
            InlineKeyboardButton("Até 5 ha", callback_data="ha_5"),
            InlineKeyboardButton("5 a 10 ha", callback_data="ha_10"),
            InlineKeyboardButton("Mais de 10 ha", callback_data="ha_mais_10")
        )
        user_states[user_id] = {"step": "hectares"}
        await bot.send_message(message.chat.id, "Bem-vindo! Quantos hectares tem a propriedade?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: user_states.get(call.from_user.id, {}).get("step") == "hectares")
async def callback_hectares(call):
    user_id = call.from_user.id
    ha_map = {
        "ha_5": "Até 5 ha",
        "ha_10": "5 a 10 ha",
        "ha_mais_10": "Mais de 10 ha"
    }
    hectares = ha_map.get(call.data, "Desconhecido")
    user_states[user_id]["hectares"] = hectares
    user_states[user_id]["step"] = "variedade"

    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("Caturra / Nanica", callback_data="var_caturra_nanica"),
        InlineKeyboardButton("Prata", callback_data="var_prata"),
        InlineKeyboardButton("Outra", callback_data="var_outra")
    )

    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f"Hectares definidos: {hectares}.\nQual a variedade principal?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: user_states.get(call.from_user.id, {}).get("step") == "variedade")
async def callback_variedade(call):
    user_id = call.from_user.id
    var_map = {
        "var_caturra_nanica": "Caturra / Nanica",
        "var_prata": "Prata",
        "var_outra": "Outra"
    }
    variedade = var_map.get(call.data, "Desconhecida")
    hectares = user_states[user_id].get("hectares")

    try:
        propriedade = await create_propriedade(hectares, variedade)
        await create_usuario(user_id, call.from_user.first_name, propriedade["_id"])

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Cadastro concluído! Agora é só me mandar um áudio ou texto avisando sobre os gastos e colheitas.")
    except Exception as e:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Houve um erro ao realizar seu cadastro. Tente novamente mais tarde.")
        print(f"Erro no cadastro: {e}")
    finally:
        if user_id in user_states:
            del user_states[user_id]


# --- Fluxo 2: Escuta Passiva ---
@bot.message_handler(content_types=['text', 'voice'])
async def passive_listening_handler(message):
    user_id = message.from_user.id

    # Check if user is registered before processing
    usuario = await get_usuario(user_id)
    if not usuario:
        await bot.reply_to(message, "Por favor, digite /start para fazer o cadastro primeiro.")
        return

    # Se estiver num passo de onboarding (por engano enviou texto), ignora
    if user_id in user_states:
        return

    processing_msg = await bot.reply_to(message, "⏳ Processando...")

    # Se for voz, extrair texto ou simular.
    # Em prod, baixaria o ogg, converteria e mandaria pro Whisper.
    texto_entrada = message.text if message.content_type == 'text' else "Audio message received"

    try:
        # Mocking IA
        dados_extraidos = await simular_ia_extracao(texto_entrada)

        # Guardar temporariamente para confirmação
        temp_state_id = f"evento_{user_id}_{message.message_id}"
        user_states[temp_state_id] = {
            "usuario_id": user_id,
            "propriedade_id": usuario.get("propriedade_id"),
            "dados_extraidos": dados_extraidos,
            "msg_id": processing_msg.message_id
        }

        # Pedir confirmação
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Sim, registrar", callback_data=f"conf_sim_{temp_state_id}"),
            InlineKeyboardButton("Não, cancelar", callback_data=f"conf_nao_{temp_state_id}")
        )

        texto_confirmacao = f"Entendi que é uma {dados_extraidos['tipo']} de R$ {dados_extraidos['dados']['valor']:.2f} ({dados_extraidos['dados']['categoria']}). Confirma?"

        await bot.edit_message_text(chat_id=message.chat.id, message_id=processing_msg.message_id,
                                    text=texto_confirmacao, reply_markup=markup)

    except Exception as e:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=processing_msg.message_id,
                                    text="❌ Ocorreu um erro ao processar sua mensagem. Tente novamente.")
        print(f"Erro no processamento de escuta: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("conf_"))
async def callback_confirmacao_evento(call):
    # Formato: conf_sim_evento_123_456
    parts = call.data.split("_", 2)
    acao = parts[1] # sim ou nao
    temp_state_id = parts[2]

    estado = user_states.get(temp_state_id)
    if not estado:
        await bot.answer_callback_query(call.id, "Sessão expirada ou já processada.")
        return

    if acao == "sim":
        try:
            dados_extraidos = estado["dados_extraidos"]
            await create_evento(
                usuario_id=estado["usuario_id"],
                propriedade_id=estado["propriedade_id"],
                tipo=dados_extraidos["tipo"],
                dados=dados_extraidos["dados"]
            )
            valor = dados_extraidos['dados']['valor']
            tipo_capitalizado = dados_extraidos['tipo'].capitalize()
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f"✅ {tipo_capitalizado} de R$ {valor:.2f} registrada com sucesso!")
        except Exception as e:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="❌ Erro ao salvar no banco de dados. Tente novamente.")
            print(f"Erro ao salvar evento: {e}")
    else:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Registro cancelado.")

    if temp_state_id in user_states:
        del user_states[temp_state_id]

async def main():
    print("Bot is running...")
    await bot.polling()

if __name__ == "__main__":
    asyncio.run(main())
