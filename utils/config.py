import json
from pathlib import Path

def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_config(path, config):
    with open(path, 'w') as f:
        json.dump(config, f)


def obter_caminho_arquivo(pasta: str, nome_arquivo: str) -> str:
    """
    Calcula o caminho absoluto seguro para qualquer arquivo do projeto,
    independentemente de onde o código for executado.
    """
    # 1. Path(__file__) aponta para utils/caminhos.py
    # 2. .parent aponta para a pasta 'utils'
    # 3. .parent.parent aponta para a RAIZ do seu projeto
    diretorio_raiz = Path(__file__).parent.parent

    # 4. Monta o caminho final unindo a raiz, a pasta solicitada e o arquivo
    caminho_final = diretorio_raiz / pasta / nome_arquivo

    # Retorna como string caso alguma biblioteca antiga exija
    return str(caminho_final)