from playwright.sync_api import sync_playwright
import pandas as pd
import os
from datetime import datetime
from playwright_stealth import Stealth
from time import sleep
import random
import logging

from processors.limpar_dados import limpar_dados_brutos
from utils.config import obter_caminho_arquivo

logger = logging.getLogger(__name__)


def baixar_dados_orcamento(ano_inicio: int, ano_fim: int, url: str) -> tuple[bool, pd.DataFrame, int]:
    """
    Baixa dados da "Execução do Orçamento da Despesa" para os anos informados.

    Para cada ano seleciona o mês adequado (dezembro para anos fechados e mês
    corrente para o ano atual), baixa o CSV de Dados Abertos e retorna um
    DataFrame consolidado com uma coluna adicional 'ano'.

    Returns: (sucesso, df, linhas_removidas)
    """
    lista_df: list[pd.DataFrame] = []
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
            context = browser.new_context(locale="pt-BR", timezone_id="America/Sao_Paulo")
            stealth = Stealth()
            stealth.apply_stealth_sync(context)
            page = context.new_page()
            page.set_default_timeout(60000)

            logger.info("Acessando o portal de execução do orçamento da despesa...")
            page.goto(url)
            sleep(random.uniform(2.5, 4.5))

            try:
                page.get_by_role("button", name="Rejeitar não necessários").click()
            except Exception:
                pass

            frame = page.locator('iframe[title="Item"]').content_frame

            for ano in range(ano_inicio, ano_fim + 1):
                mes = 12
                if ano == datetime.now().year:
                    mes = datetime.now().month
                mes_str = str(mes).zfill(2)

                logger.info(f"Selecionando ano {ano} e mês {mes_str}...")
                frame.get_by_label("Ano").select_option(str(ano))
                sleep(random.uniform(0.3, 0.8))
                frame.get_by_label("Mês", exact=True).select_option(mes_str)
                try:
                    frame.get_by_text("Consultar").click()
                except Exception:
                    pass

                page.get_by_role("button", name="Dados Abertos").click()
                with page.expect_download() as download_info:
                    with page.expect_popup():
                        frame.get_by_role("button", name="Confirmar").click(force=True)
                download = download_info.value


                caminho_arquivo = obter_caminho_arquivo('data/orcamento', f'orcamento_despesas_{ano}.csv')
                os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
                download.save_as(caminho_arquivo)

                df, linhas_ = limpar_dados_brutos(caminho_arquivo)
                df['ano'] = ano
                lista_df.append(df)
                linhas_removidas += linhas_

                try:
                    os.remove(caminho_arquivo)
                except Exception:
                    pass

                # fecha possível janela extra do portal
                try:
                    frame.get_by_role("button", name="Fechar Janela").click()
                except Exception:
                    pass

                sleep(random.uniform(0.3, 1.0))

            browser.close()

        if not lista_df:
            return False, pd.DataFrame(), 0

        df_agrupado = pd.concat(lista_df, ignore_index=True)
        logger.info("Dados de orçamento coletados com sucesso!")
        return True, df_agrupado, linhas_removidas

    except Exception as e:
        logger.error(f"Erro ao processar os dados de orçamento: {e}")
        return False, pd.DataFrame(), 0
