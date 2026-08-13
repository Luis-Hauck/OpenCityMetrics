import pandas as pd
import os
from dotenv import load_dotenv
import logging

from utils.config import obter_caminho_arquivo

load_dotenv()
logger = logging.getLogger(__name__)

token_hospedagem = os.getenv('TOKEN_HOSPEDAGEM')

from services.cloud_storage import fazer_upload

def processar_patrimonio(novo_df:pd.DataFrame, df_base: pd.DataFrame, token_hospedagem) -> bool:
    """
    Consolida e publica a base do patrimônio.

    Este processador recebe um DataFrame recém-coletado (novo_df) e um DataFrame
    base (df_base), concatena ambos, remove duplicidades com base na chave
    composta ['Entidade', 'Código', 'Valor Contábil'] (mantendo o registro mais
    recente), e salva o resultado em um
    arquivo .json local que é enviado para o armazenamento em nuvem.

    Observações importantes:
    - Em caso de duplicata, o registro mais novo (keep='last') prevalece.
    - Após o upload, o arquivo .json local é removido.

    Args:
        novo_df (pd.DataFrame): DataFrame com os novos registros de obras a
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

        # Apaga duplicatas, olhando APENAS para a chave composta
        # O parâmetro keep='last' garante que, se houver conflito, o dado que veio
        # do df_novo (o que acabou de ser baixado) vença e mate o dado velho.
        df_final = df_final.drop_duplicates(
            subset=['Unidade Gestora', 'Código', 'Valor Contábil'],
            keep='last')

        
        # Salva em JSON num caminho concreto e faz upload
        caminho_local = obter_caminho_arquivo('data/patrimonio', 'patrimonio_corupa.json')
        os.makedirs(os.path.dirname(caminho_local), exist_ok=True)
        df_final.to_json(caminho_local, orient='split', force_ascii=False, index=False, date_format='iso')
        sucesso = fazer_upload(
            arquivo=caminho_local,
            prefixo='json',
            expire=90,
            nome_arquivo='PatrimonioCorupa',
            content_type='application/json; charset=Latin1',
            token_hospedagem=token_hospedagem
        )

        if not sucesso:
            logger.warning("Falha ao fazer upload do arquivo JSON de patrimônio.")
            return False

        os.remove(caminho_local)

        logger.info("Dados do patrimônio salvos com sucesso!")

        return True
    except Exception as e:
        logger.error(f"Erro ao processar os dados dos patrimonio: {e}")
        return False

def tratar_dados(df) -> pd.DataFrame():
    """
    Trata o df.
    Args:
        df:

    Returns:

    """
    try:
        df["Código"] = pd.to_numeric(df["Código"], errors='coerce')

        df['Aquisição'] = pd.to_datetime(
            df['Aquisição'],
            format='%d/%m/%Y',
            dayfirst=True,
            errors='coerce',
        )
        df['Incorporação'] = pd.to_datetime(
            df['Incorporação'],
            format='%d/%m/%Y',
            dayfirst=True,
            errors='coerce',
        )

        df = df.dropna(subset=["Aquisição", "Código", "Incorporação"])

        df["Valor Contábil"] = df["Valor Contábil"].astype(float)

        df.rename(columns={'Unidade Gestora': 'Entidade'}, inplace=True)

        return df

    except Exception as e:
        logger.info(f"Erro ao tratar os dados: {e}")
        return pd.DataFrame()