import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.express as px
import logging

loogger = logging.getLogger(__name__)

from processors.limpar_dados import formatar_reais
from services.cloud_storage import obter_dados
from utils.config import load_config, obter_caminho_arquivo

load_dotenv()
caminho_config = obter_caminho_arquivo('data', 'config.json')
config = load_config(caminho_config)

# Carrega o dataframe base
url = os.getenv('ARQUIVO_BASE_DESPESAS_FUNCIONARIOS_CORUPA')
sucesso, df = obter_dados(url)
# REMOVER ASSIM QUE A COLETA ESTIVER DISPONIVEL
df['data'] = pd.to_datetime(df['data'], unit='ms', errors='coerce')

dados_orcamento = config['SC']['Corupa']['base_dados']['funcionarios']
data_ultima_atualizacao = dados_orcamento['ultima_atualizacao']
dados_ausentes = dados_orcamento['dados_ausentes']

if not sucesso:
    st.warning('Falha ao carregar os dados, tente novamente mais tarde')
    st.stop()

st.title('Despesas com funcionários')


tab1, tab2, tab3 = st.tabs(["Visão geral", "Concentração de Gastos", 'Vínculos e Cargos'])

try:
    with tab1:

        # pega a data de hoje
        data_mais_recente = df.nlargest(1, 'data')['data'].iloc[0]
        mes_atual = data_mais_recente.month
        df_data_ref = df[df['data'] == data_mais_recente]

        # Métrica para comaparar o mês anterior ao atual
        mes_anterior = data_mais_recente.month - 1
        ano_comparativo = data_mais_recente.year
        if data_mais_recente.month == 1:
            mes_anterior = 12
            ano_comparativo = data_mais_recente.year - 1

        data_mes_anterior = pd.to_datetime(f'01/{mes_anterior}/{ano_comparativo}', dayfirst=True)
        df_mes_anterior = df[df['data'] == data_mes_anterior]

        n_funcionarios_atual = df_data_ref['Funcionário'].nunique()
        n_funcionarios_mes_anterior = df_mes_anterior['Funcionário'].nunique()

        diferenca_de_funcinarios = (n_funcionarios_atual - n_funcionarios_mes_anterior) / n_funcionarios_mes_anterior

        # Calculos percentual de funcionarios
        populacao = 15912.00
        percentual_de_trabalhadores = (n_funcionarios_atual / populacao)
        percentual_de_trabalhadores_mes_anterior = (n_funcionarios_atual  - n_funcionarios_mes_anterior) / populacao

        # Calculando gastos totais
        gastos_mes_atual = df_data_ref['Proventos'].sum()
        gastos_mes_anterior = df_mes_anterior['Proventos'].sum()
        variacao_gastos = gastos_mes_atual - gastos_mes_anterior

        col1, col2 = st.columns(2)

        col2.metric(label='Número de funcionários',
                    value=n_funcionarios_atual,
                    delta=f"{diferenca_de_funcinarios:.2%}",
                    delta_color='inverse'
                    )

        col1.metric(label='Gastos nesse mês',
                    value=f'{formatar_reais(gastos_mes_atual)}',
                    delta=f'{formatar_reais(variacao_gastos)}',
                    )

        st.metric(label='Habitantes atuando',
                    value=f'{percentual_de_trabalhadores:.2%}',
                    delta=f"{percentual_de_trabalhadores_mes_anterior:.2%}",
                    delta_color='inverse')

        # Cria uma copia do df de referencia com as colunas a serem exibidas
        view_df = df_data_ref.drop(columns=['Líquido'])
        view_df['Proventos'] = view_df['Proventos'].apply(formatar_reais)
        colunas_visiveis = ['Nome Funcionário', 'Cargo', 'Regime de Trabalho', 'Proventos']
        df_visivel = view_df[colunas_visiveis]

        evento = st.dataframe(
            df_visivel,
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

            df_detalhado = view_df.iloc[indice2]

            st.write('🔍 Ficha Completa')
            st.dataframe(
                df_detalhado,
                width='stretch'
            )


    with tab2:
        # Lista com os anos disponiveis
        anos_disponiveis = sorted(df['data'].dt.year.unique(), reverse=True)
        meses = {
            'Todos': 0,
            'Janeiro': 1,
            'Fevereiro': 2,
            'Março': 3,
            'Abril': 4,
            'Maio': 5,
            'Junho': 6,
            'Julho': 7,
            'Agosto': 8,
            'Setembro': 9,
            'Outubro': 10,
            'Novembro': 11,
            'Dezembro': 12
        }

        ano_selecionado = st.selectbox('Selecione o ano', anos_disponiveis)
        mes_selecionado = st.selectbox('Selecione o mês', list(meses.keys()), help='Ao selecionar todos Será considerado a média de proventos de todos os meses')

        periodo_selcionado = ano_selecionado


        df_ano = df[df['data'].dt.year == ano_selecionado]

        if mes_selecionado != 'Todos':
            # Se não foi filtrado todo o período aplicamos um filtro para o mês selecionado daquele ano
            mes_ano = pd.to_datetime(f'01-{meses[mes_selecionado]}-{ano_selecionado}', dayfirst=True)
            df_ano = df[df['data'] == mes_ano]
            periodo_selcionado = f'{mes_selecionado} de {ano_selecionado}'

        df_agrupado_ano = df_ano.groupby('Nome Funcionário').agg(
            custo_anual=('Proventos', 'sum'),
            meses_pagos=('data', 'count')
        ).reset_index()

        # Custo médio por folha daquele ano específico
        df_agrupado_ano['media_mensal_no_ano'] = df_agrupado_ano['custo_anual'] / df_agrupado_ano['meses_pagos']

        # Distribuiçaõ de frequencia

        df_dados_ano = df_agrupado_ano

        fig_dist = px.histogram(
            df_dados_ano,
            x="media_mensal_no_ano",
            nbins=25,
            labels={"media_mensal_no_ano": "Faixa de Proventos (R$)", "count": "Qtd. de Funcionários"}
        )

        fig_dist.update_layout(
            yaxis_title="Número de Servidores"
        )

        st.plotly_chart(fig_dist, theme="streamlit", width='content')



        # análise dos 10 maiores custos
        top10_do_ano = df_agrupado_ano.nlargest(10, 'media_mensal_no_ano')

        # Pareto Anual
        custo_top10_ano = top10_do_ano['custo_anual'].sum()
        custo_total_prefeitura_ano = df_ano['Proventos'].sum()
        pareto_ano = custo_top10_ano / custo_total_prefeitura_ano


        st.info(f"""
            **Concentração de Gastos em {periodo_selcionado}:** Os 10 servidores com as maiores médias de proventos custaram **R$ {custo_top10_ano:,.2f}** aos cofres públicos neste período.  
            Isso representou **{pareto_ano:.2%}** de todo o gasto com funcionários da prefeitura em {periodo_selcionado}.
            """)


        fig = px.bar(top10_do_ano,
                     x='Nome Funcionário',
                     y='media_mensal_no_ano',
                     labels={
                         "Nome Funcionário": "Servidor Municipal",
                         "media_mensal_no_ano": "Média de Proventos"
                     }
                     )

        st.plotly_chart(fig, theme="streamlit", width='content')

    with tab3:

        ano_selecionado_tab3 = st.selectbox('Selecione o ano:', anos_disponiveis)
        mes_selecionado_tab3 = st.selectbox('Selecione o mês:', list(meses.keys()))

        periodo_selcionado = ano_selecionado_tab3

        mapeamento_regimes = {
            r'.*Comis.*': 'Cargos Comissionados',
            r'.*Concursado.*': 'Concursados (Efetivos)',
            r'.*Contrato.*Determ.*': 'Contratos Temporários',
            r'.*Eletivo.*': 'Prefeito/Vice-Prefeito',
            r'.*Secretarios.*': 'Cargos Comissionados'
        }



        df_ano_tab3 = df[df['data'].dt.year == ano_selecionado_tab3]

        if mes_selecionado_tab3 != 'Todos':
            # Se não foi filtrado todo o período aplicamos um filtro para o mês selecionado daquele ano
            mes_ano_tab3 = pd.to_datetime(f'01-{meses[mes_selecionado_tab3]}-{ano_selecionado_tab3}', dayfirst=True)
            df_ano_tab3 = df[df['data'] == mes_ano_tab3]

        df_ano_tab3['Regime_tratado'] = df_ano_tab3['Regime de Trabalho'].replace(mapeamento_regimes, regex=True)

        # Se sobrar algum regime que o regex não pegou,
        # ele mantém o nome original para não quebrar a sua tabela.
        df_ano_tab3['Regime_tratado'] = df_ano_tab3['Regime_tratado'].fillna(df_ano_tab3['Regime de Trabalho'])

        # Cargos escolhidos
        cargos_alvo = ['Secretários', 'Cargos Comissionados']

        df_casta = df_ano_tab3[df_ano_tab3['Regime_tratado'].isin(cargos_alvo)]

        custo_comissionados = df_casta['Proventos'].sum()
        func_comissionados = df_casta['Funcionário'].nunique()

        custo_cidade_ano = df_ano_tab3['Proventos'].sum()

        func_cidade_ano = df_ano_tab3['Funcionário'].nunique()

        fatia_pessoas = func_comissionados / func_cidade_ano
        fatia_dinheiro = custo_comissionados / custo_cidade_ano

        st.info(f"""
        Os cargos comissionados(incluido secretários) representam **{fatia_pessoas:.1%}** do quadro de servidores, e consomem **{fatia_dinheiro:.1%}** do gasto total do período.
        """)

        df_tabela_regimes = df_ano_tab3.groupby('Regime_tratado').agg(
            total_gasto=('Proventos', 'sum'),
            n_servidores=('Nome Funcionário', 'nunique')
        ).reset_index().sort_values('total_gasto', ascending=False)


        fig_bar_cargos = px.bar(
            df_tabela_regimes,
            x="Regime_tratado",
            y="total_gasto",
            labels={
                "Regime_tratado": "Cargo",
                "total_gasto": "Custo (R$)"
            }
        )

        st.plotly_chart(fig_bar_cargos, theme="streamlit", width='content')

        # tabela com os % de gastos
        gasto_total_do_ano = df_ano_tab3['Proventos'].sum()

        df_tabela_regimes['pct_gasto'] = df_tabela_regimes['total_gasto'] / gasto_total_do_ano *100

        # Ordenamos do maior gasto para o menor
        df_tabela_regimes = df_tabela_regimes.sort_values(by='total_gasto', ascending=False)

        st.dataframe(
            df_tabela_regimes,
            column_config={
                "Regime_tratado": "Categoria",
                "total_gasto": st.column_config.NumberColumn("Total Gasto", format="R$ %,.2f"),
                "n_servidores": st.column_config.NumberColumn("Nº de Servidores", format="%d"),
                "pct_gasto": st.column_config.NumberColumn("% do Orçamento", format="%.2f%%")
            },
            hide_index=True,
            width='content'
        )
        st.caption("ℹ️ **Nota Metodológica:** A soma da coluna 'Nº de Servidores' pode ser superior ao total de indivíduos físicos únicos contratados no ano. Isso ocorre porque um mesmo servidor pode ter migrado de regime durante o período (ex: encerramento de contrato temporário seguido de nomeação em concurso público), sendo contabilizado em ambas as categorias que ocupou.")

except Exception as e:
    st.error(f"Erro ao carregar os dados tente voltar depois")
    logging.error(f"Erro ao carregar os dados tente voltar depois: {e}")

if dados_ausentes > 0:
    st.info(f"⚠️ **Nota de Transparência:** Aproximadamente {dados_ausentes} registros fornecidos pela prefeitura continham erros de "
            "formatação (linhas corrompidas) e não puderam ser lidos."
            , icon="ℹ️")

st.info(f'Última coleta dos dados: {data_ultima_atualizacao}')
















