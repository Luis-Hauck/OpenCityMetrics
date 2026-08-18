import pandas as pd
import os
from dotenv import load_dotenv
import logging

from utils.config import obter_caminho_arquivo

load_dotenv()
logger = logging.getLogger(__name__)

token_hospedagem = os.getenv('TOKEN_HOSPEDAGEM')

from services.cloud_storage import fazer_upload

def processar_funcionarios(novo_df:pd.DataFrame, df_base: pd.DataFrame, token_hospedagem) -> bool:
    """
    Consolida e publica a base de salários de funcionários.

    Este processador recebe um DataFrame recém-coletado (novo_df) e um DataFrame
    base (df_base), concatena ambos, remove duplicidades com base na chave
    composta ['Funcionário', 'Cargo', 'Data'] (mantendo o registro mais
    recente), converte a coluna de datas para datetime e salva o resultado em um
    arquivo Parquet local que é enviado para o armazenamento em nuvem.

    Observações importantes:
    - Em caso de duplicata, o registro mais novo (keep='last') prevalece.
    - A conversão de datas espera o formato '%d-%m-%Y' e falha se houver
      valores inválidos (errors='raise').
    - Após o upload, o arquivo Parquet local é removido.

    Args:
        novo_df (pd.DataFrame): DataFrame com os novos registros de salários a
            serem integrados à base.
        df_base (pd.DataFrame): DataFrame existente que serve de base histórica
            para consolidação.
        token_hospedagem (str): Token/chave de autenticação para o serviço de
            hospedagem utilizado no upload.

    Returns:
        bool: True se todo o fluxo ocorrer com sucesso; False caso qualquer
            exceção seja capturada durante o processamento.

    """

    try:

        df_final = pd.concat([df_base, novo_df], ignore_index=True)

        # Apaga duplicatas, olhando APENAS para a chave composta (id_funcionario + cargo + data).
        # O parâmetro keep='last' garante que, se houver conflito, o dado que veio
        # do df_novo (o que acabou de ser baixado) vença e mate o dado velho.
        df_final = df_final.drop_duplicates(
            subset=['Funcionário', 'Cargo', 'data'],
            keep='last')

        df_final['data'] = pd.to_datetime(
            df_final['data'],
            dayfirst = True,
            errors = 'raise',
            )

        # Define o caminho do arquivo JSON local de forma robusta e garante que a pasta exista
        caminho_local = obter_caminho_arquivo('data/funcionarios','despesas_funcionarios_corupa.json')
        os.makedirs(os.path.dirname(caminho_local), exist_ok=True)

        # Salva o DataFrame em JSON usando o formato de data ISO para evitar warnings futuros
        df_final.to_json(caminho_local,
                         orient='split',
                         force_ascii=False,
                         index=False,
                         )

        # Faz o upload do arquivo salvo
        sucesso = fazer_upload(
            arquivo=caminho_local,
            prefixo='json',
            expire=90,
            nome_arquivo='DespesasFuncionariosCorupa',
            content_type='application/json; charset=Latin1',
            token_hospedagem=token_hospedagem
        )
        if not sucesso:
            logger.warning("Falha ao fazer upload do arquivo JSON.")
            return False
        # Remove o arquivo local após upload
        os.remove(caminho_local)

        logger.info("Dados dos funcionarios salvos com sucesso!")

        return True
    except Exception as e:
        logger.error(f"Erro ao processar os dados dos funcionarios: {e}")
        return False
