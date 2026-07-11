import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.express as px

from services.cloud_storage import obter_dados

load_dotenv()

# Carrea o dataframe base
url = os.getenv('ARQUIVO_BASE_OBRAS_CORUPA')

sucesso, df_obras = obter_dados(url)
df_obras["% de execução financeira"] = df_obras["% de execução financeira"].str.replace(',', '.').astype(float)


st.title('Obras')


tab1, tab2 = st.tabs(['Obras em Andamento', 'Demais obras'])

with tab1:
    df_obras_concluidas_filtrado = df_obras[df_obras['Situação'] == 'Em Andamento']
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
        use_container_width=True
    )

    linha_selecionada = evento.selection.rows

    if len(linha_selecionada) > 0:
        indice = linha_selecionada[0]

        df_detalhado = df_obras_concluidas_filtrado.iloc[indice]

        st.write('🔍 Ficha Completa da Obra')
        st.dataframe(
            df_detalhado,
            use_container_width=True
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
            use_container_width=True
        )

        linha_selecionada2 = evento2.selection.rows

        if len(linha_selecionada2) > 0:
            indice2 = linha_selecionada2[0]

            df_detalhado2 = df_demais_obras_filtrado.iloc[indice2]

            st.write('🔍 Ficha Completa da Obra')
            st.dataframe(
                df_detalhado2,
                use_container_width=True
            )



