import logging
from typing import Union
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.patrimonio import Patrimonio

logger = logging.getLogger(__name__)

class PatrimonioRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_or_update(self, dados_patrimonio: Union[dict, list[dict]]) -> bool:
        """
        Insere ou atualiza os dados de um ou vários patrimônios no banco de dados.
        Suporta envio em lote (bulk_upsert) através de uma lista de dicionários.

        Args:
            dados_patrimonio: Dicionário ou Lista de Dicionários com os dados do Patrimônio.

        Returns:
            bool: True se adicionou/atualizou com sucesso; False caso ocorra um erro.
        """
        try:
            if not dados_patrimonio:
                logger.error("Dados do patrimônio não fornecidos.")
                return False

            if isinstance(dados_patrimonio, dict):
                dados_patrimonio = [dados_patrimonio]

            from sqlalchemy.dialects.postgresql import insert as pg_insert
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            dialect_name = self.session.bind.dialect.name

            if dialect_name == 'sqlite':
                stmt = sqlite_insert(Patrimonio)
            else:
                stmt = pg_insert(Patrimonio)

            update_dict = {
                'tipo_patrimonio': stmt.excluded.tipo_patrimonio,
                'descricao': stmt.excluded.descricao,
                'num_tombamento': stmt.excluded.num_tombamento,
                'data_aquisicao': stmt.excluded.data_aquisicao,
                'data_incorporacao': stmt.excluded.data_incorporacao,
                'status_patrimonio': stmt.excluded.status_patrimonio,
                'centro_custo': stmt.excluded.centro_custo,
                'fornecedor': stmt.excluded.fornecedor,
                'valor_contabil': stmt.excluded.valor_contabil,
                'sit_aquisicao': stmt.excluded.sit_aquisicao,
            }

            if dialect_name == 'sqlite':
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id_cidade', 'entidade', 'codigo'],
                    set_=update_dict
                )
            else:
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_cidade_patrimonio',
                    set_=update_dict
                )

            self.session.execute(stmt, dados_patrimonio)
            self.session.flush()
            self.session.expire_all()

            logger.info("Dados do patrimônio salvos/atualizados com sucesso em lote!")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar os dados do patrimônio em lote: {e}")
            return False

    def search(self,
               id_cidade: int | None = None,
               entidade: str | None = None,
               tipo_patrimonio: str | None = None,
               status_patrimonio: str | None = None,
               codigo: str | None = None) -> list[Patrimonio]:
        try:
            stmt = select(Patrimonio)
            if id_cidade:
                stmt = stmt.where(Patrimonio.id_cidade == id_cidade)
            if entidade:
                stmt = stmt.where(Patrimonio.entidade == entidade)
            if tipo_patrimonio:
                stmt = stmt.where(Patrimonio.tipo_patrimonio == tipo_patrimonio)
            if status_patrimonio:
                stmt = stmt.where(Patrimonio.status_patrimonio == status_patrimonio)
            if codigo:
                stmt = stmt.where(Patrimonio.codigo == codigo)

            resultados = self.session.execute(stmt).scalars().all()
            return list(resultados)
        except Exception as e:
            logger.error(f"Erro ao buscar patrimônios: {e}")
            return []
