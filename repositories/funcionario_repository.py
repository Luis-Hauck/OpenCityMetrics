from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import select, extract
from sqlalchemy.dialects.postgresql import insert
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
            dados_funcionarios : Objeto DadosFuncionario a ser salvo no banco de dados.

        Returns:
            bool: True se adicionou com sucesso; False caso ocorra um erro.

        """
        try:
            if not dados_funcionarios:
                logger.error("Dados de funcionários não fornecidos.")
                return False
            stmt = insert(Funcionario).values(dados_funcionarios)

            # index_elements: As colunas que formam a sua UniqueConstraint
            stmt = stmt.on_conflict_do_update(
                constraint='uix_cidade_funcionario',
                set_=dict( # set_: Quais campos devem ser atualizados se o registro já existir
                    cargo=stmt.excluded.cargo,
                    regime_trabalho=stmt.excluded.regime_trabalho, # stmt.excluded carrega os valores novos que estavam tentando entrar
                    proventos=stmt.excluded.proventos,

                )
            )
            self.session.execute(stmt, dados_funcionarios)
            self.session.flush()
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
