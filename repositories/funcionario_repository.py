from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

from database.models.funcionario import Funcionario


logger = logging.getLogger(__name__)

class FuncionarioRepository:

    def __init__(self, session: Session):
        self.session = session

    def create_or_update(self, dados_funcionarios:dict) -> bool:
        """
        Recebe o DataFrame com os dados da rotina de coleta.
        Insere os novos e atualiza os salários que sofreram alterações retroativas.
        Args:
            dados_funcionarios : Dicionário com os dados do funcionário a ser salvo no banco de dados.

        Returns:
            bool: True se adicionou com sucesso; False caso ocorra um erro.

        """
        try:
            if not dados_funcionarios:
                logger.error("Dados de funcionários não fornecidos.")
                return False

            from sqlalchemy.dialects.postgresql import insert as pg_insert
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            dialect_name = self.session.bind.dialect.name

            if dialect_name == 'sqlite':
                stmt = sqlite_insert(Funcionario).values(dados_funcionarios)
            else:
                stmt = pg_insert(Funcionario).values(dados_funcionarios)

            update_dict = dict(
                cargo=stmt.excluded.cargo,
                regime_trabalho=stmt.excluded.regime_trabalho,
                proventos=stmt.excluded.proventos,
            )

            if dialect_name == 'sqlite':
                # No sqlite usamos os campos que compõem a unique constraint
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id_cidade', 'id_funcionario', 'data_referencia'],
                    set_=update_dict
                )
            else:
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_cidade_funcionario',
                    set_=update_dict
                )

            self.session.execute(stmt)
            self.session.flush()
            self.session.expire_all()

            logger.info(f"Dados dos servidores salvos com sucesso!")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar os dados: {e}")
            print(e)
            return False

    def search(self,
        id_cidade: int | None = None,
        cargo: str | None = None,
        nome: str | None = None,
        data_inicial: date | datetime | None = None,
        data_final: date | datetime | None = None,
    ) -> list[Funcionario]:
        """

        Args:
            id_cidade:
            cargo:
            nome:
            data_inicial:
            data_final:

        Returns:
            Lista de Funcionários baseada nos filtros
        """
        try:
            smt = select(Funcionario)

            # Empilhamos os filtros
            if id_cidade:
                smt = smt.where(Funcionario.id_cidade == id_cidade)

            if nome:
                smt = smt.where(Funcionario.nome == nome)

            if data_inicial:
                smt = smt.where(Funcionario.data_referencia >= data_inicial)

            if data_final:
                smt = smt.where(Funcionario.data_referencia <= data_final)

            if cargo:
                smt = smt.where(Funcionario.cargo == cargo)

            resultado = self.session.execute(smt).scalars().all()

            return list(resultado)

        except Exception as e:
            logger.error(f"Erro ao ao buscar as informações para consulta realizada: {e}")
            return []
