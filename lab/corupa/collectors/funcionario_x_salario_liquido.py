from playwright.sync_api import sync_playwright

def gerar_lista_meses(mes_inicio, mes_fim, ano_inicio, ano_fim):
    """
    Gera uma lista com base nos meses e anos informados.
    Args:
        mes_inicio:
        mes_fim:
        ano_inicio:
        ano_fim:

    Returns:

    """
    lista_meses = []

    while (ano_inicio < ano_fim) or (ano_inicio == ano_fim and mes_inicio <= mes_fim):
        lista_meses.append(f"{mes_inicio:02d}/{ano_inicio:02d}")

        mes_inicio += 1
        if mes_inicio > 12:
            mes_inicio = 1
            ano_inicio += 1
    print(lista_meses)
    return lista_meses



def baixar_dados_abertos(mes_inicio, mes_fim, ano_inicio, ano_fim):
    """

    Args:
        data_inicial:
        data_final:

    Returns:

    """

    with sync_playwright() as p:
        # Abrimos o navegador visível para você ver a mágica (e resolver o Captcha se precisar)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Acessando o portal...")
        page.goto('https://corupa.atende.net/transparencia/item/relacao-funcionario-x-salario-liquido#conteudo')

        for data in gerar_lista_meses(mes_inicio, mes_fim, ano_inicio, ano_fim):
            print(f'SelecioNANDO DATA- {data}')

            page.locator("iframe[title=\"Item\"]").content_frame.get_by_label("Mês/Ano").select_option(label=data)



            print("Iniciando o download...")

            page.get_by_role("button", name="Dados Abertos").click()

            # O Playwright "escuta" o evento de download antes mesmo de você clicar
            with page.expect_download() as download_info:
                with page.expect_popup() as page1_info:
                    page.locator("iframe[title=\"Item\"]").content_frame.get_by_role("button", name="Confirmar").click()


            # Pega o arquivo que foi gerado
            download = download_info.value


            caminho_arquivo = rf"D:\Projects\OpenCityMetrics\lab\corupa/data\funcionarioXsalario_liquido/dados_corupa_{data.replace("/", "-")}.csv"
            download.save_as(caminho_arquivo)

            print(f"Sucesso! Arquivo salvo como: {caminho_arquivo}")



        browser.close()




# Executa a função
baixar_dados_abertos(1,3,2025,2026)