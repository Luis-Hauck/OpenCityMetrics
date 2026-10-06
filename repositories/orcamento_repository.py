import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.orcamento import Orcamento

logger = logging.getLogger(__name__)

class OrcamentoRepository:
    def __init__(self, session: Session):
        """
        Inicializa o repositório de Orçamento com a sessão do banco de dados.
        """
        self.session = session

    def create_or_update(self, dados_orcamento: dict) -> bool:
        """
        Insere ou atualiza os dados de um orçamento no banco de dados.
        Utiliza upsert baseado na chave única 'uix_cidade_orcamento'.

        Args:
            dados_orcamento (dict): Dicionário contendo os dados do Orçamento.

        Returns:
            bool: True se adicionou/atualizou com sucesso; False caso ocorra um erro.
        """
        try:
            if not dados_orcamento:
                logger.error("Dados do orçamento não fornecidos.")
                return False

            from sqlalchemy.dialects.postgresql import insert as pg_insert
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            dialect_name = self.session.bind.dialect.name

            if dialect_name == 'sqlite':
                stmt = sqlite_insert(Orcamento).values(dados_orcamento)
            else:
                stmt = pg_insert(Orcamento).values(dados_orcamento)

            update_dict = {
                'entidade': stmt.excluded.entidade,
                'orcamento_inicial': stmt.excluded.orcamento_inicial,
                'orcamento_atualizado': stmt.excluded.orcamento_atualizado,
                'empenhado_no_periodo': stmt.excluded.empenhado_no_periodo,
                'liquidado_no_periodo': stmt.excluded.liquidado_no_periodo,
                'pago_no_periodo': stmt.excluded.pago_no_periodo,
            }

            if dialect_name == 'sqlite':
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id_cidade', 'funcao', 'subfuncao', 'programa', 'acao', 'vinculo',
                                    'categoria_economica', 'grupo_despesa', 'modalidade', 'mes_referencia', 'ano_exercicio'],
                    set_=update_dict
                )
            else:
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_cidade_orcamento',
                    set_=update_dict
                )

            self.session.execute(stmt)
            self.session.flush()
            self.session.expire_all()

            logger.info("Dados do orçamento salvos/atualizados com sucesso!")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar os dados do orçamento: {e}")
            return False

    def search(self,
               id_cidade: int | None = None,
               ano_exercicio: str | None = None,
               mes_referencia: str | None = None,
               entidade: str | None = None,
               funcao: str | None = None) -> list[Orcamento]:
        """
        Realiza a busca de orçamentos utilizando filtros opcionais.

        Args:
            id_cidade (int, optional): Filtra pelo ID do IBGE da cidade.
            ano_exercicio (str, optional): Filtra pelo ano de exercício.
            mes_referencia (str, optional): Filtra pelo mês de referência.
            entidade (str, optional): Filtra pela entidade responsável.
            funcao (str, optional): Filtra pela função orçamentária.

        Returns:
            list[Orcamento]: Lista de orçamentos que satisfazem os filtros.
        """
        try:
            stmt = select(Orcamento)

            if id_cidade:
                stmt = stmt.where(Orcamento.id_cidade == id_cidade)

            if ano_exercicio:
                stmt = stmt.where(Orcamento.ano_exercicio == ano_exercicio)

            if mes_referencia:
                stmt = stmt.where(Orcamento.mes_referencia == mes_referencia)

            if entidade:
                stmt = stmt.where(Orcamento.entidade == entidade)

            if funcao:
                stmt = stmt.where(Orcamento.funcao == funcao)

            resultados = self.session.execute(stmt).scalars().all()
            return list(resultados)

        except Exception as e:
            logger.error(f"Erro ao buscar orçamentos: {e}")
            return []
