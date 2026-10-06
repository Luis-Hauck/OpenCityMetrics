import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.cidade import Cidade
from database.models.funcionario import Funcionario
from repositories.funcionario_repository import FuncionarioRepository

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
    return FuncionarioRepository(db_session)


def test_create_or_update_funcionario(repository, db_session):
    data_atual = datetime(2023, 10, 1)
    dados = {
        "id": 1,
        "id_cidade": 1,
        "id_funcionario": "F-123",
        "entidade": "Prefeitura",
        "contrato": "Estatutário",
        "nome": "João Silva",
        "cargo": "Professor",
        "regime_trabalho": "40h",
        "proventos": 5000.0,
        "data_referencia": data_atual
    }

    # Create
    result = repository.create_or_update(dados)
    assert result is True

    func_in_db = db_session.get(Funcionario, 1)
    assert func_in_db.cargo == "Professor"
    assert func_in_db.proventos == 5000.0

    # Update
    dados["cargo"] = "Diretor"
    dados["proventos"] = 7000.0
    result_update = repository.create_or_update(dados)
    assert result_update is True

    func_atualizado = db_session.get(Funcionario, 1)
    assert func_atualizado.cargo == "Diretor"
    assert func_atualizado.proventos == 7000.0


def test_search_funcionarios(repository, db_session):
    data_atual = datetime(2023, 10, 1)
    dados = {
        "id": 1,
        "id_cidade": 1,
        "id_funcionario": "F-123",
        "entidade": "Prefeitura",
        "contrato": "Estatutário",
        "nome": "João Silva",
        "cargo": "Professor",
        "regime_trabalho": "40h",
        "proventos": 5000.0,
        "data_referencia": data_atual
    }

    repository.create_or_update(dados)

    resultados = repository.search(id_cidade=1, nome="João Silva")
    assert len(resultados) == 1
    assert resultados[0].cargo == "Professor"

    resultados_vazios = repository.search(id_cidade=1, cargo="Médico")
    assert len(resultados_vazios) == 0
