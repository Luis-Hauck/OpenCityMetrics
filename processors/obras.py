import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

token_hospedagem = os.getenv('TOKEN_HOSPEDAGEM')

from services.cloud_storage import fazer_upload

def processar_obras(novo_df:pd.DataFrame, df_base: pd.DataFrame, token_hospedagem) -> bool:
    """
    Consolida e publica a base de obras.

    Este processador recebe um DataFrame recém-coletado (novo_df) e um DataFrame
    base (df_base), concatena ambos, remove duplicidades com base na chave
    composta ['Entidade', 'CPF/CNPJ', 'Numero da Obra', 'Ano'] (mantendo o registro mais
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
            subset=['Entidade', 'CPF/CNPJ', 'Numero da Obra', 'Ano'],
            keep='last')


        caminho_local = df_final.to_json('data/obras/obras_corupa.json',orient='split', force_ascii=False, index=False)
        fazer_upload(
            arquivo=caminho_local,
            prefixo='json',
            expire=90,
            nome_arquivo='ObrasCorupa.json',
            content_type='json',
            token_hospedagem=token_hospedagem
        )

        os.remove(caminho_local)

        print("Dados dos funcionarios salvos com sucesso!")

        return True
    except Exception as e:
        print(f"Erro ao processar os dados dos funcionarios: {e}")
        return False

def limpar_dados(df_obras) -> pd.DataFrame():
    """
    Trata o df.
    Args:
        df_obras: 

    Returns:

    """
    df_obras["Percentual Conclusão (%)"] = df_obras["Percentual Conclusão (%)"].str.replace(',', '.').astype(float)
    df_obras["% de execução financeira"] = df_obras["% de execução financeira"].str.replace(',', '.').astype(float)
    return df_obras