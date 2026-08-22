import streamlit as st
from utils.config import obter_caminho_arquivo, load_config

# Carrega configurações do projeto (datas de atualização, status das bases, etc.)
try:
    caminho_config = obter_caminho_arquivo('data', 'config.json')
    config = load_config(caminho_config)
    dados_sc = config.get('SC', {}).get('Corupa', {}).get('base_dados', {})
except Exception:
    dados_sc = {}

st.title('OpenCityMetrics — Painel de Transparência Cidadã')
st.caption('Monitoramento de gastos públicos, obras, patrimônio e orçamento — com dados da Prefeitura de Corupá/SC')


@st.dialog("⚠️ Aviso Importante sobre os Dados")
def popup_avisos():
    st.markdown(
        """    
    * **Apenas Poder Executivo:** Os dados deste painel refletem exclusivamente a **Prefeitura Municipal** (secretarias, fundos e autarquias). O Poder Legislativo (Câmara de Vereadores) possui orçamento e portal próprios, não estando incluído aqui.
    * **Limitações Técnicas:** A coleta automatizada enfrenta bloqueios de segurança. Por isso, os dados atuais podem estar temporariamente desatualizados ou incompletos.
    * **Uso Informativo:** Este painel não substitui as fontes oficiais. Para validação legal, certidões ou denúncias (a fonte absoluta da verdade), consulte sempre o Portal da Transparência da Prefeitura.
    """
    )
    # Botão para fechar o pop-up
    if st.button("Entendi, acessar o painel"):
        st.session_state.aviso_lido = True
        st.rerun()  # Recarrega a página para fechar a janela


# 2. Verifica se a pessoa já leu. Se não, mostra o pop-up!
if "aviso_lido" not in st.session_state:
    popup_avisos()
st.markdown(
    """
    Bem-vindo! Este painel foi criado para facilitar o acesso e a compreensão dos dados públicos municipais. 
    Aqui você encontra visualizações simples, comparações e indicadores que ajudam a responder perguntas como:
    - Quanto a Prefeitura gasta com servidores? 
    - Quais são as obras em andamento e seu andamento físico/financeiro? 
    - Qual é o patrimônio público cadastrado? 
    - O que foi orçado e o que está sendo executado ao longo do ano?
    """
)

# Seção Sobre
with st.expander("🚀 Sobre este projeto, desafios e comunidade", expanded=False):
    st.markdown(
        """
        ### O Propósito
        O **OpenCityMetrics** nasceu para traduzir dados e planilhas governamentais complexas em informações acessíveis. O objetivo final é criar uma infraestrutura de dados padronizada que possa ser replicada em qualquer cidade do Brasil.

        ### O Desafio da Automação (Web Scraping)
        Coletar dados de sistemas governamentais legados não é uma tarefa trivial. Atualmente, o sistema passa por uma reestruturação para superar duas barreiras principais:
        - **Da raspagem visual para APIs:** A versão inicial simula a navegação humana (Playwright). Apesar de intuitiva, a lentidão na renderização, iframes e pop-ups imprevisíveis tornavam a coleta frágil. A solução em andamento é migrar para a interceptação direta das requisições de rede (via `httpx`).
        - **Sistemas de Segurança:** Firewalls rigorosos identificam automações de nuvem, o que ocasionalmente pausa a nossa coleta diária. Desenvolver resiliência contra essas defesas é o foco atual.

        ### Próximos Passos
        1. **Estabilidade e Velocidade:** Finalizar a transição para coleta via API, tornando o robô invisível e mais rápido.
        2. **Banco de Dados Padronizado:** Criar uma estrutura de dados universal, contornando o fato de que cada prefeitura possui um layout diferente.
        3. **OpenCity API:** Disponibilizar uma API pública do projeto e manter *snapshots* de segurança para os dias em que os portais oficiais saírem do ar.

        ---
        ### 🤝 Junte-se ao Projeto!
        Este é um projeto de **código aberto** em fase de estruturação. Se você se interessa por automação, análise de dados ou transparência pública, toda ajuda é bem-vinda (desde sugerir ideias até escrever código).
        """
    )

    # Botões de comunidade lado a lado
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.link_button("💻 Contribua no GitHub", "https://github.com/Luis-Hauck/OpenCityMetrics",
                       use_container_width=True)
    with btn_col2:
        st.link_button("💬 Participe do Discord", "https://discord.gg/Sc9Z84V3nU", use_container_width=True)

st.subheader('O que você vai encontrar por aqui')
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """
        - Despesas com Funcionários: evolução mensal, quantidade de servidores e proventos.
        - Obras: lista de obras, percentuais de execução e valores empenhados/pagos.
        """
    )
with col2:
    st.markdown(
        """
        - Patrimônio: bens cadastrados e situação do inventário.
        - Orçamento: comparação entre o valor orçado e o executado por ano.
        """
    )

st.divider()

st.subheader('Resumo das bases de dados')
st.info("Clique nos blocos abaixo para visualizar os detalhes da última atualização de cada base.")


# Helper para montar cartões-resumo dentro de EXPANDERS
def cartao_base(titulo: str, chave: str, descricao: str):
    base = dados_sc.get(chave, {}) if isinstance(dados_sc, dict) else {}
    ativo = base.get('ativo', False)
    ultima = base.get('ultima_atualizacao', '—')
    faltantes = base.get('dados_ausentes', '—')
    url = base.get('url', None)

    # Cria o bloco sanfonado com o Título
    with st.expander(f"📊 {titulo}", expanded=False):
        st.write(descricao)

        cols = st.columns(3)
        with cols[0]:
            st.metric('Status', 'Ativo' if ativo else 'Indisponível')
        with cols[1]:
            st.metric('Última atualização', f"{ultima}")
        with cols[2]:
            st.metric('Dados ausentes', f"{faltantes}")

        if url:
            st.link_button('Acessar Fonte Oficial', url)


cartao_base(
    'Despesas com Funcionários',
    'funcionarios',
    'Informações sobre vínculo, cargos e proventos, com foco em evolução e distribuição dos gastos.'
)

cartao_base(
    'Obras',
    'obras',
    'Acompanhamento das obras públicas: valores, prazos e percentuais de execução.'
)

cartao_base(
    'Patrimônio',
    'patrimonio',
    'Bens públicos cadastrados. A métrica de dados ausentes indica campos ainda não informados/validados.'
)

cartao_base(
    'Orçamento — Orçado x Executado',
    'orcamento',
    'Comparativo por ano e por categoria econômica entre o que foi planejado e o que está sendo executado.'
)

st.divider()

# Seção Youtube

st.subheader('Acompanhe a construção do projeto')
st.markdown("Assista à playlist no YouTube documentando os desafios e a evolução da automação deste painel.")

# Cria duas colunas para não ocupar a tela toda
video_col1, video_col2 = st.columns(2)

with video_col1:
    st.video("https://youtu.be/b185IegnxS8")

with video_col2:
    st.video("https://youtu.be/bHBstagaHmk")

st.markdown("📺 **[Clique aqui para ver a playlist completa no canal](https://www.youtube.com/playlist?list=PLAs4Mo36_cVk)**")

st.divider()

st.subheader('Transparência e metodologia')
st.markdown(
    """
    - As coletas utilizam as páginas oficiais do Portal da Transparência da Prefeitura de Corupá/SC.
    - O processamento padroniza colunas, converte datas e normaliza valores monetários para viabilizar análises.
    - Indicadores apresentados aqui são informativos e não substituem os dados primários da fonte oficial.
    """
)

st.caption('Projeto aberto — contribuições e sugestões são bem-vindas.')