from playwright.sync_api import sync_playwright
import glob
import pandas as pd

def agrupar_obras():
    # Pega todos os arquivos que começam com 'obras_' na pasta data
    arquivos = glob.glob(rf"D:\Projects\OpenCityMetrics\lab\corupa\data\obras/obras_*.csv")

    # Junta tudo num único DataFrame
    df_geral = pd.concat([pd.read_csv(f, sep=";", encoding='latin-1') for f in arquivos])

    return df_geral

def baixar_obras(ano_inicio, ano_fim):
    """
    Script que baixa todas as obras do portal da transparência
    Args:
        ano_inicio: ano inicial da obra
        ano_fim: ano final da obra

    Returns:

    """



    with sync_playwright() as p:
        # Abrimos o navegador visível
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Acessando o portal...")
        page.goto('https://corupa.atende.net/transparencia/item/obras#conteudo')

        # Para cada ano, baixamos o arquivo .csv
        for ano in range(ano_inicio, ano_fim + 1):
            page.wait_for_timeout(1000)
            ano = str(ano)
            print(f'Selecionando data - {ano}')
            page.locator("iframe[title=\"Item\"]").content_frame.get_by_label("Ano", exact=True).select_option(ano)


            print("Iniciando o download...")

            page.get_by_role("button", name="Dados Abertos").click()
            # O Playwright identifica o evento downloud
            with page.expect_download() as download_info:
                page.wait_for_timeout(1000)
                page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Confirmar").click()
                page.wait_for_timeout(1000)
                page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Fechar Janela").click()

            # Pega o arquivo que foi gerado
            download = download_info.value

            caminho_arquivo = rf"D:\Projects\OpenCityMetrics\lab/corupa/data/obras/obras_{ano}.csv"
            download.save_as(caminho_arquivo)

            print(f"Sucesso! Arquivo salvo como: {caminho_arquivo}")


        browser.close()


def adiciona_coluna_porcentagem_execucao():
    """
    Script que processa o arquivo .csv das obras e busca no portal o % pago da obra

    Ele realiza a busca para cada ano da tabela, além de verificar o número da obra, se o ano da linha for
    diferete do que está na seleção atual ele muda.
    Returns: pd.DataFrame

    """

    lista_porcentagens = []

    # Agrupamos os dfs baixados
    df = agrupar_obras()

    # criamos novas colunas e tratamos os dados
    df[['Numero da Obra', 'Ano']] = df['Número/Ano Obra'].str.split('/', expand=True)
    df['Ano'] = df['Ano'].str.strip()
    df['Numero da Obra'] = df['Numero da Obra'].str.strip()
    df['Numero da Obra'] = df['Numero da Obra'].astype(int)
    df['Ano'] = df['Ano'].astype(int)
    df = df.drop(columns=['Número/Ano Obra'])
    df = df.sort_values(by=['Ano'], ascending=True)

    ano_atual_no_site = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://corupa.atende.net/transparencia/item/obras#conteudo')

        frame = page.locator('iframe[title="Item"]').content_frame



        # Realizamos a busca no site, com um loop para ano e número da obra
        for ano_obra, numero_da_obra, entidade in zip(df['Ano'], df['Numero da Obra'], df['Entidade']):

            if ano_obra != ano_atual_no_site:
                page.wait_for_timeout(1000)
                print(f"Mudando filtro do portal para o ano: {ano_obra}")
                frame.get_by_label("Ano", exact=True).select_option(
                    str(ano_obra))
                ano_atual_no_site = ano_obra


            print(ano_obra, numero_da_obra, entidade)


            frame.locator("select[aria-label='Campo de Filtro'][aria-description='campo lista']").select_option(
                "numero")

            page.wait_for_timeout(1000)
            frame.get_by_role("textbox",name="Primeiro valor para o filtro").fill(str(numero_da_obra))
            frame.get_by_text("Consultar").click()

            page.wait_for_timeout(1000)


            linha_correta = frame.locator("table tbody tr").filter(has_text=entidade)
            linha_correta.get_by_title("Visualizar").first.click()

            page.wait_for_timeout(1000)

            frame.get_by_role("listitem", name="Execução").click()


            valor_extraido  = frame.get_by_role("textbox",name="% de execução financeira")
            valor_extraido.wait_for(state="visible")

            valor_extraido = valor_extraido.input_value()

            lista_porcentagens.append(valor_extraido)

            frame.get_by_role("button", name="Fechar Janela").click()

            page.wait_for_timeout(1000)

    df['% de execução financeira'] = lista_porcentagens

    return df


dados_obras = adiciona_coluna_porcentagem_execucao()
dados_obras.to_excel(r"D:\Projects\OpenCityMetrics\lab\corupa\data\obras\dados_obras_com_percent.xlsx")
