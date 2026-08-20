from datetime import datetime

from playwright.sync_api import sync_playwright
import pandas as pd
import os
from playwright_stealth import Stealth
from time import sleep
import random
import logging

from utils.config import obter_caminho_arquivo
from processors.limpar_dados import limpar_dados_brutos
from processors.obras import limpar_dados

logger = logging.getLogger(__name__)

def baixar_dados_obras(ano_inicio: int, ano_fim: int, url: str) -> tuple[bool, pd.DataFrame, int]:
    """
    Baixa os dados de obras do portal no intervalo de anos informado e retorna um DataFrame consolidado
    já enriquecido com a coluna "% de execução financeira" (segunda etapa de coleta).

    A rotina incorpora atrasos aleatórios e contexto stealth para reduzir riscos de bloqueios.

    Args:
        ano_inicio: Ano inicial do filtro (inclusive)
        ano_fim: Ano final do filtro (inclusive)
        url: URL da página de obras no portal

    Returns:
        (sucesso: bool, df: pd.DataFrame, linhas_removidas: int)
    """
    lista_dfs: list[pd.DataFrame] = []
    linhas_removidas = 0

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            context = browser.new_context(locale="pt-BR",
                                          timezone_id="America/Sao_Paulo",
                                          )
            stealth = Stealth()
            stealth.apply_stealth_sync(context)
            page = context.new_page()
            page.set_default_timeout(60000)

            logger.info("Acessando o portal de obras...")
            page.goto(url)
            sleep(random.uniform(3.0, 7.0))

            # Tenta rejeitar cookies se existir o botão
            try:
                page.get_by_role("button", name="Rejeitar não necessários").click()
            except Exception:
                pass

            frame = page.locator('iframe[title="Item"]').content_frame
            sleep(random.uniform(1, 4))
            # ETAPA 1
            #  baixar CSVs por ano
            for ano in range(ano_inicio, ano_fim + 1):
                logger.info(f"Selecionando o ano: {ano}")
                frame.get_by_label("Ano", exact=True).select_option(str(ano))
                sleep(random.uniform(0.6, 2))

                logger.info("Iniciando o download de Dados Abertos...")
                page.get_by_role("button", name="Dados Abertos").click()

                with page.expect_download() as download_info:
                    with page.expect_popup():
                        frame.get_by_role("button", name="Confirmar").click()
                download = download_info.value

                page.pause()

                caminho_arquivo = obter_caminho_arquivo('data/obras', f'obras_{ano}.csv')
                os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
                download.save_as(caminho_arquivo)
                download.save_as(caminho_arquivo)
                logger.info(f"Sucesso! Arquivo salvo como: {caminho_arquivo}")

                # Lê e limpa o CSV baixado (padrão AtendeNet é ; e Latin1)
                df, linhas_ = limpar_dados_brutos(caminho_arquivo)
                df = limpar_dados(df)
                lista_dfs.append(df)
                linhas_removidas += linhas_

                # Remove arquivo temporário
                try:
                    os.remove(caminho_arquivo)
                except Exception:
                    pass

                sleep(random.uniform(0.5, 1.5))

            # Se nada foi baixado, aborta
            if not lista_dfs:
                browser.close()
                return False, pd.DataFrame(), 0

            # Consolida os CSVs
            df_agrupado = pd.concat(lista_dfs, ignore_index=True)

            try:
                frame.get_by_role("button", name="Fechar Janela", exact=True).click()
            except Exception:
                pass

            # ETAPA 2

            # busca o "% de execução financeira" por obra, como no coletor do lab
            # Prepara colunas de apoio a partir de "Número/Ano Obra"
            if 'Número/Ano Obra' in df_agrupado.columns:
                partes = df_agrupado['Número/Ano Obra'].astype(str).str.split('/', n=1, expand=True)
                df_agrupado['Numero da Obra'] = partes[0].str.strip()
                df_agrupado['Ano'] = partes[1].str.strip()
            else:
                # Se não existir, tenta colunas já separadas; se ainda assim não tiver, não há como prosseguir a etapa 2
                if not ({'Numero da Obra', 'Ano'} <= set(df_agrupado.columns)):
                    logger.info('Coluna "Número/Ano Obra" não encontrada e não há colunas de apoio; pulando etapa de execução financeira.')
                    browser.close()
                    logger.info("Dados de obras coletados com sucesso!")
                    return True, df_agrupado, linhas_removidas

            # Tipagens seguras
            df_agrupado['Numero da Obra'] = pd.to_numeric(df_agrupado['Numero da Obra'], errors='coerce').astype('Int64')
            df_agrupado['Ano'] = pd.to_numeric(df_agrupado['Ano'], errors='coerce').astype('Int64')

            # Ordena para minimizar trocas de ano no portal
            df_agrupado = df_agrupado.sort_values(by=['Ano', 'Entidade', 'Numero da Obra']).reset_index(drop=True)

            lista_porcentagens: list[str] = []
            ano_atual_no_site = None


            for ano_obra, numero_da_obra, entidade in zip(
                df_agrupado['Ano'],
                df_agrupado['Numero da Obra'],
                df_agrupado['Entidade'],
            ):
                # Valores inválidos não são buscados
                if pd.isna(ano_obra) or pd.isna(numero_da_obra):
                    lista_porcentagens.append(None)
                    continue

                # Troca o ano no filtro quando necessário
                if ano_obra != ano_atual_no_site:
                    sleep(random.uniform(0.8, 1.6))
                    logger.info(f"Mudando filtro do portal para o ano: {int(ano_obra)}")
                    frame.get_by_label("Ano", exact=True).select_option(str(int(ano_obra)))
                    ano_atual_no_site = ano_obra


                try:
                    # Seleciona campo de filtro por número
                    frame.locator("select[aria-label='Campo de Filtro'][aria-description='campo lista']").first.select_option("numero")

                    # Preenche o número da obra e consulta
                    campo_ano_obra = frame.get_by_role("textbox", name="Primeiro valor para o filtro")
                    campo_ano_obra.clear()
                    campo_ano_obra.press_sequentially((str(int(numero_da_obra))), delay=random.uniform(0.1, 0.3))
                    frame.get_by_text("Consultar", exact=True).click()
                    sleep(random.uniform(0.9, 1.7))

                    # Localiza a linha correta pela entidade e abre detalhes
                    linha_correta = frame.locator("table tbody tr").filter(has_text=entidade)
                    linha_correta.get_by_title("Visualizar").first.click()
                    sleep(random.uniform(0.8, 1.5))

                    # Aba Execução e captura o campo de %
                    frame.get_by_role("listitem", name="Execução").click()
                    valor_extraido = frame.get_by_role("textbox", name="% de execução financeira")
                    valor_extraido.wait_for(state="visible")
                    percentual = valor_extraido.input_value()
                    lista_porcentagens.append(percentual)

                    # Fecha a janela/modal
                    frame.get_by_role("button", name="Fechar Janela").click()
                    sleep(random.uniform(0.8, 1.4))

                except Exception as e:
                    logger.warning(f"Falha ao obter % de execução para Obra {numero_da_obra}/{ano_obra} ({entidade}): {e}")
                    lista_porcentagens.append(None)
                    # Tenta fechar eventual modal aberto
                    try:
                        frame.get_by_role("button", name="Fechar Janela").click()
                    except Exception:
                        pass
                    sleep(random.uniform(0.6, 1.2))

            # Garante que o tamanho bate; se não, preenche com None
            if len(lista_porcentagens) != len(df_agrupado):
                faltam = len(df_agrupado) - len(lista_porcentagens)
                if faltam > 0:
                    lista_porcentagens.extend([None] * faltam)

            df_agrupado['% de execução financeira'] = lista_porcentagens

            browser.close()

        logger.info("Dados de obras coletados com sucesso!")
        return True, df_agrupado, linhas_removidas

    except Exception as e:
        try:
            # Descobre a raiz do projeto e salva na pasta logs
            caminho_foto = obter_caminho_arquivo( "logs", f"erro_tela{datetime.now()}.png")
            page.screenshot(path=str(caminho_foto), full_page=True)
            logger.error(f"Erro na raspagem. Screenshot salvo em: {caminho_foto}")
        except Exception as erro_foto:
            logger.error("Não foi possível tirar o screenshot.")
        logger.warning(f"Erro ao processar os dados de obras: {e}")
        return False, pd.DataFrame(), 0