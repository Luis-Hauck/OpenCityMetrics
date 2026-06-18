from playwright.sync_api import sync_playwright
import glob
import pandas as pd

def agrupar_diarias():
    # Pega todos os arquivos que começam com 'obras_' na pasta data
    arquivos = glob.glob(rf"D:\Projects\OpenCityMetrics\lab\corupa\data\gastos_com_diarias/gastos_com_diarias*.csv")

    # Junta tudo num único DataFrame
    df_geral = pd.concat([pd.read_csv(f, sep=";", encoding='latin-1') for f in arquivos])

    return df_geral


def baixar_gastos_com_diarias(ano_inicio, ano_fim):
    """
    Baixa as despesas com diárias com bas no interválo passado
    Args:
        ano_inicio:
        ano_fim:

    Returns:

    """
    with sync_playwright() as p:
        # Abrimos o navegador visível
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        frame = page.locator('iframe[title="Item"]').content_frame

        print("Acessando o portal...")
        page.goto('https://corupa.atende.net/transparencia/item/despesas-com-diarias#conteudo')


        for ano in range(ano_inicio, ano_fim + 1):
            frame.get_by_label("Ano").select_option(str(ano))

            page.wait_for_timeout(1000)

            frame.get_by_text("Consultar", exact=True).click()

            print("Iniciando o download...")

            page.get_by_role("button", name="Dados Abertos").click()

            # O Playwright "escuta" o evento de download antes de você clicar
            with page.expect_download() as download_info:
                with page.expect_popup() as page1_info:
                    frame.get_by_role("button",name="Confirmar").click()

            download = download_info.value

            caminho_arquivo = rf"D:\Projects\OpenCityMetrics\lab\corupa/data\gastos_com_diarias/gastos_com_diarias{ano}.csv"

            download.save_as(caminho_arquivo)


def detalhar_gastos_com_diarias(df):
    """

    Args:
        df:

    Returns:

    """

    lista_descricao_empenho = []

    df[['N_Empenho', 'Ano_Empenho']] = df['Empenho'].str.split('/', expand=True)
    df['Ano_Empenho'] = df['Ano_Empenho'].str.strip()
    df['N_Empenho'] = df['N_Empenho'].str.strip()

    ano_atual_no_site = None

    with sync_playwright() as p:
        # Abrimos o navegador visível
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        frame = page.locator('iframe[title="Item"]').content_frame

        print("Acessando o portal...")
        page.goto('https://corupa.atende.net/transparencia/item/despesas-com-diarias#conteudo')

        for n_empenho, ano_empenho in zip(df['N_Empenho'], df['Ano_Empenho']):
            print(f'Ano: {ano_empenho} - Empenho: {n_empenho}')

            if ano_empenho != ano_atual_no_site:
                page.wait_for_timeout(1000)
                print(f"Mudando filtro do portal para o ano: {ano_empenho}")
                frame.get_by_label("Ano").select_option(str(ano_empenho))

            ano_atual_no_site = ano_empenho


            frame.get_by_label("Campo de Filtro").select_option("empnro")
            frame.get_by_role("textbox",name="Primeiro valor para o filtro").fill(n_empenho)
            frame.get_by_text("Consultar", exact=True).click()
            frame.get_by_title("Detalhar").first.click()
            texto_extraido = frame.get_by_role("textbox", name="Histórico")
            texto_extraido.wait_for(state="visible")

            texto_extraido = texto_extraido.input_value()

            lista_descricao_empenho.append(texto_extraido)

            frame.get_by_role("button", name="Fechar Janela").click()

    df['Descrição do empenho'] = lista_descricao_empenho

    return df






# baixar_gastos_com_diarias(2017, 2023)
df = agrupar_diarias()
df = detalhar_gastos_com_diarias(df)
df.to_excel(r"D:\Projects\OpenCityMetrics\lab\corupa\data\gastos_com_diarias\dados_gastos_com_diarias.xlsx")

#page.locator("iframe[title=\"Item\"]").content_frame.locator("td").filter(has_text="1511 /").click()
# page.get_by_role("button", name=" Dados Abertos").click()
# with page.expect_download() as download_info:
#     with page.expect_popup() as page1_info:
#         page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Confirmar").click()
#     page1 = page1_info.value
# download = download_info.value
# page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Fechar Janela").click()
# page.locator("iframe[title=\"Item\"]").content_frame.get_by_label("Ano").select_option("2019")
# page.locator("iframe[title=\"Item\"]").content_frame.get_by_title("Detalhar").first.click()
# page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("textbox", name="Histórico").click()
# page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Fechar Janela").click()
