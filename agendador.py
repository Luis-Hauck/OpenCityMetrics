import os
import random

import schedule
import pandas as pd
from dotenv import load_dotenv
import time
from datetime import datetime
import logging
from time import sleep

from services.cloud_storage import obter_dados
from processors.funcionarios import processar_funcionarios
from processors.obras import processar_obras
from processors.orcamento import processar_orcamento
from processors.patrimonio import processar_patrimonio
from collectors.funcionarios import baixar_dados_funcionarios
from collectors.obras import baixar_dados_obras
from collectors.orcamento import baixar_dados_orcamento
from collectors.patrimonio import baixar_dados_patrimonio
from utils.config import load_config, save_config, obter_caminho_arquivo


load_dotenv()

ARQUIVO_BASE_DESPESAS_FUNCIONARIOS_CORUPA = os.getenv('ARQUIVO_BASE_DESPESAS_FUNCIONARIOS_CORUPA')
ARQUIVO_BASE_OBRAS_CORUPA = os.getenv('ARQUIVO_BASE_OBRAS_CORUPA')
ARQUIVO_BASE_PATRIMONIO_CORUPA = os.getenv('ARQUIVO_BASE_PATRIMONIO_CORUPA')
ARQUIVO_BASE_ORCAMENTO_CORUPA = os.getenv('ARQUIVO_BASE_ORCAMENTO_CORUPA')
TOKEN_HOSPEDAGEM = os.getenv('TOKEN_HOSPEDAGEM')

logger = logging.getLogger(__name__)

def job_coletar_dados_funcionarios():

    try:
        sucesso_base, df_base = obter_dados(ARQUIVO_BASE_DESPESAS_FUNCIONARIOS_CORUPA)
    except Exception as e:
        logger.error("Falha ao carregar a base de funcionários da nuvem; prosseguindo com base vazia.")
        df_base = pd.DataFrame()

    logger.info(f'Iniciando coleta de dados dos funcionarios')
    caminho = obter_caminho_arquivo('data', 'config.json')
    config = load_config(rf'{caminho}')
    try:
        for estado, cidades in config.items():
            for cidade, dados_cidade in cidades.items():
                if dados_cidade['base_dados']['funcionarios']['ativo']:
                    url = dados_cidade['base_dados']['funcionarios']['url']
                    mes_incial = 1
                    mes_final = 7
                    ano_incial = 2026
                    ano_final = datetime.today().year

                    tentativas = 0
                    concluido = False
                    logger.info(f'Tentativa n° {tentativas + 1} de acessar o portal')
                    while tentativas < 3 and not concluido:
                        sleep(random.uniform(20, 120))
                        sucesso, df_novo, linhas_removidas = baixar_dados_funcionarios(mes_incial, mes_final, ano_incial, ano_final, url)
                        if sucesso:
                            dados_cidade['base_dados']['funcionarios']['dados_ausentes'] = linhas_removidas
                            dados_cidade['base_dados']['funcionarios']['ultima_atualizacao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                            save_config(caminho, config)
                            processar_funcionarios(df_novo, df_base, TOKEN_HOSPEDAGEM)
                            concluido = True
                            logger.info("Dados dos funcionarios salvos com sucesso!")
                        else:
                            tentativas += 1
    except Exception as e:
        logger.error(f"Erro ao processar os dados dos funcionarios: {e}")


def job_coletar_dados_obras():
    sucesso_base, df_base = obter_dados(ARQUIVO_BASE_OBRAS_CORUPA)
    if not sucesso_base:
        logger.error("Falha ao carregar a base de obras da nuvem; prosseguindo com base vazia.")
        df_base = pd.DataFrame()

    caminho = obter_caminho_arquivo('data', 'config.json')
    config = load_config(rf'{caminho}')
    try:
        for estado, cidades in config.items():
            for cidade, dados_cidade in cidades.items():
                base = dados_cidade.get('base_dados', {})
                if dados_cidade['base_dados']['obras']['ativo']:
                    url = dados_cidade['base_dados']['obras']['url']
                    ano_inicio = datetime.today().year - 2
                    ano_fim = datetime.today().year
                    tentativas = 0
                    concluido = False
                    logger.info(f'Tentativa n° {tentativas + 1} de acessar o portal')
                    while tentativas < 3 and not concluido:
                        sleep(random.uniform(20, 120))
                        sucesso, df_novo, linhas_removidas = baixar_dados_obras(ano_inicio, ano_fim, url)
                        if sucesso:
                            base['obras']['dados_ausentes'] = linhas_removidas
                            base['obras']['ultima_atualizacao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            save_config(rf'{caminho}', config)
                            processar_obras(df_novo, df_base, TOKEN_HOSPEDAGEM)
                            concluido = True
                            logger.info("Dados das obras salvos com sucesso!")
                        else:
                            tentativas += 1
    except Exception as e:
        logger.warning(f"Erro ao processar os dados das obras: {e}")


def job_coletar_dados_orcamento():
    sucesso_base, df_base = obter_dados(ARQUIVO_BASE_ORCAMENTO_CORUPA)
    if not sucesso_base:
        logger.error("Falha ao carregar a base de orçamento da nuvem; prosseguindo com base vazia.")
        df_base = pd.DataFrame()
    caminho = obter_caminho_arquivo('data', 'config.json')
    config = load_config(rf'{caminho}')
    logger.info(config)
    try:
        for estado, cidades in config.items():
            for cidade, dados_cidade in cidades.items():
                base = dados_cidade.get('base_dados', {})
                if dados_cidade['base_dados']['orcamento']['ativo']:
                    url = dados_cidade['base_dados']['orcamento']['url']
                    ano_inicio = datetime.today().year - 2
                    ano_fim = datetime.today().year
                    tentativas = 0
                    concluido = False
                    logger.info(f'Tentativa n° {tentativas + 1} de acessar o portal')
                    while tentativas < 3 and not concluido:
                        sleep(random.uniform(5, 15))
                        sucesso, df_novo, linhas_removidas = baixar_dados_orcamento(ano_inicio, ano_fim, url)
                        if sucesso:
                            base['orcamento']['dados_ausentes'] = linhas_removidas
                            base['orcamento']['ultima_atualizacao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            save_config(rf'{caminho}', config)
                            processar_orcamento(df_novo, df_base, TOKEN_HOSPEDAGEM)
                            concluido = True
                            logger.info('Sucessp ao coletar dados do orçamento')
                        else:
                            tentativas += 1
    except Exception as e:
        logger.error(f"Erro ao processar os dados do orçamento: {e}")


def job_coletar_dados_patrimonio():
    sucesso_base, df_base = obter_dados(ARQUIVO_BASE_PATRIMONIO_CORUPA)
    if not sucesso_base:
        logger.info("Falha ao carregar a base de patrimônio da nuvem; prosseguindo com base vazia.")
        df_base = pd.DataFrame()
    caminho = obter_caminho_arquivo('data', 'config.json')
    config = load_config(rf'{caminho}')
    logger.info(config)
    try:
        for estado, cidades in config.items():
            for cidade, dados_cidade in cidades.items():
                base = dados_cidade.get('base_dados', {})
                if dados_cidade['base_dados']['patrimonio']['ativo']:
                    url = dados_cidade['base_dados']['patrimonio']['url']
                    tentativas = 0
                    concluido = False
                    logger.info(f'Tentativa n° {tentativas+1} de acessar o portal')
                    while tentativas < 3 and not concluido:
                        sleep(random.uniform(5, 20))
                        sucesso, df_novo, linhas_removidas = baixar_dados_patrimonio(url)
                        if sucesso:
                            base['patrimonio']['dados_ausentes'] = linhas_removidas
                            base['patrimonio']['ultima_atualizacao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            save_config(rf'{caminho}', config)
                            processar_patrimonio(df_novo, df_base, TOKEN_HOSPEDAGEM)
                            concluido = True
                        else:
                            tentativas += 1
    except Exception as e:
        logger.error(f"Erro ao processar os dados do patrimônio: {e}")


def setup_schedule():

    schedule.every().day.at("19:27", "America/Sao_Paulo").do(job_coletar_dados_orcamento())
    schedule.every().day.at("19:29", "America/Sao_Paulo").do(job_coletar_dados_patrimonio())
    schedule.every().day.at("19:30", "America/Sao_Paulo").do(job_coletar_dados_funcionarios())
    schedule.every().day.at("19::35", "America/Sao_Paulo").do(job_coletar_dados_obras())


def start_scheduler():
    setup_schedule()
    logger.info("Scheduler iniciado. Aguardando jobs...")
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == "__main__":
    start_scheduler()