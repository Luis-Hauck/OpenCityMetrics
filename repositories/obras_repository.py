import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.obras import Obra

logger = logging.getLogger(__name__)

class ObrasRepository:
    def __init__(self, session: Session):
        """
        Inicializa o repositório de Obras com a sessão do banco de dados.
        """
        self.session = session

    def create_or_update(self, dados_obra: dict) -> bool:
        """
        Insere ou atualiza os dados de uma obra no banco de dados.
        Utiliza upsert baseado na chave única 'uix_cidade_obra' (id_cidade, entidade, numero_obra).

        Args:
            dados_obra (dict): Dicionário contendo os dados da Obra.

        Returns:
            bool: True se adicionou/atualizou com sucesso; False caso ocorra um erro.
        """
        try:
            if not dados_obra:
                logger.error("Dados da obra não fornecidos.")
                return False

            from sqlalchemy.dialects.postgresql import insert as pg_insert
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            dialect_name = self.session.bind.dialect.name

            if dialect_name == 'sqlite':
                stmt = sqlite_insert(Obra).values(dados_obra)
            else:
                stmt = pg_insert(Obra).values(dados_obra)

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
                # SQLite precisa referenciar as colunas do conflito
                # e elas precisam estar em uma restrição UNIQUE para on_conflict_do_update funcionar no SQLite (>= 3.24.0)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id_cidade', 'entidade', 'numero_obra'],
                    set_=update_dict
                )
            else:
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_cidade_obra',
                    set_=update_dict
                )

            self.session.execute(stmt)
            self.session.flush()

            # Necessário forçar expire/refresh se formos ler no mesmo teste usando SessionLocal sqlite pra atualizar a instancia no cache
            self.session.expire_all()

            logger.info("Dados da obra salvos/atualizados com sucesso!")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar os dados da obra: {e}")
            return False

    def search(self,
               id_cidade: int | None = None,
               entidade: str | None = None,
               situacao_obra: str | None = None,
               cnpj_cpf_empresa: str | None = None) -> list[Obra]:
        """
        Realiza a busca de obras utilizando filtros opcionais.

        Args:
            id_cidade (int, optional): Filtra pelo ID do IBGE da cidade.
            entidade (str, optional): Filtra pela entidade responsável.
            situacao_obra (str, optional): Filtra pela situação da obra.
            cnpj_cpf_empresa (str, optional): Filtra pelo CNPJ/CPF da empresa responsável.

        Returns:
            list[Obra]: Lista de obras que satisfazem os filtros.
        """
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
