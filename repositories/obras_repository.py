import logging
from typing import Union
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.obras import Obra

logger = logging.getLogger(__name__)

class ObrasRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_or_update(self, dados_obra: Union[dict, list[dict]]) -> bool:
        """
        Insere ou atualiza os dados de uma ou várias obras no banco de dados.
        Suporta envio em lote (bulk_upsert) através de uma lista de dicionários.

        Args:
            dados_obra: Dicionário ou Lista de Dicionários com os dados da Obra.

        Returns:
            bool: True se adicionou/atualizou com sucesso; False caso ocorra um erro.
        """
        try:
            if not dados_obra:
                logger.error("Dados da obra não fornecidos.")
                return False

            if isinstance(dados_obra, dict):
                dados_obra = [dados_obra]

            from sqlalchemy.dialects.postgresql import insert as pg_insert
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            dialect_name = self.session.bind.dialect.name

            if dialect_name == 'sqlite':
                stmt = sqlite_insert(Obra)
            else:
                stmt = pg_insert(Obra)

            update_dict = {
                'ano_obra': stmt.excluded.ano_obra,
                'cnpj_cpf_empresa': stmt.excluded.cnpj_cpf_empresa,
                'nome_empresa': stmt.excluded.nome_empresa,
                'valor_total': stmt.excluded.valor_total,
                'descricao_da_obra': stmt.excluded.descricao_da_obra,
                'data_cadastramento': stmt.excluded.data_cadastramento,
                'data_inicio_execucao': stmt.excluded.data_inicio_execucao,
                'data_previsao_conclusao': stmt.excluded.data_previsao_conclusao,
                'situacao_obra': stmt.excluded.situacao_obra,
                'qtd_contratada': stmt.excluded.qtd_contratada,
                'valor_unit_contratado': stmt.excluded.valor_unit_contratado,
                'valor_tot_contratado': stmt.excluded.valor_tot_contratado,
                'percentual_contratado': stmt.excluded.percentual_contratado,
                'qtd_executada': stmt.excluded.qtd_executada,
                'valor_unit_executado': stmt.excluded.valor_unit_executado,
                'valor_tot_executado': stmt.excluded.valor_tot_executado,
                'percentual_executado': stmt.excluded.percentual_executado,
                'percentual_pago': stmt.excluded.percentual_pago
            }

            if dialect_name == 'sqlite':
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id_cidade', 'entidade', 'numero_obra'],
                    set_=update_dict
                )
            else:
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_cidade_obra',
                    set_=update_dict
                )

            self.session.execute(stmt, dados_obra)
            self.session.flush()
            self.session.expire_all()

            logger.info("Dados das obras salvos/atualizados com sucesso em lote!")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar os dados da obra em lote: {e}")
            return False

    def search(self,
               id_cidade: int | None = None,
               entidade: str | None = None,
               situacao_obra: str | None = None,
               cnpj_cpf_empresa: str | None = None) -> list[Obra]:
        try:
            stmt = select(Obra)
            if id_cidade:
                stmt = stmt.where(Obra.id_cidade == id_cidade)
            if entidade:
                stmt = stmt.where(Obra.entidade == entidade)
            if situacao_obra:
                stmt = stmt.where(Obra.situacao_obra == situacao_obra)
            if cnpj_cpf_empresa:
                stmt = stmt.where(Obra.cnpj_cpf_empresa == cnpj_cpf_empresa)

            resultados = self.session.execute(stmt).scalars().all()
            return list(resultados)
        except Exception as e:
            logger.error(f"Erro ao buscar obras: {e}")
            return []
