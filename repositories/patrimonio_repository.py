import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.patrimonio import Patrimonio

logger = logging.getLogger(__name__)

class PatrimonioRepository:
    def __init__(self, session: Session):
        """
        Inicializa o repositório de Patrimônio com a sessão do banco de dados.
        """
        self.session = session

    def create_or_update(self, dados_patrimonio: dict) -> bool:
        """
        Insere ou atualiza os dados de um patrimônio no banco de dados.
        Utiliza upsert baseado na chave única 'uix_cidade_patrimonio'.

        Args:
            dados_patrimonio (dict): Dicionário contendo os dados do Patrimônio.

        Returns:
            bool: True se adicionou/atualizou com sucesso; False caso ocorra um erro.
        """
        try:
            if not dados_patrimonio:
                logger.error("Dados do patrimônio não fornecidos.")
                return False

            from sqlalchemy.dialects.postgresql import insert as pg_insert
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            dialect_name = self.session.bind.dialect.name

            if dialect_name == 'sqlite':
                stmt = sqlite_insert(Patrimonio).values(dados_patrimonio)
            else:
                stmt = pg_insert(Patrimonio).values(dados_patrimonio)

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

            self.session.execute(stmt)
            self.session.flush()
            self.session.expire_all()

            logger.info("Dados do patrimônio salvos/atualizados com sucesso!")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar os dados do patrimônio: {e}")
            return False

    def search(self,
               id_cidade: int | None = None,
               entidade: str | None = None,
               tipo_patrimonio: str | None = None,
               status_patrimonio: str | None = None,
               codigo: str | None = None) -> list[Patrimonio]:
        """
        Realiza a busca de patrimônios utilizando filtros opcionais.

        Args:
            id_cidade (int, optional): Filtra pelo ID do IBGE da cidade.
            entidade (str, optional): Filtra pela entidade responsável.
            tipo_patrimonio (str, optional): Filtra pelo tipo de patrimônio.
            status_patrimonio (str, optional): Filtra pelo status do patrimônio.
            codigo (str, optional): Filtra pelo código do patrimônio.

        Returns:
            list[Patrimonio]: Lista de patrimônios que satisfazem os filtros.
        """
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
