import streamlit as st
import os
from dotenv import load_dotenv
import logging

from services.cloud_storage import obter_dados
from processors.limpar_dados import formatar_reais
from utils.config import load_config, obter_caminho_arquivo


load_dotenv()
logger = logging.getLogger(__name__)

caminho_config = obter_caminho_arquivo('data', 'config.json')
config = load_config(caminho_config)

# Carrea os dados base
url = os.getenv('ARQUIVO_BASE_OBRAS_CORUPA')
dados_ausentes = config['SC']['Corupa']['base_dados']['obras']['dados_ausentes']
data_ultima_atualizacao = config['SC']['Corupa']['base_dados']['obras']['ultima_atualizacao']

try:
    sucesso, df_obras = obter_dados(url)
except Exception as e:
    st.warning(f"Erro ao carregar os dados tente voltar depois")
    logging.error(f"Erro ao carregar os dados tente voltar depois: {e}")
    st.stop()

df_obras['Valor Total'] = df_obras['Valor Total'].astype(float).apply(formatar_reais)


st.title('Obras')


tab1, tab2 = st.tabs(['Obras em Andamento', 'Demais obras'])

try:
    with tab1:
        df_obras_concluidas_filtrado = df_obras[df_obras['Situação'] == 'Em Andamento']
        df_obras_concluidas_filtrado['% de execução financeira'] = df_obras_concluidas_filtrado['% de execução financeira'].str.replace(',', '.').astype(float)
        colunas_visiveis_obras_concluidas = ["Descrição", "Percentual Conclusão (%)", "% de execução financeira", "Valor Total"]
        df_visivel_obras_concluidas = df_obras_concluidas_filtrado[colunas_visiveis_obras_concluidas]

        evento = st.dataframe(
            df_visivel_obras_concluidas,
            column_config={
                "Percentual Conclusão (%)": st.column_config.ProgressColumn(
                    "Status da Obra(%)",
                    help="",
                    format="%f",
                    min_value=0,
                    max_value=100,
                ),
                "% de execução financeira": st.column_config.ProgressColumn(
                    "Pagamento da Obra(%)",
                    help="",
                    format="%f",
                    min_value=0,
                    max_value=100,
                )
            },
            hide_index=True,
            selection_mode='single-row',
            on_select='rerun',
            width='content'
        )

        linha_selecionada = evento.selection.rows

        if len(linha_selecionada) > 0:
            indice = linha_selecionada[0]

            df_detalhado = df_obras_concluidas_filtrado.iloc[indice]

            st.write('🔍 Ficha Completa da Obra')
            st.dataframe(
                df_detalhado,
                width='stretch'
            )

    with tab2:
        df_demais_obras_filtrado = df_obras[df_obras['Situação'] != 'Em Andamento']
        colunas_visiveis_demais_obras = ["Descrição", "Situação", "Data de Início", "Previsão Conclusão", "Valor Total"]
        df_visivel_demais_obras = df_demais_obras_filtrado[colunas_visiveis_demais_obras]

        evento2 = st.dataframe(
            df_visivel_demais_obras,
            hide_index=True,
            selection_mode='single-row',
            on_select='rerun',
            width='content'
        )

        linha_selecionada2 = evento2.selection.rows

        if len(linha_selecionada2) > 0:
            indice2 = linha_selecionada2[0]

            df_detalhado2 = df_demais_obras_filtrado.iloc[indice2]

            st.write('🔍 Ficha Completa da Obra')
            st.dataframe(
                df_detalhado2,
                width='stretch'
            )
except Exception as e:
    st.error(f"Erro ao carregar os dados tente voltar depois")
    logging.error(f"Erro ao carregar os dados tente voltar depois: {e}")

if dados_ausentes > 0:
    st.info(
        f"⚠️ **Nota de Transparência:** Aproximadamente {dados_ausentes} registros fornecidos pela prefeitura continham erros de "
        "formatação (linhas corrompidas) e não puderam ser lidos."
        , icon="ℹ️")
st.info(f'Última coleta dos dados: {data_ultima_atualizacao}')



