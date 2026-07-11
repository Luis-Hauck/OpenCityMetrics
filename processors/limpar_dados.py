import pandas as pd


def limpar_dados_brutos(caminho) -> tuple[pd.DataFrame, int]:
    """
    Limpa os dados brutos do arquivo CSV.
    Args:
        caminho_csv: caminho do arquivo CSV

    Returns: Retorna o dataframe do CSV lido com o número e elinhas removidas.

    """

    try:

        with open(caminho, 'r', encoding='Latin1') as arquivo:
            total_linhas_brutas = sum(1 for linha in arquivo) - 1

        df_limpo = pd.read_csv(caminho, sep=';', quotechar='"', encoding='Latin1', on_bad_lines='skip')

        total_linhas_ = len(df_limpo)

        linhas_removidas = total_linhas_brutas - total_linhas_

        print(f'{linhas_removidas} linhas foram removidas do DataFrame por dados corrompidos')
        return df_limpo, linhas_removidas

    except Exception as e:
        print(f'Erro ao limpar dados: {e}')
        return pd.DataFrame, 0