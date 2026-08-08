import pandas as pd
import csv


def limpar_dados_brutos(caminho, sep=';') -> tuple[pd.DataFrame, int]:
    """
    Limpa os dados brutos do arquivo CSV.
    Args:
        caminho_csv: caminho do arquivo CSV

    Returns: Retorna o dataframe do CSV lido com o número e elinhas removidas.

    """

    try:

        with open(caminho, 'r', encoding='Latin1') as arquivo:
            arquivo = csv.reader(arquivo, delimiter=sep)
            total_linhas_brutas = sum(1 for linha in arquivo if linha) - 1
            print(f'Total de linhas brutas: {total_linhas_brutas}')


        df_limpo = pd.read_csv(caminho, sep=sep, quotechar='"', encoding='Latin1', on_bad_lines='skip')

        total_linhas_ = len(df_limpo)

        linhas_removidas = total_linhas_brutas - total_linhas_
        print(f'Total de linhas limpas: {total_linhas_}')

        print(f'{linhas_removidas} linhas foram removidas do DataFrame por dados corrompidos')
        return df_limpo, linhas_removidas

    except Exception as e:
        print(f'Erro ao limpar dados: {e}')
        return pd.DataFrame, 0


def formatar_reais(valor:float) -> str:
    """

    Args:
        valor:

    Returns:

    """
    try:
        valor_formatado = (f'R$ {valor:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
        return valor_formatado
    except Exception as e:
        print(f'Erro ao formatar o valor: {e} ')
        return 'R$ 0,00'


