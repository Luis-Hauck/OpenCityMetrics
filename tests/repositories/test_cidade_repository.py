import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.cidade import Cidade
from repositories.cidade_repository import CidadeRepository

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

def test_create_cidade(repository, db_session):
    cidade = Cidade(
        id_ibge=1234567,
        nome="Cidade Teste",
        uf="SC",
        populacao=50000
    )
    result = repository.create(cidade)

    assert result is True

    # Verify in DB
    cidade_in_db = db_session.get(Cidade, 1234567)
    assert cidade_in_db is not None
    assert cidade_in_db.id_ibge == 1234567
    assert cidade_in_db.nome == "Cidade Teste"
    assert cidade_in_db.uf == "SC"
    assert cidade_in_db.populacao == 50000

def test_get_by_id_cidade(repository, db_session):
    cidade = Cidade(
        id_ibge=1234567,
        nome="Cidade Teste",
        uf="SC",
        populacao=50000
    )
    repository.create(cidade)

    cidade_buscada = repository.get_by_id(1234567)
    assert cidade_buscada is not None
    assert cidade_buscada.nome == "Cidade Teste"

def test_get_by_id_nonexistent_cidade(repository):
    cidade_buscada = repository.get_by_id(9999999)
    assert cidade_buscada is None

def test_update_cidade(repository, db_session):
    cidade = Cidade(
        id_ibge=1234567,
        nome="Cidade Teste",
        uf="SC",
        populacao=50000
    )
    repository.create(cidade)

    result = repository.update(1234567, nome="Cidade Atualizada", populacao=55000)
    assert result is True

    updated_cidade = db_session.get(Cidade, 1234567)
    assert updated_cidade.id_ibge == 1234567
    assert updated_cidade.nome == "Cidade Atualizada"
    assert updated_cidade.populacao == 55000
    assert updated_cidade.uf == "SC" # Unchanged

def test_update_nonexistent_cidade(repository):
    result = repository.update(9999999, nome="Nao Existe")
    assert result is False
