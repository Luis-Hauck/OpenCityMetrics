import requests
import pandas as pd
import io
import logging
import streamlit as st

logger = logging.getLogger(__name__)

def fazer_upload(nome_arquivo, prefixo, expire, arquivo, content_type, token_hospedagem) -> bool:
    """
    Sobe o arquivo para a nuvem.
    Args:
        nome_arquivo: nome do arquivo
        prefixo: prefixo do arquivo(ex: csv)
        expire: tempo em dias para expirar o arquivo
        arquivo: caminho do arquivo
        content_type: tipo do arquivo(ex: 'text/csv')
        token_hospedagem: api token da nuvem

    Returns: True caso consiga subir o arquivo na nuvem False caso contrário

    """
    nome_arquivo = nome_arquivo.replace('\\', '/').strip()
    prefixo = prefixo.replace('\\', '/').strip()

    try:
        with open(arquivo, 'rb') as f:
            response = requests.post(
                'https://blob.squarecloud.app/v1/objects',
                headers={'Authorization': token_hospedagem},
                params={'name': nome_arquivo, 'prefix': prefixo, 'expire': expire},
                files={'file': (nome_arquivo, f, content_type)},
            )

        data = response.json()

        status = data.get('status', 'error')

        if status != 'success':
            logging.error(f'Erro ao fazer upload para nuvem: {data.get("code", "Erro desconhecido")}')
            return False

        logging.info(f'Sucesso em fazer upload para nuvem')
        return True

    except Exception as e:
        print(f'Erro ao fazer upload para nuvem: {e}')
        return False

@st.cache_data(ttl=43200)
def obter_dados(url) -> (bool, pd.DataFrame):
    """Busca o JSON/Parquet consolidado do Blob e retorna o DataFrame pronto."""

    try:
        if not url:
            logger.error("URL vazia ao tentar obter dados.")
            return False, pd.DataFrame()

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        resp = requests.get(url, timeout=15)
        resp.raise_for_status()  # Força o erro ir para o "except" se for 404 (Não Encontrado)

        if resp.status_code == 200:
            json_data = io.StringIO(resp.text)
            return True, pd.read_json(json_data, orient='split')

    except requests.exceptions.RequestException as e:
        # Cai aqui se a URL estiver errada, site fora do ar, ou arquivo não existir (404)
        logger.error(f"Falha de conexão ou arquivo não encontrado: {e}")
        return False, pd.DataFrame()

    except ValueError as e:
        # Cai aqui se o arquivo baixou, mas não era um JSON válido
        logger.error(f"O arquivo baixado não é um JSON válido: {e}")
        return False, pd.DataFrame()

    except Exception as e:
        # Segurança máxima contra falhas bizarras
        logger.error(f"Erro inesperado no obter_dados: {e}")
        return False, pd.DataFrame()
