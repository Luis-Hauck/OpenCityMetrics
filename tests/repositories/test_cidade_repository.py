import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from models.cidade import Cidade
from repositories.cidade_repository import CidadeRepository
from repositories.base_repository import ItemNotFoundError

# Setup an in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    # Teardown
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def repository(db_session):
    return CidadeRepository(db_session)

def test_create_cidade(repository):
    cidade_data = {
        "id_ibge": 1234567,
        "nome": "Cidade Teste",
        "uf": "SC",
        "populacao": 50000
    }
    created_cidade = repository.create(cidade_data)

    assert created_cidade.id_ibge == 1234567
    assert created_cidade.nome == "Cidade Teste"
    assert created_cidade.uf == "SC"
    assert created_cidade.populacao == 50000

def test_get_cidade(repository):
    cidade_data = {
        "id_ibge": 1234567,
        "nome": "Cidade Teste",
        "uf": "SC",
        "populacao": 50000
    }
    repository.create(cidade_data)

    cidade = repository.get(1234567)
    assert cidade is not None
    assert cidade.nome == "Cidade Teste"

def test_get_nonexistent_cidade(repository):
    with pytest.raises(ItemNotFoundError):
        repository.get(9999999)

def test_get_all_cidades(repository):
    repository.create({
        "id_ibge": 1111111,
        "nome": "Cidade 1",
        "uf": "SP",
        "populacao": 1000
    })
    repository.create({
        "id_ibge": 2222222,
        "nome": "Cidade 2",
        "uf": "RJ",
        "populacao": 2000
    })

    cidades = repository.get_all()
    assert len(cidades) == 2
    assert cidades[0].nome == "Cidade 1"
    assert cidades[1].nome == "Cidade 2"

def test_update_cidade(repository):
    cidade_data = {
        "id_ibge": 1234567,
        "nome": "Cidade Teste",
        "uf": "SC",
        "populacao": 50000
    }
    created_cidade = repository.create(cidade_data)

    updated_data = {"nome": "Cidade Atualizada", "populacao": 55000}
    updated_cidade = repository.update(1234567, updated_data)

    assert updated_cidade.id_ibge == 1234567
    assert updated_cidade.nome == "Cidade Atualizada"
    assert updated_cidade.populacao == 55000
    assert updated_cidade.uf == "SC" # Unchanged

def test_update_nonexistent_cidade(repository):
    with pytest.raises(ItemNotFoundError):
        repository.update(9999999, {"nome": "Nao Existe"})

def test_delete_cidade(repository):
    cidade_data = {
        "id_ibge": 1234567,
        "nome": "Cidade Teste",
        "uf": "SC",
        "populacao": 50000
    }
    repository.create(cidade_data)

    result = repository.delete(1234567)
    assert result is True

    with pytest.raises(ItemNotFoundError):
        repository.get(1234567)

def test_delete_nonexistent_cidade(repository):
    with pytest.raises(ItemNotFoundError):
        repository.delete(9999999)
