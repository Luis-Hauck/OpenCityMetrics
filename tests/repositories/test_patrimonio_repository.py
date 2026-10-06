import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.cidade import Cidade
from database.models.patrimonio import Patrimonio
from repositories.patrimonio_repository import PatrimonioRepository

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
    return PatrimonioRepository(db_session)


def test_create_or_update_patrimonio(repository, db_session):
    hoje = date.today()
    dados = {
        "id": 1,
        "id_cidade": 1,
        "entidade": "Prefeitura",
        "tipo_patrimonio": "Veículo",
        "codigo": "V-001",
        "descricao": "Carro Oficial",
        "num_tombamento": "T-1234",
        "data_aquisicao": hoje,
        "data_incorporacao": hoje,
        "status_patrimonio": "Ativo",
        "centro_custo": "Gabinete",
        "fornecedor": "Concessionária",
        "valor_contabil": 50000.0,
        "sit_aquisicao": "Compra"
    }

    # Create
    result = repository.create_or_update(dados)
    assert result is True

    pat_in_db = db_session.get(Patrimonio, 1)
    assert pat_in_db.valor_contabil == 50000.0

    # Update (mesmo id_cidade, entidade, codigo)
    dados["valor_contabil"] = 45000.0
    dados["status_patrimonio"] = "Em manutenção"
    result_update = repository.create_or_update(dados)
    assert result_update is True

    pat_atualizado = db_session.get(Patrimonio, 1)
    assert pat_atualizado.valor_contabil == 45000.0
    assert pat_atualizado.status_patrimonio == "Em manutenção"


def test_search_patrimonios(repository, db_session):
    hoje = date.today()
    dados = {
        "id": 1,
        "id_cidade": 1,
        "entidade": "Prefeitura",
        "tipo_patrimonio": "Imóvel",
        "codigo": "I-001",
        "descricao": "Prédio da Prefeitura",
        "num_tombamento": "T-9999",
        "data_aquisicao": hoje,
        "data_incorporacao": hoje,
        "status_patrimonio": "Ativo",
        "centro_custo": "Administração",
        "fornecedor": "Construtora",
        "valor_contabil": 1000000.0,
        "sit_aquisicao": "Construção"
    }

    repository.create_or_update(dados)

    resultados = repository.search(id_cidade=1, tipo_patrimonio="Imóvel")
    assert len(resultados) == 1
    assert resultados[0].codigo == "I-001"

    resultados_vazios = repository.search(id_cidade=1, status_patrimonio="Baixado")
    assert len(resultados_vazios) == 0
