import streamlit as st
import os
from dotenv import load_dotenv
from utils.config import load_config
from datetime import datetime
import plotly.express as px

from services.cloud_storage import obter_dados
from processors.orcamento import tratar_dados
from processors.limpar_dados import formatar_reais



load_dotenv()


config = load_config('data/config.json')
url = os.getenv('ARQUIVO_BASE_ORCAMENTO_CORUPA')

dados_orcamento = config['SC']['Corupa']['bases_dados']['orcamento']
data_ultima_atualizacao = dados_orcamento['ultima_atualizacao']
dados_ausentes = dados_orcamento['dados_ausentes']

sucesso, df_ = obter_dados(url)
df_orcamento = tratar_dados(df_)

st.title('Orçamento Atualizado e Executado')

# Guarda de segurança para dados ausentes ou estrutura inesperada
if not sucesso or df_orcamento is None or df_orcamento.empty:
    st.warning('Não foi possível carregar os dados de orçamento no momento. Tente novamente mais tarde.')
    st.stop()


tab1, tab2 = st.tabs(['Visão geral', 'Para onde vai o dinheiro?'])

with tab1:
    lista_anos = sorted(df_orcamento['Ano'].dropna().unique(), reverse=True)

    ano_selecionado1 = st.selectbox('Selecione o ano', lista_anos, key='ano_selecionado_tab1')

    dados_ano_atual = df_orcamento[df_orcamento['Ano'] == ano_selecionado1]
    orcamento_incial = dados_ano_atual['Orçamento Inicial'].sum()
    orcamento_atualziado = dados_ano_atual['Orçamento Atualizado'].sum()
    realizado_no_ano = dados_ano_atual['Liquidado Até o Mês'].sum()

    percentual_orcado = (realizado_no_ano / orcamento_atualziado) * 100

    col1, col2 = st.columns(2, gap='xxsmall')
    col1.metric(label='Despesas Executadas', value=formatar_reais(realizado_no_ano))
    col2.metric(label='% Executado do Orcamento', value=f'{percentual_orcado:.2f}%')
    st.metric(label='Orçamento Inicial', value=formatar_reais(orcamento_incial))
    st.metric(label='Orçamento Atualizado', value=formatar_reais(orcamento_atualziado))

    # top maiores gastos por funçao
    top_10_gastos_por_funcoes =  dados_ano_atual.groupby(['Função'])['Liquidado Até o Mês'].sum().sort_values(ascending=False).head(10).reset_index()

    fig = px.bar(top_10_gastos_por_funcoes,
                 x='Função',
                 y='Liquidado Até o Mês',
                 title='Ranking das Funções com Maiores Gastos',
                 )

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


    # ranking dos maiores gastos
    st.space()
    st.subheader('Top 10 Ações com Maiores Gastos')
    top_10_gastos_por_valor =  dados_ano_atual.sort_values(by='Liquidado Até o Mês', ascending=False).head(10)
    # Formatação para reais
    top_10_gastos_por_valor['Realizado_Reais'] = top_10_gastos_por_valor['Liquidado Até o Mês'].astype(float).apply(formatar_reais)

    colunas_visiveis_gastos = ['Ação', 'Realizado_Reais']
    df_gastos_visiveis = top_10_gastos_por_valor[colunas_visiveis_gastos]

    evento = st.dataframe(
        df_gastos_visiveis,
        hide_index=True,
        width='stretch',
        selection_mode='single-row',
        on_select='rerun',
        column_config={
            'Realizado_Reais': st.column_config.TextColumn('Executado (R$)')
        }
    )
    linha_selecionada = evento.selection.rows

    if len(linha_selecionada) > 0:
        indice2 = linha_selecionada[0]

        df_detalhado = top_10_gastos_por_valor.iloc[indice2]

        st.write('🔍 Ficha Completa')
        st.dataframe(
            df_detalhado,
            width='stretch'
        )

with tab2:
    anos_disponiveis = sorted(df_orcamento['Ano'].unique(), reverse=True)

    ano_selecionado = st.selectbox('Selecione o ano', anos_disponiveis, key='ano_selecionado_tab2')

    dados_ano_selecionado = df_orcamento[df_orcamento['Ano'] == ano_selecionado]

    # top maiores gastos por funçao
    gastos_por_funcoes = dados_ano_selecionado.groupby(['Função'])[['Orçamento Atualizado', 'Liquidado Até o Mês']].sum().reset_index()

    fig2 = px.bar(gastos_por_funcoes,
                  x=['Liquidado Até o Mês','Orçamento Atualizado'],
                  y='Função',
                  barmode='group',
                  orientation='h',
                  title='Ranking das Funções com Maiores Gastos',
                  )

    fig2.update_layout(yaxis={'categoryorder': 'total ascending'})

    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

    lista_funcoes = sorted(dados_ano_selecionado['Função'].unique())

    funcao_selecioanda = st.selectbox('Selecione a Função', lista_funcoes)

    dados_funcao_slecioanda =  dados_ano_selecionado[dados_ano_selecionado['Função']==funcao_selecioanda]

    fig3 = px.bar(dados_funcao_slecioanda,
                  x='Subfunção',
                  y=['Liquidado Até o Mês','Orçamento Atualizado'],
                  barmode='group',
                  title=f'Ranking das Subfunções Realacionadas a {funcao_selecioanda}',
                  )

    st.plotly_chart(fig3, theme="streamlit", use_container_width=True)
    with st.expander("Ver detalhamento profundo (Subfunções, Programas e Ações)"):
        lista_subfuncoes = sorted(dados_funcao_slecioanda['Subfunção'].unique())
        subfuncao_selecioanda = st.selectbox('Selecione a Subfunção', lista_subfuncoes)

        dados_subfuncao_selecioanda = dados_funcao_slecioanda[dados_funcao_slecioanda['Subfunção']==subfuncao_selecioanda]

        fig4 = px.bar(dados_funcao_slecioanda,
                      x='Programa',
                      y=['Liquidado Até o Mês','Orçamento Atualizado'],
                      barmode='group',
                      title=f'Programa Realacionadas a {funcao_selecioanda}',
                      )

        st.plotly_chart(fig4, theme="streamlit", use_container_width=True)

        lista_acoes = sorted(dados_funcao_slecioanda['Ação'].unique())
        acao_selecioanda = st.selectbox('Selecione a Ação', lista_acoes)

        dados_acao_selecioanda = dados_funcao_slecioanda[
            dados_funcao_slecioanda['Ação'] == acao_selecioanda]

        fig5 = px.bar(dados_acao_selecioanda,
                      x='Ação',
                      y=['Liquidado Até o Mês','Orçamento Atualizado'],
                      barmode='group',
                      title=f'Ações Realacionadas a {funcao_selecioanda}',
                      )
        fig5.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig5, theme="streamlit", use_container_width=True)







