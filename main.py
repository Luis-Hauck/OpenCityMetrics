import subprocess
import sys
import time
import logging

from utils.logging_ import setup_logging
from utils.config import obter_caminho_arquivo

logger = logging.getLogger(__name__)
setup_logging()

caminho_app_streamlit = obter_caminho_arquivo('dashboard', 'app.py')

def instalar_playwright():
    """Baixa o navegador usando o próprio Python, garantindo que vá para a pasta certa"""
    logger.info("\n[SETUP] Baixando navegador Chromium...")
    try:
        # Executa 'python -m playwright install chromium' internamente
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        logger.info("[SETUP] Navegador instalado com sucesso!\n")
    except Exception as e:
        logger.error(f"[SETUP] Erro crítico ao instalar o navegador: {e}")

def iniciar_servidor_streamlit():
    """Inicia o painel do Streamlit como um processo independente"""
    logger.info("Iniciando Painel Streamlit...")
    # O comando é exatamente o que você digitaria no terminal
    comando = [
        sys.executable, "-m", "streamlit", "run", caminho_app_streamlit,
        "--server.port", "80",
        "--server.address", "0.0.0.0"
    ]
    # Retorna o processo (não bloqueia o código)
    return subprocess.Popen(comando)


def iniciar_agendador():
    """Inicia o robô coletor como um processo independente"""
    logger.info("Iniciando Agendador de Tarefas...")
    comando = [sys.executable, "agendador.py"]
    return subprocess.Popen(comando)


if __name__ == "__main__":
    logger.info("=== INICIANDO SISTEMA OPENCITY METRICS ===")

    instalar_playwright()

    # Liga o Streamlit
    processo_streamlit = iniciar_servidor_streamlit()

    # Dá 5 segundos para o Streamlit ligar com calma antes de subir o robô
    time.sleep(5)

    # Liga o Agendador (que dentro dele pode chamar a inicialização dos logs)
    processo_agendador = iniciar_agendador()

    try:
        # 3. Mantém o arquivo run.py vivo enquanto os dois processos estiverem rodando
        processo_streamlit.wait()
        processo_agendador.wait()
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        logger.info("\nDesligando sistema. Encerrando processos...")
        processo_streamlit.terminate()
        processo_agendador.terminate()
        logger.info("Sistema encerrado com sucesso.")