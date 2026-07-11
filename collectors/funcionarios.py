from playwright.sync_api import sync_playwright
from processors.limpar_dados import limpar_dados_brutos
import pandas as pd
import os
from playwright_stealth import Stealth
from time import sleep
import random

def gerar_lista_meses(mes_inicio:int, mes_fim:int, ano_inicio:int, ano_fim:int) -> list[str]:
    """
    Gera uma lista com base nos meses e anos informados no formato MM/AAAA.
    Args:
        mes_inicio: mês incial da busca de 1 a 12
        mes_fim: mês fianl da busca de 1 a 12
        ano_inicio: ano incial da busca
        ano_fim: ano final da busca

    Returns: Retorna uma lista com os meses e anos informados no formato MM/AAAA.

    """
    lista_meses = []

    while (ano_inicio < ano_fim) or (ano_inicio == ano_fim and mes_inicio <= mes_fim):
        lista_meses.append(f"{mes_inicio:02d}/{ano_inicio:02d}")

        mes_inicio += 1
        if mes_inicio > 12:
            mes_inicio = 1
            ano_inicio += 1

    return lista_meses



def baixar_dados(mes_inicio:int, mes_fim:int, ano_inicio:int, ano_fim:int, url:str) -> tuple[bool, pd.DataFrame, int]:
    """
    Função para coletar os dados dos funcionarios.

    O script faz o download dos dados dos funcionarios e salva-os em um arquivo CSV.
    Args:
        mes_inicio: mês inicial do filtro
        mes_fim: mês final do filtro
        ano_inicio: Ano inicial do filtro
        ano_fim: Ano final do filtro
        url: url do site

    Returns: True caso consiga realizar o processo e False caso contrário.

    """

    lista_dfs = []

    linhas_removidas = 0

    try:

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # Mantenha False até passarmos pelo bloqueio na sua máquina
                args=[
                    "--disable-blink-features=AutomationControlled",  # Desliga o letreiro "SOU UM ROBÔ" do Chrome
                    "--disable-infobars",  # Esconde aquela barra "O Chrome está sendo controlado por software..."
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            # 2. A CONFIGURAÇÃO DO CONTEXTO (A Identidade Humana)
            context = browser.new_context(
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )

            stealth = Stealth()
            stealth.apply_stealth_sync(context)

            page = context.new_page()

            page.set_default_timeout(60000)


            frame = page.locator('iframe[title="Item"]').content_frame

            print("Acessando o portal...")
            page.goto(url)

            sleep(random.uniform(4.5, 7.2))

            page.get_by_role("button", name="Rejeitar não necessários").click()


            for data in gerar_lista_meses(mes_inicio, mes_fim, ano_inicio, ano_fim):
                print(f'Selecioando a data: {data}')

                frame.get_by_label("Mês/Ano").select_option(label=data)

                print("Iniciando o download...")


                page.get_by_role("button", name="Dados Abertos").click()

                # O Playwright "escuta" o evento de download antes mesmo de você clicar
                with page.expect_download() as download_info:
                    with page.expect_popup() as page1_info:
                        frame.get_by_role("button", name="Confirmar").click()

                # Pega o arquivo que foi gerado
                download = download_info.value

                caminho_arquivo = rf"/data/funcionarios/salarios_funcionarios_corupa_{data.replace("/", "-")}.csv"
                download.save_as(caminho_arquivo)
                print(f"Sucesso! Arquivo salvo como: {caminho_arquivo}")
                df, linhas_ = limpar_dados_brutos(caminho_arquivo)
                df['data'] = f'01/{data}'
                lista_dfs.append(df)
                linhas_removidas += linhas_

                #Deleta o arquivo lido
                os.remove(caminho_arquivo)

            browser.close()

        df_agrupado = pd.concat(lista_dfs)

        print("Dados dos funcionarios salvos com sucesso!")
        return True, df_agrupado, linhas_removidas

    except Exception as e:
        print(f"Erro ao processar os dados dos funcionarios: {e}")
        return False, pd.DataFrame(), 0


url = 'https://corupa.atende.net/transparencia/item/relacao-funcionario-x-salario-liquido#conteudo'

SUCESSO, df, linhas = baixar_dados(1,5,2013,2026, url)

df.to_parquet(r'/data/funcionarios/salarios_funcionarios_corupa.parquet')