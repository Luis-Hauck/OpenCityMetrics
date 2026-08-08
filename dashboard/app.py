import streamlit as st

# Define as views
main_page = st.Page("views/home.py", title="Página inicial")
page_2 = st.Page("views/funcionarios.py", title="Despesas com os funcionários")
#page_3 = st.Page("views/diarias.py", title="Despesas com Diárias")
page_4 = st.Page("views/obras.py", title="Obras")
page_5 = st.Page("views/patrimonio.py", title="Patrimônio")
page6 = st.Page("views/orcamento.py", title="Orçado e Executado")


pg = st.navigation([main_page, page_2, page_4, page_5, page6])

pg.run()