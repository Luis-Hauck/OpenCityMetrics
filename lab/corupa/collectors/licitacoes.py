from playwright.sync_api import sync_playwright
import pandas as pd
import io
import os

def baixar_licitacoes(ano_inicio=2026, ano_fim=2026):
    with sync_playwright() as p:
        # Abrimos o navegador visível
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Acessando o portal...")
        page.goto('https://corupa.atende.net/transparencia/item/licitacoes-gerais#conteudo')

        frame = page.locator('iframe[title="Item"]').content_frame


        for ano in range(ano_inicio, ano_fim + 1):
            frame.get_by_label("Ano Licitação").click()
            frame.get_by_role("checkbox", name=str(ano)).check()

        frame.get_by_text("Consultar", exact=True).click()
        page.wait_for_timeout(3000)

        page.get_by_role("button", name=" Dados Abertos").click()

        with page.expect_download() as download_info:
            frame.get_by_role("button", name="Confirmar").click()
            frame.get_by_role("button", name="Fechar Janela").click()

        # Pega o arquivo que foi gerado
        download = download_info.value

        caminho_arquivo = rf"D:\Projects\OpenCityMetrics\lab\corupa\data\licitacoes/licitacoes.csv"
        download.save_as(caminho_arquivo)

        return caminho_arquivo

def ler_licitacao_vencedora(path_licitacao):

    df = pd.read_csv(path_licitacao, sep=';', quotechar='"', encoding='Latin1')

    print(df)

    df_agrupado = df.groupby(['Fornecedor - Cód.', 'Fornecedor - CPF/CNPJ','Fornecedor - Nome/Razão' ])['Vlr Total'].sum().reset_index()

    df_agrupado.rename(columns={'Vlr Total': 'Valor total', 'Fornecedor - CPF/CNPJ':'CPF/CNPJ', 'Fornecedor - Nome/Razão': 'Vencedor da licitação' }, inplace=True)

    print(df_agrupado)

    return df_agrupado

def adcionar_vencedor_licitacao(ano_inicio=2026, ano_fim=2026):


    licitacoes = baixar_licitacoes(ano_inicio, ano_fim)

    with open(licitacoes, 'r', encoding='Latin1') as arquivo:
        total_linhas_brutas = sum(1 for linha in arquivo) - 1

    df_licitacoes = pd.read_csv(licitacoes, sep=';', quotechar='"', encoding='Latin1', on_bad_lines='skip')

    print(df_licitacoes)
    df_licitacoes = df_licitacoes.dropna(subset=['Número','Registro'])

    total_linhas_ = len(df_licitacoes)

    print(f'{total_linhas_brutas - total_linhas_} Licitações foram removidas por falta de dados ou dados corrompidos')

    caminho_backup = r"D:\Projects\OpenCityMetrics\lab\corupa\data\licitacoes\backup_vencedores.csv"
    registros_ja_feitos = []


    if os.path.exists(caminho_backup):
        df_backup = pd.read_csv(caminho_backup)
        registros_ja_feitos = df_backup['Registro'].unique().tolist()
        print(f"Retomando trabalho: {len(registros_ja_feitos)} licitações já foram raspadas anteriormente.")


    with sync_playwright() as p:
        # Abrimos o navegador visível
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Acessando o portal...")
        page.goto('https://corupa.atende.net/transparencia/item/licitacoes-gerais#conteudo')

        frame = page.locator('iframe[title=\"Item\"]').content_frame

        for ano in range(ano_inicio, ano_fim + 1):
            frame.get_by_label("Ano Licitação").click()
            frame.get_by_role("checkbox", name=str(ano)).check()

        for registro in df_licitacoes['Registro']:
            if registro in registros_ja_feitos:
                pass
            frame.get_by_label("Campo de Filtro").select_option("codigo_registro")
            frame.get_by_role("textbox", name="Primeiro valor para o filtro").click()
            frame.get_by_role("textbox", name="Primeiro valor para o filtro").fill(registro)
            frame.get_by_text("Consultar", exact=True).click()
            page.wait_for_timeout(2000)
            frame.get_by_title("Detalhar").click()
            frame.get_by_text("Vencedores").click()
            page.wait_for_timeout(3000)
            frame.get_by_label("Assistente - Profundidade").get_by_role( "button", name="Imprimir/Exportar Consulta (").click()
            frame.get_by_label("Formato").select_option("csv")
            frame.get_by_role("button", name="Confirmar").click()
            with page.expect_download() as download_info:
                with page.expect_popup() as page1_info:
                    page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Sim").click()
                page1 = page1_info.value
            download = download_info.value

            caminho_arquivo = rf"D:\Projects\OpenCityMetrics\lab\corupa\data\licitacoes/licitacao_vencedora.csv"
            download.save_as(caminho_arquivo)

            df_temp = ler_licitacao_vencedora(caminho_arquivo)

            df_temp['Registro'] = registro

            # O mode='a' significa "Append" (Adicionar ao final do arquivo sem apagar o que tem lá)
            # O header garante que o cabeçalho só seja escrito na primeira vez
            df_temp.to_csv(caminho_backup, mode='a', index=False, header=not os.path.exists(caminho_backup))

            frame.get_by_role("button", name="Fechar Janela").click()
            page.wait_for_timeout(2000)

    df_todos_vencedores = pd.read_csv(caminho_backup)

    df_banco_de_dados = pd.merge(df_todos_vencedores, df_licitacoes, on='Registro', how='inner')

    print(df_banco_de_dados)
    df_banco_de_dados.to_excel(r"D:\Projects\OpenCityMetrics\lab\corupa\data\licitacoes\dados_licitacoes.xlsx", index=False)



adcionar_vencedor_licitacao(2026,2026)


"""def test_example(page: Page) -> None:
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_label("Ano Licitação").click()
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("checkbox", name="2026").uncheck()
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_text("Consultar", exact=True).click()
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_title("Detalhar").first.click()

    page.locator("iframe[title=\"Item\"]").content_frame.get_by_label("Campo de Filtro").select_option("codigo_registro")
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("textbox", name="Primeiro valor para o filtro").click()
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("textbox", name="Primeiro valor para o filtro").fill("E0B9EE593CDCED87912793A0CF9A027A5742BC16")
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_text("Consultar").click()
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_title("Detalhar").click()
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_text("Vencedores").click()
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Fechar Janela").click()
    
     page.locator("iframe[title=\"Item\"]").content_frame.get_by_label("Assistente - Profundidade").get_by_role("button", name="Imprimir/Exportar Consulta (").click()
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_label("Formato").select_option("csv")
    page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Confirmar").click()
    with page.expect_download() as download_info:
        with page.expect_popup() as page1_info:
            page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Sim").click()
        page1 = page1_info.value
    download = download_info.value
"""