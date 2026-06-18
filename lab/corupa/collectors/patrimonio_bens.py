from playwright.sync_api import sync_playwright
import pandas as pd

def agrupar_patrimonio_bens():
    with sync_playwright() as p:
        # Abrimos o navegador visível
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Acessando o portal...")
        page.goto('https://corupa.atende.net/transparencia/item/bens#conteudo')

        frame = page.locator('iframe[title="Item"]').content_frame

        # Identificamos todas checkboxes
        frame.get_by_label("Ano da Aquisição").click()
        frame.get_by_role("checkbox", name="2026").uncheck()

        frame.get_by_text("Consultar", exact=True).click()
        page.wait_for_timeout(1000)

        page.get_by_role("button", name=" Dados Abertos").click()

        with page.expect_download() as download_info:
            frame.get_by_role("button", name="Confirmar").click()
            frame.get_by_role("button", name="Fechar Janela").click()

        # Pega o arquivo que foi gerado
        download = download_info.value

        caminho_arquivo = rf"D:\Projects\OpenCityMetrics\lab\corupa\data\patrimonio_bens/patrimonio_bens.csv"
        download.save_as(caminho_arquivo)

        df = pd.read_csv(caminho_arquivo)
        df.to_excel(r"D:\Projects\OpenCityMetrics\lab\corupa\data\patrimonio_bens\dados_patrimonio_bens.xlsx", index=False)


agrupar_patrimonio_bens()