import requests
import pandas as pd
import io


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

    try:
        with open(arquivo, 'rb') as f:
            response = requests.post(
                'https://blob.squarecloud.app/v1/objects',
                headers={'Authorization': token_hospedagem},
                params={'name': nome_arquivo, 'prefix': prefixo, 'expire': expire},
                files={'file': ('dados.json', f, content_type)},
            )

        data = response.json()

        status = data.get('status', 'error')

        if status != 'success':
            print(f'Erro ao fazer upload para nuvem: {data.get("code", "Erro desconhecido")}')
            return False

        print(f'Sucesso em fazer upload para nuvem')
        return True

    except Exception as e:
        print(f'Erro ao fazer upload para nuvem: {e}')
        return False


def obter_dados(url) -> (bool, pd.DataFrame):
    """Busca o JSON/Parquet consolidado do Blob e retorna o DataFrame pronto."""
    resp = requests.get(url)
    resp.raise_for_status()

    if resp.status_code == 200:
        json = io.StringIO(resp.text)
        return True, pd.read_json(json, orient='split')
    else:
        print(f"Erro ao baixar da Square Cloud. Código HTTP: {resp.status_code}")
        print("Verifique se a URL está correta ou se o arquivo é público.")
        return False, pd.DataFrame()
