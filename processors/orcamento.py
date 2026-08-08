import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

token_hospedagem = os.getenv('TOKEN_HOSPEDAGEM')

from services.cloud_storage import fazer_upload

def processar_orcamento(novo_df:pd.DataFrame, df_base: pd.DataFrame, token_hospedagem) -> bool:
    """
    Consolida e publica a base dos orçamentos.

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
            subset=["Entidade","Função","Subfunção","Programa","Ação","Vínculo","Categoria Econômica","Grupo de Despesa","Modalidade","ano"],
            keep='last')


        caminho_local = df_final.to_json('data/orcamento/orcamento_corupa.json',orient='split', force_ascii=False, index=False)
        fazer_upload(
            arquivo=caminho_local,
            prefixo='json',
            expire=90,
            nome_arquivo='OrcamentoCorupa1.json',
            content_type='application/json; charset=Latin1',
            token_hospedagem=token_hospedagem
        )

        os.remove(caminho_local)

        print("Dados do orçamento salvos com sucesso!")

        return True
    except Exception as e:
        print(f"Erro ao processar os dados dos funcionarios: {e}")
        return False

def tratar_dados(df) -> pd.DataFrame():
    """
    Padroniza e trata o DataFrame de orçamento para consumo no dashboard.

    - Renomeia colunas para nomes padronizados.
    - Converte colunas numéricas para float.
    - Remove colunas auxiliares se existirem.
    """
    try:
        if df is None or len(df) == 0:
            return pd.DataFrame()

        # Renomeia colunas conhecidas para o padrão usado no dashboard
        mapeamento = {
            'ano': 'Ano',
            'Inicial': 'Orçamento Inicial',
            'Atualizado': 'Orçamento Atualizado',
            'Até o Mês.1': 'Liquidado Até o Mês',
        }
        # Apenas renomeia o que existir
        colunas_existentes = {k: v for k, v in mapeamento.items() if k in df.columns}
        if colunas_existentes:
            df = df.rename(columns=colunas_existentes)

        # Remove colunas não utilizadas, ignorando se não existirem
        df = df.drop(columns=["No Mês", "Até o Mês", "No Mês.1", "No Mês.2", "Até o Mês.2"], errors='ignore')

        return df

    except Exception as e:
        print(f"Erro ao tratar os dados do orçamento: {e}")
        return pd.DataFrame()