from playwright.sync_api import sync_playwright
import pandas as pd
import os
from playwright_stealth import Stealth
from time import sleep
from datetime import datetime
import random
import logging

from processors.limpar_dados import limpar_dados_brutos
from utils.config import obter_caminho_arquivo

logger = logging.getLogger(__name__)

def baixar_dados_patrimonio(url: str) -> tuple[bool, pd.DataFrame, int]:
    """
    Baixa a listagem de patrimônio (bens) via portal e retorna DataFrame.

    Args:
        url: URL da página de Bens (Patrimônio) no portal

    Returns:
        (sucesso: bool, df: pd.DataFrame)
    """
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

            logger.info("Acessando o portal de patrimônio...")
            page.goto(url)
            sleep(random.uniform(2.5, 4.5))

            try:
                page.get_by_role("button", name="Rejeitar não necessários").click(force=True)
            except Exception:
                pass

            frame = page.locator('iframe[title="Item"]').content_frame

            # Executa consulta padrão (sem ano corrente)
            try:
                frame.get_by_label("Ano da Aquisição").click()
                # Tenta desmarcar 2026 se existir
                try:
                    frame.get_by_role("checkbox", name=f"{datetime.today().year}").uncheck()
                except Exception:
                    pass
            except Exception:
                pass

            try:
                frame.get_by_text("Consultar", exact=True).click()
            except Exception:
                pass

            sleep(random.uniform(0.6, 1.2))
            page.get_by_role("button", name="Dados Abertos").click()

            with page.expect_download() as download_info:
                frame.get_by_role("button", name="Confirmar").click()
            download = download_info.value

            caminho_arquivo = obter_caminho_arquivo('data/patrimonio', f'patrimonio_bens.csv')
            os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
            download.save_as(caminho_arquivo)

            # Leitura e limpeza do CSV baixado
            df, linhas_removidas = limpar_dados_brutos(caminho_arquivo)

            # Remove arquivo temporário
            try:
                os.remove(caminho_arquivo)
            except Exception:
                pass

            browser.close()

        logger.info("Dados de patrimônio coletados com sucesso!")
        return True, df, linhas_removidas

    except Exception as e:
        try:
            # Descobre a raiz do projeto e salva na pasta logs
            caminho_foto = obter_caminho_arquivo( "logs", f"erro_tela{datetime.now()}.png")
            page.screenshot(path=str(caminho_foto), full_page=True)
            logger.error(f"Erro na raspagem. Screenshot salvo em: {caminho_foto}")
        except Exception as erro_foto:
            logger.error(f"Não foi possível tirar o screenshot.{erro_foto}")
        logger.error(f"Erro ao processar os dados de orçamento: {e}")
        return False, pd.DataFrame(), 0
