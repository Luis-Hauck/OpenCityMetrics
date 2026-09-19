from sqlalchemy.orm import Session
import logging

from database.models.cidade import Cidade


logger = logging.getLogger(__name__)

class CidadeRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(self, cidade: Cidade) -> bool:
        """
        Cria um novo objeto Cidade no banco de dados.
        Args:
            cidade (Cidade): Objeto Cidade a ser salvo no banco de dados.

        Returns:
            bool: True se adicionou com sucesso; False caso ocorra um erro.

        """
        try:
            self.session.add(cidade)
            self.session.flush()
            logger.info(f"Cidade salva com sucesso: {cidade.nome}")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar cidade: {e}")
            print(e)
            return False

    def get_by_id(self, id_ibge: int) -> type[Cidade] | None:
        """
        Busca os dados da cidade pelomid do IBGE
        Args:
            id_ibge (int): Identificação do IBGE da cidade

        Returns:
            Cidade | None: Cidade se encontrado, None se não encontrado ou em caso de erro.

        """
        try:
            dados_cidade = self.session.get(Cidade, id_ibge)

            if not dados_cidade:
                logger.warning(f'Dados da cidade com código do IBGE: {id_ibge} não encontrados.')
                return None

            logger.info(f"Dados da cidade: {dados_cidade.nome}")
            return dados_cidade

        except Exception as e:
            logger.error(f"Erro ao obter dados da cidade com código do IBGE: {id_ibge}: {e}")
            return None

    def update(self, id_ibge:int, **kwargs) -> bool:
        """
        Atualiza os dados da cidade
        Args:
            id_ibge (int): Identificação do IBGE da cidade

        Returns:
            bool: True se atualizou com sucesso; False caso ocorra um erro.

        """

        try:
            cidade_existente  = self.session.get(Cidade, id_ibge)

            if not cidade_existente:
                logger.warning('Não foi possível encontrar a cidade selecioanda para atualizar os dados')
                return False
            for key, value in kwargs.items():
                setattr(cidade_existente, key, value)

            self.session.flush()
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar os dados da cidade: {e}")
            return False
