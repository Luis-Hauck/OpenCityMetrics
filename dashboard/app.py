import streamlit as st
from utils.config import obter_caminho_arquivo

st.logo('https://public-blob.squarecloud.dev/c5fea93b0bd97005b83e0c46a5465f22c4b53eac/image/LogoOpenCitymetrics-ex180.jpeg'
    'logo.png')

# Define as views usando caminhos absolutos seguros
main_page = st.Page(obter_caminho_arquivo('dashboard/views', 'home.py'), title="Página inicial")
page_2 = st.Page(obter_caminho_arquivo('dashboard/views', 'funcionarios.py'), title="Despesas com os funcionários")
#page_3 = st.Page(obter_caminho_arquivo('dashboard/views', 'diarias.py'), title="Despesas com Diárias")
page_4 = st.Page(obter_caminho_arquivo('dashboard/views', 'obras.py'), title="Obras")
page_5 = st.Page(obter_caminho_arquivo('dashboard/views', 'patrimonio.py'), title="Patrimônio")
page6 = st.Page(obter_caminho_arquivo('dashboard/views', 'orcamento.py'), title="Orçado e Executado")

pg = st.navigation([main_page, page_2, page_4, page_5, page6])

pg.run()