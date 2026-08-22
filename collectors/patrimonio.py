import pandas as pd
import os
from time import sleep
from datetime import datetime
import random
import logging
import asyncio
from cloakbrowser import launch

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
        asyncio.set_event_loop(asyncio.new_event_loop())
        browser = launch(
            headless=False,
            humanize=True,
            args=[
                # Mantemos apenas os argumentos de estabilidade para Linux
                "--no-sandbox",
                "--disable-dev-shm-usage",

            ]
        )

        context = browser.new_context(
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        page.set_default_timeout(60000)
        page = context.new_page()
        page.set_default_timeout(60000)

        try:
            logger.info("Acessando o portal de patrimônio...")
            page.goto(url)
            sleep(random.uniform(7, 15))

            try:
                page.get_by_role("button", name="Rejeitar não necessários").click(force=True)
            except Exception:
                pass

            frame = page.locator('iframe[title="Item"]').content_frame

            # Executa consulta padrão (sem ano corrente)
            try:
                frame.get_by_label("Ano da Aquisição").click()
                # Tenta desmarcar o ano corrente se existir
                try:
                    frame.get_by_role("checkbox", name=f"{datetime.today().year}").uncheck()
                    sleep(random.uniform(3, 6))
                except Exception:
                    pass
            except Exception:
                pass

            try:
                frame.get_by_text("Consultar", exact=True).click()
            except Exception:
                pass

            sleep(random.uniform(3, 5))
            page.get_by_role("button", name="Dados Abertos").click(force=True)

            # Aguarda um pouco para que o download seja iniciado
            page.wait_for_timeout(5000)

            with page.expect_download() as download_info:
                with page.expect_popup() as page1_info:
                    frame.get_by_role("button", name="Confirmar").click(force=True)

            # Pega o arquivo que foi gerado
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

            # fecha possível janela extra do portal
            try:
                frame.get_by_role("button", name="Fechar Janela").click()
            except Exception:
                pass
        except Exception as erro_raspagem:
            try:
                agora = datetime.now().strftime("%Y%m%d_%H%M%S")
                caminho_foto = obter_caminho_arquivo("logs", f"erro_patrimonio_{agora}.png")
                page.screenshot(path=str(caminho_foto), full_page=True)
                logger.error(f"ERRO CAPTURADO! Screenshot salvo em: {caminho_foto}")
            except Exception as erro_foto:
                logger.error(f"Não foi possível tirar o screenshot: {erro_foto}")
            raise erro_raspagem

        browser.close()

        logger.info("Dados de patrimônio coletados com sucesso!")
        return True, df, linhas_removidas

    except Exception as e:
        logger.error(f"Erro ao processar os dados de patrimônio: {e}")
        return False, pd.DataFrame(), 0
