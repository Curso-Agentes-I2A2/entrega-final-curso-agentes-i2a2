# 🖥️ Prompt para Gerar Frontend (Streamlit)

**Instruções:** Copie este prompt e cole no Claude ou GPT-4 para gerar o código inicial do frontend.

---

## PROMPT:

```
Você é um especialista em Streamlit e Python. Preciso que você crie a estrutura inicial completa de um frontend Streamlit para um sistema de auditoria de notas fiscais brasileiras.

CONTEXTO DO PROJETO:
- Interface web para auditoria de notas fiscais
- Upload de XML/PDF de NF-e
- Visualização de resultados de auditoria
- Dashboard com métricas e gráficos
- Geração de notas fiscais sintéticas para testes
- Relatórios exportáveis
- Design moderno e profissional

REQUISITOS TÉCNICOS:
- Framework: Streamlit
- Gráficos: Plotly
- Tabelas: Pandas
- HTTP Client: httpx (async)
- Estilo: CSS customizado
- Multi-page app
- Session state para persistência

ESTRUTURA DE PASTAS:
```
frontend/
├── app.py                     # Página inicial (Home/Dashboard)
├── pages/
│   ├── 01_📊_Dashboard.py     # Dashboard com métricas
│   ├── 02_📤_Upload_NF.py     # Upload de notas fiscais
│   ├── 03_🔍_Auditoria.py     # Consulta de auditorias
│   ├── 04_🧪_NF_Sinteticas.py # Geração de NFs sintéticas
│   └── 05_📈_Relatorios.py    # Relatórios e análises
├── components/
│   ├── __init__.py
│   ├── sidebar.py             # Sidebar customizada
│   ├── charts.py              # Componentes de gráficos
│   └── tables.py              # Tabelas formatadas
├── services/
│   ├── __init__.py
│   └── api_client.py          # Cliente HTTP para Backend
├── utils/
│   ├── __init__.py
│   ├── formatters.py          # Formatadores de dados
│   └── validators.py          # Validações frontend
├── .streamlit/
│   └── config.toml            # Configurações Streamlit
├── assets/
│   └── styles.css             # CSS customizado
├── requirements.txt
└── README.md
```

POR FAVOR, GERE:

1. **app.py** - Página inicial/Home:
   - Configuração do app (set_page_config)
   - CSS customizado integrado
   - Título e descrição do sistema
   - Métricas principais em cards:
     * Total de NFs
     * Taxa de aprovação
     * NFs pendentes
     * Últimas 24h
   - Gráfico de tendência (últimos 7 dias)
   - Tabela de atividades recentes
   - Links rápidos para outras páginas
   - Sidebar com informações do usuário (mock)

2. **.streamlit/config.toml** - Configurações:
   - Tema customizado:
     * primaryColor: #1f77b4
     * backgroundColor: #ffffff
     * secondaryBackgroundColor: #f0f2f6
   - Server port: 8501
   - maxUploadSize: 10 (MB)

3. **pages/02_📤_Upload_NF.py** - Upload de NFs:
   - st.file_uploader para XML/PDF
   - Suporte a múltiplos arquivos
   - Preview do arquivo carregado
   - Opções de processamento:
     * Validar schema
     * Executar auditoria
     * Gerar relatório
   - Barra de progresso durante processamento
   - Exibição de resultados:
     * Status (aprovada/rejeitada)
     * Score de confiança
     * Irregularidades encontradas
   - Botão para baixar relatório PDF

4. **pages/03_🔍_Auditoria.py** - Consulta de auditorias:
   - Filtros:
     * Data (range picker)
     * Status (aprovada/rejeitada/pendente)
     * CNPJ do emitente
   - Tabela com resultados filtrados
   - Expansor para detalhes de cada auditoria
   - Gráfico de distribuição de status
   - Exportar para Excel

5. **pages/04_🧪_NF_Sinteticas.py** - Geração de NFs sintéticas:
   - Formulário de configuração:
     * Tipo (válida/inválida/suspeita)
     * Quantidade
     * Valor máximo
     * Estado (UF)
   - Botão "Gerar NFs"
   - Preview das NFs geradas
   - Download em lote (ZIP)
   - Estatísticas das NFs geradas

6. **pages/05_📈_Relatorios.py** - Relatórios e análises:
   - Seletor de período
   - Gráficos:
     * Pizza: distribuição de status
     * Barra: top fornecedores
     * Linha: evolução temporal
     * Heatmap: volume por estado
   - Tabela de métricas consolidadas
   - Exportar relatório completo

7. **services/api_client.py** - Cliente da API:
   - Classe BackendClient usando httpx
   - Métodos assíncronos:
     * upload_invoice(file) -> dict
     * get_invoices(filters) -> List[dict]
     * get_audit_result(invoice_id) -> dict
     * generate_synthetic(params) -> dict
   - Tratamento de erros
   - Timeout de 30s
   - Retry logic (3 tentativas)
   - Mock quando backend indisponível

8. **components/sidebar.py** - Sidebar customizada:
   - Logo do sistema
   - Menu de navegação
   - Informações do usuário:
     * Nome
     * Cargo
     * Último acesso
   - Estatísticas rápidas
   - Botão de logout

9. **components/charts.py** - Componentes de gráficos:
   - plot_status_distribution(data) -> plotly figure
   - plot_timeline(data) -> plotly figure
   - plot_top_suppliers(data) -> plotly figure
   - Todos usando Plotly para interatividade

10. **utils/formatters.py** - Formatadores:
    - format_currency(value: float) -> str: "R$ 10.000,00"
    - format_cnpj(cnpj: str) -> str: "12.345.678/0001-90"
    - format_date(date: str) -> str: "18/10/2024"
    - format_status(status: str) -> str com emoji

11. **utils/validators.py** - Validações frontend:
    - validate_xml_file(file) -> bool
    - validate_cnpj_format(cnpj: str) -> bool
    - Validações básicas antes de enviar ao backend

12. **CSS customizado** (em app.py):
    - Cards com sombra
    - Botões estilizados
    - Tabelas responsivas
    - Cores do tema corporativo

13. **requirements.txt**:
    - streamlit
    - plotly
    - pandas
    - httpx
    - python-dotenv
    - openpyxl (para export Excel)

FUNCIONALIDADES IMPORTANTES:

14. **Session State**:
    - Armazenar uploads
    - Cache de dados da API
    - Estado de filtros
    - Histórico de navegação

15. **Mock de dados**:
    - Quando backend não disponível
    - Dados fictícios para demonstração
    - Permite desenvolvimento independente

EXEMPLO DE USO DO API CLIENT:

```python
# services/api_client.py
import httpx
import os

class BackendClient:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.timeout = 30.0
    
    async def upload_invoice(self, file_bytes: bytes, filename: str) -> dict:
        """Upload de nota fiscal"""
        try:
            async with httpx.AsyncClient() as client:
                files = {"file": (filename, file_bytes)}
                response = await client.post(
                    f"{self.base_url}/api/invoices/upload",
                    files=files,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError:
            # Mock quando backend não disponível
            return {
                "id": "mock-123",
                "status": "processando",
                "message": "Upload realizado com sucesso (mock)"
            }
```

DESIGN E UX:

- Use st.columns para layouts responsivos
- Adicione st.expander para informações adicionais
- Use st.tabs para organizar conteúdo
- Implemente loading states com st.spinner
- Adicione st.success/warning/error para feedback
- Use st.metric para KPIs
- Implemente caching com @st.cache_data
- Adicione tooltips explicativos

EXEMPLO DE PÁGINA:

```python
# pages/02_📤_Upload_NF.py
import streamlit as st
from services.api_client import BackendClient

st.set_page_config(page_title="Upload de NF", page_icon="📤")
st.title("📤 Upload de Nota Fiscal")

# Upload
uploaded_file = st.file_uploader(
    "Escolha o arquivo XML da NF-e",
    type=["xml", "pdf"],
    help="Formatos aceitos: XML (NF-e) ou PDF"
)

if uploaded_file:
    # Preview
    st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
    
    col1, col2 = st.columns([2, 1])
    with col2:
        st.info(f"**Tamanho:** {uploaded_file.size / 1024:.2f} KB")
    
    # Opções
    with st.expander("⚙️ Opções de Processamento"):
        validate_schema = st.checkbox("Validar Schema XML", value=True)
        run_audit = st.checkbox("Executar Auditoria", value=True)
        generate_report = st.checkbox("Gerar Relatório", value=True)
    
    # Processar
    if st.button("🚀 Processar", type="primary"):
        with st.spinner("Processando nota fiscal..."):
            client = BackendClient()
            result = await client.upload_invoice(
                uploaded_file.read(),
                uploaded_file.name
            )
            
            st.success("✅ Processamento concluído!")
            
            # Resultados
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", result.get("status", "N/A"))
            with col2:
                st.metric("Confiança", f"{result.get('confidence', 0):.0%}")
            with col3:
                st.metric("Irregularidades", len(result.get("issues", [])))
```

IMPORTANTE:
- Use async/await com asyncio.run() nas páginas Streamlit
- Implemente cache de dados para performance
- Adicione tratamento de erros robusto
- Use session_state para estado da aplicação
- Implemente mock completo para desenvolvimento offline
- Adicione logs de debug
- Use type hints
- Documente componentes

FORMATO DE RESPOSTA:
Gere cada arquivo completo, funcional e pronto para uso. Inclua mocks para trabalhar sem backend.
```

---

## TESTE:

```bash
cd frontend
pip install -r requirements.txt

# Configurar backend URL
echo "BACKEND_URL=http://localhost:8000" > .env

# Iniciar
streamlit run app.py

# Acessar: http://localhost:8501
```