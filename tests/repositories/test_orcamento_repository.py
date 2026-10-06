import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.cidade import Cidade
from database.models.orcamento import Orcamento
from repositories.orcamento_repository import OrcamentoRepository

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
    return OrcamentoRepository(db_session)


def test_create_or_update_orcamento(repository, db_session):
    dados = {
        "id": 1,
        "id_cidade": 1,
        "ano_exercicio": "2023",
        "mes_referencia": "10",
        "entidade": "Prefeitura",
        "funcao": "Saúde",
        "subfuncao": "Atenção Básica",
        "programa": "Saúde para todos",
        "acao": "Manutenção",
        "vinculo": "Recurso Próprio",
        "categoria_economica": "Despesas Correntes",
        "grupo_despesa": "Pessoal",
        "modalidade": "Aplicação Direta",
        "orcamento_inicial": 1000.0,
        "orcamento_atualizado": 1000.0,
        "empenhado_no_periodo": 500.0,
        "liquidado_no_periodo": 500.0,
        "pago_no_periodo": 500.0
    }

    # Create
    result = repository.create_or_update(dados)
    assert result is True

    orc_in_db = db_session.get(Orcamento, 1)
    assert orc_in_db.pago_no_periodo == 500.0

    # Update
    dados["pago_no_periodo"] = 600.0
    dados["orcamento_atualizado"] = 1200.0
    result_update = repository.create_or_update(dados)
    assert result_update is True

    orc_atualizado = db_session.get(Orcamento, 1)
    assert orc_atualizado.pago_no_periodo == 600.0
    assert orc_atualizado.orcamento_atualizado == 1200.0


def test_search_orcamentos(repository, db_session):
    dados = {
        "id": 1,
        "id_cidade": 1,
        "ano_exercicio": "2023",
        "mes_referencia": "10",
        "entidade": "Prefeitura",
        "funcao": "Saúde",
        "subfuncao": "Atenção Básica",
        "programa": "Saúde para todos",
        "acao": "Manutenção",
        "vinculo": "Recurso Próprio",
        "categoria_economica": "Despesas Correntes",
        "grupo_despesa": "Pessoal",
        "modalidade": "Aplicação Direta",
        "orcamento_inicial": 1000.0,
        "orcamento_atualizado": 1000.0,
        "empenhado_no_periodo": 500.0,
        "liquidado_no_periodo": 500.0,
        "pago_no_periodo": 500.0
    }

    repository.create_or_update(dados)

    resultados = repository.search(id_cidade=1, ano_exercicio="2023", mes_referencia="10")
    assert len(resultados) == 1
    assert resultados[0].funcao == "Saúde"

    resultados_vazios = repository.search(id_cidade=1, ano_exercicio="2022")
    assert len(resultados_vazios) == 0
