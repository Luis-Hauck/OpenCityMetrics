import pytest
import pytest_asyncio
import os
from unittest.mock import AsyncMock, patch

from telegram_bot.database import get_usuario, create_usuario, create_propriedade, create_evento

# Tests using standard mocking. Note: proper DB testing should ideally use
# mongomock or testcontainers, but since we're using pymongo.AsyncMongoClient
# which is quite new, AsyncMocking the collections is a quick way for MVP.

@pytest.fixture
def mock_db_collections(mocker):
    usuarios = mocker.patch('telegram_bot.database.usuarios_collection', new_callable=AsyncMock)
    propriedades = mocker.patch('telegram_bot.database.propriedades_collection', new_callable=AsyncMock)
    eventos = mocker.patch('telegram_bot.database.eventos_collection', new_callable=AsyncMock)
    return usuarios, propriedades, eventos

@pytest.mark.asyncio
async def test_get_usuario(mock_db_collections):
    usuarios_col, _, _ = mock_db_collections
    usuarios_col.find_one.return_value = {"_id": 123, "nome": "Test User", "propriedade_id": "abc"}

    usuario = await get_usuario(123)

    usuarios_col.find_one.assert_called_once_with({"_id": 123})
    assert usuario["nome"] == "Test User"

@pytest.mark.asyncio
async def test_create_usuario(mock_db_collections):
    usuarios_col, _, _ = mock_db_collections

    usuario = await create_usuario(123, "Test User", "abc")

    usuarios_col.insert_one.assert_called_once_with({"_id": 123, "nome": "Test User", "propriedade_id": "abc"})
    assert usuario["_id"] == 123

@pytest.mark.asyncio
async def test_create_propriedade(mock_db_collections):
    _, propriedades_col, _ = mock_db_collections

    # Mocking the result of insert_one to have inserted_id
    mock_result = AsyncMock()
    mock_result.inserted_id = "mocked_id"
    propriedades_col.insert_one.return_value = mock_result

    propriedade = await create_propriedade("Até 5 ha", "Prata")

    propriedades_col.insert_one.assert_called_once()
    args, _ = propriedades_col.insert_one.call_args
    assert args[0]["hectares"] == "Até 5 ha"
    assert args[0]["variedade"] == "Prata"
    assert propriedade["_id"] == "mocked_id"

@pytest.mark.asyncio
async def test_create_evento(mock_db_collections):
    _, _, eventos_col = mock_db_collections

    mock_result = AsyncMock()
    mock_result.inserted_id = "mocked_evento_id"
    eventos_col.insert_one.return_value = mock_result

    evento = await create_evento(123, "abc", "despesa", {"valor": 100})

    eventos_col.insert_one.assert_called_once()
    args, kwargs = eventos_col.insert_one.call_args
    assert args[0]["usuario_id"] == 123
    assert args[0]["propriedade_id"] == "abc"
    assert args[0]["tipo"] == "despesa"
    assert "data_registro" in args[0]
    assert args[0]["dados"] == {"valor": 100}
    assert evento["_id"] == "mocked_evento_id"
