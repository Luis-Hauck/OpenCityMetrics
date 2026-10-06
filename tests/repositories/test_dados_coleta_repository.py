import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.cidade import Cidade
from database.models.dados_coleta import RegistroColeta
from repositories.dados_coleta_repository import DadosColetaRepository

engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    # Inserir uma cidade para a Foreign Key
    cidade = Cidade(id_ibge=1, nome="Cidade Teste", uf="SC", populacao=100)
    session.add(cidade)
    session.flush()

    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def repository(db_session):
    return DadosColetaRepository(db_session)


def test_create_registro_coleta(repository, db_session):
    data_coleta = datetime.now()
    dados = {
        "id": 1,
        "id_cidade": 1,
        "software_portal": "Portal X",
        "base_de_dados": "Base Y",
        "url": "http://teste.com",
        "formato_origem": "csv",
        "frequencia_coleta": "mensal",
        "dados_ausentes": 0,
        "data_coleta": data_coleta
    }

    result = repository.create(dados)
    assert result is True

    # Verifica no DB
    registro_in_db = db_session.get(RegistroColeta, 1)
    assert registro_in_db is not None
    assert registro_in_db.software_portal == "Portal X"
    assert registro_in_db.id_cidade == 1

def test_search_registro_coleta(repository, db_session):
    data_coleta = datetime.now()
    dados1 = {
        "id": 1,
        "id_cidade": 1,
        "software_portal": "Portal X",
        "base_de_dados": "Base 1",
        "url": "http://teste1.com",
        "formato_origem": "csv",
        "frequencia_coleta": "mensal",
        "dados_ausentes": 0,
        "data_coleta": data_coleta
    }
    dados2 = {
        "id": 2,
        "id_cidade": 1,
        "software_portal": "Portal Y",
        "base_de_dados": "Base 2",
        "url": "http://teste2.com",
        "formato_origem": "json",
        "frequencia_coleta": "semanal",
        "dados_ausentes": 2,
        "data_coleta": data_coleta
    }

    repository.create(dados1)
    repository.create(dados2)

    resultados = repository.search(id_cidade=1)
    assert len(resultados) == 2

    resultados_json = repository.search(formato_origem="json")
    assert len(resultados_json) == 1
    assert resultados_json[0].software_portal == "Portal Y"
