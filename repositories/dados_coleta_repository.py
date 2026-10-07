import logging
from typing import Union
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models.dados_coleta import RegistroColeta

logger = logging.getLogger(__name__)

class DadosColetaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, dados: Union[dict, list[dict]]) -> bool:
        """
        Cria um ou vários novos registros de coleta no banco de dados.

        Args:
            dados: Dicionário ou Lista de Dicionários contendo os dados de RegistroColeta.

        Returns:
            bool: True se adicionado com sucesso; False caso ocorra um erro.
        """
        try:
            if not dados:
                logger.error("Dados de coleta não fornecidos.")
                return False

            if isinstance(dados, dict):
                dados = [dados]

            # Utiliza o bulk_insert_mappings de forma eficiente para uma lista de dicts
            self.session.bulk_insert_mappings(RegistroColeta, dados)
            self.session.flush()
            logger.info("Registros de coleta salvos com sucesso em lote.")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar registros de coleta em lote: {e}")
            return False

    def search(self,
               id_cidade: int | None = None,
               software_portal: str | None = None,
               base_de_dados: str | None = None,
               formato_origem: str | None = None) -> list[RegistroColeta]:
        try:
            stmt = select(RegistroColeta)
            if id_cidade:
                stmt = stmt.where(RegistroColeta.id_cidade == id_cidade)
            if software_portal:
                stmt = stmt.where(RegistroColeta.software_portal == software_portal)
            if base_de_dados:
                stmt = stmt.where(RegistroColeta.base_de_dados == base_de_dados)
            if formato_origem:
                stmt = stmt.where(RegistroColeta.formato_origem == formato_origem)

            resultados = self.session.execute(stmt).scalars().all()
            return list(resultados)
        except Exception as e:
            logger.error(f"Erro ao buscar registros de coleta: {e}")
            return []
