from datetime import datetime, date
from typing import Union

from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

from database.models.funcionario import Funcionario

logger = logging.getLogger(__name__)

class FuncionarioRepository:

    def __init__(self, session: Session):
        self.session = session

    def create_or_update(self, dados_funcionarios: Union[dict, list[dict]]) -> bool:
        """
        Recebe os dados da rotina de coleta (um dicionário ou uma lista deles).
        Insere os novos e atualiza os salários que sofreram alterações retroativas em lote (bulk).

        Args:
            dados_funcionarios : Dicionário ou Lista de Dicionários com os dados do(s) funcionário(s).

        Returns:
            bool: True se adicionou com sucesso; False caso ocorra um erro.
        """
        try:
            if not dados_funcionarios:
                logger.error("Dados de funcionários não fornecidos.")
                return False

            # Assegura que sempre seja tratado como lista para o bulk execute
            if isinstance(dados_funcionarios, dict):
                dados_funcionarios = [dados_funcionarios]

            from sqlalchemy.dialects.postgresql import insert as pg_insert
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            dialect_name = self.session.bind.dialect.name

            # Constroi o statement sem acoplar os valores
            if dialect_name == 'sqlite':
                stmt = sqlite_insert(Funcionario)
            else:
                stmt = pg_insert(Funcionario)

            update_dict = dict(
                cargo=stmt.excluded.cargo,
                regime_trabalho=stmt.excluded.regime_trabalho,
                proventos=stmt.excluded.proventos,
            )

            if dialect_name == 'sqlite':
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id_cidade', 'id_funcionario', 'data_referencia'],
                    set_=update_dict
                )
            else:
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_cidade_funcionario',
                    set_=update_dict
                )

            # Execute suporta lote (bulk) de dicionarios automaticamente
            self.session.execute(stmt, dados_funcionarios)
            self.session.flush()
            self.session.expire_all()

            logger.info(f"Dados dos servidores salvos com sucesso em lote!")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar os dados em lote: {e}")
            print(e)
            return False

    def search(self,
        id_cidade: int | None = None,
        cargo: str | None = None,
        nome: str | None = None,
        data_inicial: date | datetime | None = None,
        data_final: date | datetime | None = None,
    ) -> list[Funcionario]:
        try:
            smt = select(Funcionario)
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
            logger.error(f"Erro ao buscar informações: {e}")
            return []
