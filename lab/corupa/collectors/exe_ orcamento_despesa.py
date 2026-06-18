from playwright.sync_api import sync_playwright
from datetime import datetime
import pandas as pd

def processar_orc_das_despesas(ano_inicio, ano_fim):
    with sync_playwright() as p:
        # Abrimos o navegador visível
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Acessando o portal...")
        page.goto('https://corupa.atende.net/transparencia/item/execucao-do-orcamento-da-despesa#conteudo')

        lista_df = []


        for ano in range(ano_inicio, ano_fim + 1):
            mes  = 12

            frame = page.locator("iframe[title=\"Item\"]").content_frame

            if ano == datetime.now().year:
                mes = datetime.now().month
                mes = str(mes).zfill(2)
            print(mes)
            frame.get_by_label("Ano").select_option(str(ano))
            page.wait_for_timeout(1000)
            frame.get_by_label("Mês", exact=True).select_option(str(mes))
            frame.get_by_text("Consultar").click()
            page.get_by_role("button", name=" Dados Abertos").click()

            with page.expect_download() as download_info:
                with page.expect_popup() as page1_info:
                    frame.get_by_role("button", name="Confirmar").click()
                page1 = page1_info.value

            download = download_info.value

            caminho_arquivo = rf"D:\Projects\OpenCityMetrics\lab\corupa/data\orcamento-despesas/orcamento_despesas{ano}.csv"

            download.save_as(caminho_arquivo)

            df = pd.read_csv(caminho_arquivo, sep=';', quotechar='"', encoding='Latin1')
            df['ano'] = ano

            lista_df.append(df)



            frame.get_by_role("button", name="Fechar Janela").click()

        df_agrupado = pd.concat(lista_df)

        df_agrupado.to_csv(rf"D:\Projects\OpenCityMetrics\lab\corupa/data\orcamento-despesas/orcamento_despesas_{ano_inicio}_{ano_fim}.csv")

processar_orc_das_despesas(2024, 2026)



"""
 page.get_by_role("button", name="Rejeitar não necessários").click()
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_label("Ano").select_option("2025")
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_label("Mês", exact=True).select_option("12")
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_text("Consultar").click()
    page.get_by_role("button", name=" Dados Abertos").click()
    with page.expect_download() as download_info:
        with page.expect_popup() as page1_info:
            page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Confirmar").click()
        page1 = page1_info.value
    download = download_info.value
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Fechar Janela").click()
"""