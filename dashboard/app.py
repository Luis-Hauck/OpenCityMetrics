import streamlit as st
from utils.config import obter_caminho_arquivo

caminho_logo= obter_caminho_arquivo('assets', 'logo.png')


st.set_page_config(
    page_title="Open City Metrics",
    page_icon="🏛️",
)

st.logo(caminho_logo,
        size='large',
        )

st.markdown(
    """
    <style>
        [data-testid="stSidebarHeader"] img {
            height: 5rem !important; 
            max-height: 5rem !important;
            width: auto !important;
            max-width: 100% !important;
        }

        /Dá mais espaço para o cabeçalho respirar e acomodar a logo maior */
        [data-testid="stSidebarHeader"] {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# Define as views usando caminhos absolutos seguros
main_page = st.Page(obter_caminho_arquivo('dashboard/views', 'home.py'), title="Página inicial")
page_2 = st.Page(obter_caminho_arquivo('dashboard/views', 'funcionarios.py'), title="Despesas com os funcionários")
#page_3 = st.Page(obter_caminho_arquivo('dashboard/views', 'diarias.py'), title="Despesas com Diárias")
page_4 = st.Page(obter_caminho_arquivo('dashboard/views', 'obras.py'), title="Obras")
page_5 = st.Page(obter_caminho_arquivo('dashboard/views', 'patrimonio.py'), title="Patrimônio")
page6 = st.Page(obter_caminho_arquivo('dashboard/views', 'orcamento.py'), title="Orçado e Executado")

pg = st.navigation([main_page, page_2, page_4, page_5, page6])

pg.run()