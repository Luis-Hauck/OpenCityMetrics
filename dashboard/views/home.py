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

st.markdown("### 📊 Acesse os Painéis")
st.write("Clique abaixo na base de dados que deseja explorar:")

# Cria duas colunas para os botões ficarem lado a lado no PC e empilhados no mobile
col1, col2 = st.columns(2)

with col1:
    # O caminho deve ser o exato nome do arquivo na sua pasta 'pages/'
    st.page_link("views/funcionarios.py", label="Despesas com os funcionários", icon="👥")
    st.page_link("views/patrimonio.py", label="Patrimônio", icon="🏢")

with col2:
    st.page_link("views/obras.py", label="Obras", icon="🏗️")
    st.page_link("views/orcamento.py", label="Orçado e Executado", icon="💰")

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