import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.cidade import Cidade
from database.models.obras import Obra
from repositories.obras_repository import ObrasRepository

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
    return ObrasRepository(db_session)


def test_create_or_update_obra(repository, db_session):
    data_atual = datetime.now()
    dados = {
        "id": 1,
        "id_cidade": 1,
        "entidade": "Prefeitura",
        "numero_obra": "123",
        "ano_obra": "2023",
        "cnpj_cpf_empresa": "11.111.111/0001-11",
        "nome_empresa": "Construtora A",
        "valor_total": 100000.0,
        "descricao_da_obra": "Reforma praça",
        "data_cadastramento": data_atual,
        "data_inicio_execucao": data_atual,
        "data_previsao_conclusao": data_atual,
        "situacao_obra": "Em andamento",
        "qtd_contratada": 1.0,
        "valor_unit_contratado": 100000.0,
        "valor_tot_contratado": 100000.0,
        "percentual_contratado": 100.0,
        "qtd_executada": 0.5,
        "valor_unit_executado": 100000.0,
        "valor_tot_executado": 50000.0,
        "percentual_executado": 50.0,
        "percentual_pago": 50.0
    }

    # Create
    result = repository.create_or_update(dados)
    assert result is True

    obra_in_db = db_session.get(Obra, 1)
    assert obra_in_db.situacao_obra == "Em andamento"
    assert obra_in_db.valor_total == 100000.0

    # Update (usando a mesma chave unica: id_cidade, entidade, numero_obra)
    dados["situacao_obra"] = "Concluida"
    dados["valor_total"] = 120000.0 # valor modificado para testar upsert
    result_update = repository.create_or_update(dados)
    assert result_update is True

    obra_atualizada = db_session.get(Obra, 1)
    assert obra_atualizada.situacao_obra == "Concluida"
    assert obra_atualizada.valor_total == 120000.0


def test_search_obras(repository, db_session):
    data_atual = datetime.now()
    dados = {
        "id": 1,
        "id_cidade": 1,
        "entidade": "Prefeitura",
        "numero_obra": "123",
        "ano_obra": "2023",
        "cnpj_cpf_empresa": "11.111.111/0001-11",
        "nome_empresa": "Construtora A",
        "valor_total": 100000.0,
        "descricao_da_obra": "Reforma praça",
        "data_cadastramento": data_atual,
        "data_inicio_execucao": data_atual,
        "data_previsao_conclusao": data_atual,
        "situacao_obra": "Concluida",
        "qtd_contratada": 1.0,
        "valor_unit_contratado": 100000.0,
        "valor_tot_contratado": 100000.0,
        "percentual_contratado": 100.0,
        "qtd_executada": 1.0,
        "valor_unit_executado": 100000.0,
        "valor_tot_executado": 100000.0,
        "percentual_executado": 100.0,
        "percentual_pago": 100.0
    }

    repository.create_or_update(dados)

    resultados = repository.search(id_cidade=1, situacao_obra="Concluida")
    assert len(resultados) == 1
    assert resultados[0].entidade == "Prefeitura"

    resultados_vazios = repository.search(id_cidade=1, situacao_obra="Em andamento")
    assert len(resultados_vazios) == 0
