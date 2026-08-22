# OpenCityMetrics

Transparência cidadã com dados abertos municipais. Este repositório reúne coletores (robôs), processadores e um dashboard em Streamlit para acompanhar gastos com servidores, obras, patrimônio e execução orçamentária.

> Importante: Projeto em fase Beta/Testes. A coleta automatizada pode enfrentar bloqueios de segurança, o que pode resultar em dados temporariamente desatualizados, faltantes ou corrompidos. Este painel tem caráter informativo e analítico — para validação legal, certidões ou denúncias (a fonte absoluta da verdade), consulte sempre o Portal da Transparência oficial da Prefeitura.

## Visão geral
- Dashboard em Streamlit com navegação por páginas (Home, Funcionários, Obras, Patrimônio, Orçamento).
- Robô agendador que coleta, trata e publica bases consolidadas em blob storage.
- Pipelines de processamento para padronização de colunas, conversões e deduplicação.

## Sobre o projeto
O OpenCityMetrics nasceu para traduzir dados governamentais complexos em informações acessíveis. A Home do painel explica o propósito e como navegar pelas seções:
- Despesas com Funcionários: evolução mensal, quantidade de servidores e proventos.
- Obras: andamento físico e financeiro, com percentuais e valores.
- Patrimônio: bens cadastrados e situação do inventário.
- Orçamento: comparação entre o valor orçado e o executado por ano.

### Desafios da automação (coleta)
- Transição de raspagem visual (simulação de navegação) para interceptação de APIs/requisições, buscando mais velocidade e resiliência.
- Restrições de segurança (firewalls) nos portais oficiais podem pausar a coleta automatizada em nuvem; estamos reforçando a robustez do robô.

### Próximos passos
1. Estabilidade e velocidade na coleta via API.
2. Base de dados padronizada e replicável para qualquer município.
3. API pública com snapshots de segurança.

## Acompanhe no YouTube
Estamos documentando a evolução técnica e as decisões de produto em uma playlist aberta. Inscreva-se e acompanhe pelo canal:
- Playlist do projeto: https://www.youtube.com/playlist?list=PLAs4Mo36_cVk
- Vídeos relacionados: https://youtu.be/b185IegnxS8 e https://youtu.be/bHBstagaHmk

Se preferir, acesse pelo link da playlist acima diretamente no canal do YouTube.

## Transparência e metodologia
- As coletas utilizam as páginas oficiais do Portal da Transparência da Prefeitura de Corupá/SC.
- O processamento padroniza colunas, converte datas e normaliza valores monetários para viabilizar análises.
- Os indicadores apresentados são informativos e não substituem os dados primários da fonte oficial.

## Pré‑requisitos
- Python 3.11+
- Pip (ou Poetry)

## Configuração
1. Clone o repositório.
2. Crie um arquivo `.env` na raiz com as variáveis necessárias (URLs do blob e token da nuvem):
   
   ```env
   # URLs públicas (blob) dos JSONs consolidados
   ARQUIVO_BASE_DESPESAS_FUNCIONARIOS_CORUPA=https://.../json/FuncionariosCorupa
   ARQUIVO_BASE_OBRAS_CORUPA=https://.../json/ObrasCorupa
   ARQUIVO_BASE_PATRIMONIO_CORUPA=https://.../json/PatrimonioCorupa
   ARQUIVO_BASE_ORCAMENTO_CORUPA=https://.../json/OrcamentoCorupa

   # Token para upload (Square Cloud Blob)
   TOKEN_HOSPEDAGEM=seu_token_aqui
   ```

3. Verifique/edite o arquivo de configuração em `data\config.json` (status das bases, URLs oficiais, última atualização, etc.).

## Instalação
Usando pip:
```bash
pip install -r requirements.txt
```

Usando Poetry:
```bash
poetry install
poetry shell
```

## Como executar
- Modo completo (dashboard + agendador de coletas):
  ```bash
  python main.py
  ```
  Isso inicia o Streamlit (porta 80 por padrão) e, após alguns segundos, o agendador (`agendador.py`).

- Apenas o dashboard:
  ```bash
  streamlit run dashboard/app.py
  ```

## Estrutura de pastas (resumo)
- `dashboard/` – App Streamlit (páginas em `dashboard\views\`).
- `collectors/` – Robôs de coleta por domínio (funcionários, obras, orçamento, patrimônio).
- `processors/` – Tratamento/padronização e publicação das bases.
- `services/` – Serviços (blob storage, cache de dados, etc.).
- `utils/` – Utilitários (logging, configuração e paths seguros).
- `data/` – Configurações e artefatos temporários durante o processamento.

## Testes
Em construção. Por ora, valide o carregamento das páginas do dashboard e o log de coletas em `logs\app.log`.

## Licença
Este projeto está licenciado sob os termos do arquivo `LICENSE` na raiz do repositório.


