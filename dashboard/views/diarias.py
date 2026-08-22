import streamlit as st
import pandas as pd
import os
import io
import requests

from datetime import datetime
import plotly.express as px




df = pd.read_parquet(r'D:\Projects\OpenCityMetrics\data\diarias\gastos_com_diarias_corupa.parquet')
df['Emissão'] = pd.to_datetime(
            df['Emissão'],
            format = '%d/%m/%Y',
            dayfirst = True,
            errors = 'raise',
            )


st.title('Despesas com Diárias')

# Nota explicativa geral
st.info(
    """
    **Uso informativo:** esta aba apresenta tendências de gastos com diárias em nível agregado (secretarias, períodos, finalidades).
    
    **Referência oficial:** dados podem conter atrasos ou lacunas conforme a publicação municipal. Para fins legais, utilize o **Portal da Transparência oficial**.
    """
)


tab1, tab2 = st.tabs(["Visão geral", "Concentração de Gastos"])

with tab1:
    st.write("Em breve...")

with tab2:
    st.write("Em breve...")