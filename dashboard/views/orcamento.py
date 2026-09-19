import streamlit as st
import os
from dotenv import load_dotenv
from utils.config import load_config
import logging
import plotly.express as px

from services.cloud_storage import obter_dados
from processors.orcamento import tratar_dados
from processors.limpar_dados import formatar_reais

load_dotenv()


config = load_config('data/config.json')
url = os.getenv('ARQUIVO_BASE_ORCAMENTO_CORUPA')

dados_orcamento = config['SC']['Corupa']['base_dados']['orcamento']
data_ultima_atualizacao = dados_orcamento['ultima_atualizacao']
dados_ausentes = dados_orcamento['dados_ausentes']
url_orcamento = dados_orcamento['url']

sucesso, df_ = obter_dados(url)
df_orcamento = tratar_dados(df_)

st.title('Orçamento Atualizado e Executado')

# Guarda de segurança para dados ausentes ou estrutura inesperada
if not sucesso or df_orcamento is None or df_orcamento.empty:
    st.warning('Não foi possível carregar os dados de orçamento no momento. Tente novamente mais tarde.')
    logging.error(f'Não foi possível carregar os dados de orçamento')
    st.stop()

st.caption(
    """
    **Análise agregada:** explore a relação entre o que foi orçado e o que está sendo executado por função, programa e ação.

    **Dados sujeitos a atualização:** eventuais atrasos ou lacunas decorrem do calendário de publicação da Prefeitura. Para fins legais, consulte o **Portal da Transparência oficial**.
    """
)

tab1, tab2 = st.tabs(['Visão geral', 'Para onde vai o dinheiro?'])

try:
    with tab1:
        lista_anos = sorted(df_orcamento['Ano'].dropna().unique(), reverse=True)

        ano_selecionado1 = st.selectbox('Selecione o ano', lista_anos, key='ano_selecionado_tab1')

        dados_ano_atual = df_orcamento[df_orcamento['Ano'] == ano_selecionado1]
        orcamento_inicial = dados_ano_atual['Orçamento Inicial'].sum()
        orcamento_atualizado = dados_ano_atual['Orçamento Atualizado'].sum()
        realizado_no_ano = dados_ano_atual['Liquidado Até o Mês'].sum()

        percentual_orcado = (realizado_no_ano / orcamento_atualizado) * 100

        col1, col2 = st.columns(2, gap='xxsmall')
        col1.metric(label='Despesas Executadas', value=formatar_reais(realizado_no_ano))
        col2.metric(label='% Executado do Orcamento', value=f'{percentual_orcado:.2f}%')
        st.metric(label='Orçamento Inicial', value=formatar_reais(orcamento_inicial))
        st.metric(label='Orçamento Atualizado', value=formatar_reais(orcamento_atualizado))

        # top maiores gastos por funçao
        top_10_gastos_por_funcoes =  dados_ano_atual.groupby(['Função'])['Liquidado Até o Mês'].sum().sort_values(ascending=False).head(10).reset_index()

        fig = px.bar(top_10_gastos_por_funcoes,
                     x='Função',
                     y='Liquidado Até o Mês',
                     title='Ranking das Funções com Maiores Gastos',
                     )

        st.plotly_chart(fig, theme="streamlit", width='content')


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
        anos_disponiveis = sorted(df_orcamento['Ano'].dropna().unique(), reverse=True)

        ano_selecionado = st.selectbox('Selecione o ano', anos_disponiveis, key='ano_selecionado_tab2')

        dados_ano_selecionado = df_orcamento[df_orcamento['Ano'] == ano_selecionado].copy()

        dados_ano_selecionado['Função'] = dados_ano_selecionado['Função'].str.strip()
        dados_ano_selecionado['Subfunção'] = dados_ano_selecionado['Subfunção'].str.strip()
        dados_ano_selecionado['Ação'] = dados_ano_selecionado['Ação'].str.strip()
        dados_ano_selecionado['Programa'] = dados_ano_selecionado['Programa'].str.strip()

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

        st.plotly_chart(fig2, theme="streamlit", width='content')

        # Subfuções relacionadas a função selecionada

        lista_funcoes = sorted(dados_ano_selecionado['Função'].unique())

        funcao_selecioanda = st.selectbox('Selecione a Função', lista_funcoes).strip()

        dados_funcao_selecionada = dados_ano_selecionado[dados_ano_selecionado['Função'] == funcao_selecioanda]
        dados_subfuncao_agrupada = dados_funcao_selecionada.groupby('Subfunção')[['Liquidado Até o Mês', 'Orçamento Atualizado']].sum().reset_index()

        fig3 = px.bar(dados_subfuncao_agrupada,
                      x='Subfunção',
                      y=['Liquidado Até o Mês','Orçamento Atualizado'],
                      barmode='group',
                      title=f'Ranking das Subfunções Realacionadas a {funcao_selecioanda}',
                      )

        st.plotly_chart(fig3, theme="streamlit", width='content')
        with st.expander("Ver detalhamento profundo (Programas e Ações)"):
            # Programas relacionadas a função selecionada
            lista_subfuncoes = sorted(dados_funcao_selecionada['Subfunção'].unique())
            subfuncao_selecionada = st.selectbox('Selecione a Subfunção', lista_subfuncoes).strip()

            dados_subfuncao_selecionada = dados_funcao_selecionada[dados_funcao_selecionada['Subfunção'] == subfuncao_selecionada]
            dados_programa_agrupado = dados_subfuncao_selecionada.groupby('Programa')[['Liquidado Até o Mês', 'Orçamento Atualizado']].sum().reset_index()

            fig4 = px.bar(dados_programa_agrupado,
                          x='Programa',
                          y=['Liquidado Até o Mês','Orçamento Atualizado'],
                          barmode='group',
                          title=f'Programas Relacionados a {subfuncao_selecionada}',
                          )

            st.plotly_chart(fig4, theme="streamlit", width='content')

            # Ações do Programa selecioando

            lista_programas = sorted(dados_subfuncao_selecionada['Programa'].unique())
            programa_selecionado = st.selectbox('Selecione o Programa', lista_programas)

            dados_programa_selecionado = dados_subfuncao_selecionada[dados_subfuncao_selecionada['Programa'] == programa_selecionado]
            dados_acao_agrupada = dados_programa_selecionado.groupby('Ação')[['Liquidado Até o Mês', 'Orçamento Atualizado']].sum().reset_index()

            fig5 = px.bar(dados_acao_agrupada,
                y='Ação',
                x=['Liquidado Até o Mês', 'Orçamento Atualizado'],
                barmode='group',
                orientation='h',  # Transforma o gráfico em horizontal
                title=f'Detalhamento das Ações do Programa {programa_selecionado}',
            )

            fig5.update_layout(
                yaxis={'categoryorder': 'total ascending'},            )

            st.plotly_chart(fig5, theme="streamlit", width='content')
except Exception as e:
    st.error(f"Erro ao carregar os dados tente voltar depois")
    logging.error(f"Erro ao carregar os dados: {e}")
    st.stop()

st.divider()

st.caption(f"🗓️ **Última coleta:** {data_ultima_atualizacao} &nbsp;&nbsp;|&nbsp;&nbsp; "
           f"⚠️ **Dados ausentes:** {dados_ausentes} &nbsp;&nbsp;|&nbsp;&nbsp; "
           f"[🏛️ **Acessar Fonte Oficial**]({url_orcamento})")






