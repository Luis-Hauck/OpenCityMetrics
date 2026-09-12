import os
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
# Create an asynchronous MongoClient
client = AsyncMongoClient(MONGO_URI)
db = client.assistente_agricola

usuarios_collection = db.usuarios
propriedades_collection = db.propriedades
eventos_collection = db.eventos

async def get_usuario(telegram_user_id: int):
    """Retorna um usuário pelo seu ID do Telegram."""
    return await usuarios_collection.find_one({"_id": telegram_user_id})

async def create_usuario(telegram_user_id: int, nome: str, propriedade_id):
    """Cria um novo usuário na coleção."""
    usuario = {
        "_id": telegram_user_id,
        "nome": nome,
        "propriedade_id": propriedade_id
    }
    await usuarios_collection.insert_one(usuario)
    return usuario

async def create_propriedade(hectares: str, variedade: str):
    """Cria uma nova propriedade na coleção."""
    propriedade = {
        "hectares": hectares,
        "variedade": variedade
    }
    result = await propriedades_collection.insert_one(propriedade)
    propriedade["_id"] = result.inserted_id
    return propriedade

async def create_evento(usuario_id: int, propriedade_id, tipo: str, dados: dict):
    """Cria um novo evento (despesa, colheita, etc)."""
    evento = {
        "usuario_id": usuario_id,
        "propriedade_id": propriedade_id,
        "tipo": tipo,
        "data_registro": datetime.now(timezone.utc),
        "dados": dados
    }
    result = await eventos_collection.insert_one(evento)
    evento["_id"] = result.inserted_id
    return evento
