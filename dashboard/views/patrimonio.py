import streamlit as st
import os
from dotenv import load_dotenv
import logging

from services.cloud_storage import obter_dados
from processors.patrimonio import tratar_dados
from utils.config import load_config

load_dotenv()

config = load_config('data/config.json')
url = os.getenv('ARQUIVO_BASE_PATRIMONIO_CORUPA')

dados_patrimonio = config['SC']['Corupa']['base_dados']['patrimonio']
data_ultima_atualizacao = dados_patrimonio['ultima_atualizacao']
dados_ausentes = dados_patrimonio['dados_ausentes']
url_patrimonio = dados_patrimonio['url']

try:
    sucesso, df_= obter_dados(url)
    df_patrimonio = tratar_dados(df_)
except Exception as e:
    st.warning(f"Erro ao carregar os dados tente voltar depois")
    logging.error(f"Erro ao carregar os dados tente voltar depois: {e}")
    st.stop()

st.title('Patrimônio')

# Nota explicativa geral
st.caption(
    """
    **Visão informativa:** esta página apresenta o patrimônio público de forma agregada para apoiar análises e planejamento.
    
    **Cuidado com interpretações:** podem existir campos sem preenchimento ou dados atrasados conforme a atualização da Prefeitura. Para validação legal, utilize o **Portal da Transparência oficial**.
    """
)


tab1, tab2, tab3 = st.tabs(['Visão geral', 'Frota de Veículos', 'Busca'])

try:
    with tab1:
        patrimonio_disponivel = df_patrimonio[df_patrimonio["Status"] == 'Disponível']
        valor_patrimonial = patrimonio_disponivel["Valor Contábil"].sum()
        valor_patrimonial_formatado = f"R$ {valor_patrimonial:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.metric('Valor Patrimonial Estimado Disponível', f'{valor_patrimonial_formatado}')

        st.subheader('Top 20 Bens Mais Valiosos')
        df_top_20 = patrimonio_disponivel.nlargest(20, 'Valor Contábil')
        colunas_visiveis = ['Tipo', 'Descrição', 'Valor Contábil']
        df_top_20_visivel = df_top_20[colunas_visiveis]

        df_top_20_visivel['Tipo'] = df_top_20_visivel['Tipo'].replace({
            'Bens Imóveis': '🏢 Imóvel',
            'Bens Móveis': '🚜 Veículo/Equip.'
        })

        df_top_20_visivel['Descrição'] = df_top_20_visivel['Descrição'].str.slice(0, 60) + '...'
        df_top_20_visivel['Valor Contábil'] = df_top_20_visivel['Valor Contábil'].astype(float).apply(lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))


        evento = st.dataframe(df_top_20_visivel,
                     hide_index=True,
                     width='content',
                     selection_mode='single-row',
                     on_select='rerun',

                     )
        linha_selecionada = evento.selection.rows

        if len(linha_selecionada) > 0:
            indice = linha_selecionada[0]

            df_detalhado = df_top_20.iloc[indice]

            st.write('🔍 Ficha Completa')
            st.dataframe(
                df_detalhado,
                width='stretch'
            )


    with tab2:
        st.write('Agrupamento dos véiculos disponiveis pela prefeitura')
        regex_veiculos = (
            r"CHASSI|RENAVAM|"  # Identificadores
            r"VE[ÍI]CULO|AUTOM[ÓO]VEL|AMBUL[ÂA]NCIA|CAMINHONETE|MOTOCICLETA"  
            r"CAMINH[ÃA]O|[ÔO]NIBUS" 
            r"TRATOR|ESCAVAD|RETROESCAVAD|MOTONIVELADORA|P[ÁA] CARREGADEIRA|ROLO COMPACTADOR|EMPILHADEIRA"
        )
        df_veiculos = df_patrimonio[
            df_patrimonio['Descrição'].str.contains(
                regex_veiculos,
                regex=True,
                case=False,
                na=False,
            )
        ]

        colunas_visiveis_veiculos = ['Descrição', 'Valor Contábil', 'Aquisição', 'Incorporação']
        df_veiculos_visivel = df_veiculos[colunas_visiveis_veiculos]
        df_veiculos_visivel['Valor Contábil'] = df_veiculos_visivel['Valor Contábil'].astype(float).apply(
            lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))

        evento2 = st.dataframe(df_veiculos_visivel,
                              hide_index=True,
                              width='content',
                              selection_mode='single-row',
                              on_select='rerun',

                              )
        linha_selecionada2 = evento2.selection.rows

        if len(linha_selecionada2) > 0:
            indice2 = linha_selecionada2[0]

            df_detalhado2 = df_veiculos.iloc[indice2]

            st.write('🔍 Ficha Completa')
            st.dataframe(
                df_detalhado2,
                width='stretch'
            )
    with tab3:
        st.write('Busca de itens pertencentes a prefeitura')
        desc_selecao_item = st.text_input('Descrição do item:')

        df_filtrado = df_patrimonio
        df_filtrado = df_filtrado[colunas_visiveis]
        if desc_selecao_item:
            df_filtrado = df_filtrado[df_filtrado['Descrição'].str.contains(desc_selecao_item, case=False, na=False)]


        evento3 = st.dataframe(df_filtrado,
                               hide_index=True,
                               width='content',
                               selection_mode='single-row',
                               on_select='rerun',
                               )

        linha_selecionada3 = evento3.selection.rows

        if len(linha_selecionada3) > 0:
            indice3 = linha_selecionada3[0]

            df_detalhado3 = df_veiculos.iloc[indice3]

            st.write('🔍 Ficha Completa')
            st.dataframe(
                df_detalhado3,
                width='stretch'
            )
except Exception as e:
    st.error(f"Erro ao carregar os dados tente voltar depois")
    logging.error(f"Erro ao carregar os dados tente voltar depois: {e}")
    st.stop()

st.divider()

st.caption(f"🗓️ **Última coleta:** {data_ultima_atualizacao} &nbsp;&nbsp;|&nbsp;&nbsp; "
           f"⚠️ **Dados ausentes:** {dados_ausentes} &nbsp;&nbsp;|&nbsp;&nbsp; "
           f"[🏛️ **Acessar Fonte Oficial**]({url_patrimonio})")
