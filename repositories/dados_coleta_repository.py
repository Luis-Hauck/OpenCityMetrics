import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models.dados_coleta import RegistroColeta

logger = logging.getLogger(__name__)

class DadosColetaRepository:
    def __init__(self, session: Session):
        """
        Inicializa o repositório de Dados de Coleta com a sessão do banco de dados.
        """
        self.session = session

    def create(self, dados: dict) -> bool:
        """
        Cria um novo registro de coleta no banco de dados.

        Args:
            dados (dict): Dicionário contendo os dados de RegistroColeta.

        Returns:
            bool: True se adicionado com sucesso; False caso ocorra um erro.
        """
        try:
            if not dados:
                logger.error("Dados de coleta não fornecidos.")
                return False

            registro = RegistroColeta(**dados)
            self.session.add(registro)
            self.session.flush()
            logger.info("Registro de coleta salvo com sucesso.")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar registro de coleta: {e}")
            return False

    def search(self,
               id_cidade: int | None = None,
               software_portal: str | None = None,
               base_de_dados: str | None = None,
               formato_origem: str | None = None) -> list[RegistroColeta]:
        """
        Realiza a busca de registros de coleta utilizando filtros opcionais.

        Args:
            id_cidade (int, optional): Filtra pelo ID do IBGE da cidade.
            software_portal (str, optional): Filtra pelo software do portal.
            base_de_dados (str, optional): Filtra pelo nome da base de dados.
            formato_origem (str, optional): Filtra pelo formato de origem (ex: csv, json).

        Returns:
            list[RegistroColeta]: Lista de registros de coleta que satisfazem os filtros.
        """
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
