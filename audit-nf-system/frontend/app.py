import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio
from datetime import datetime, timedelta

# Importações locais
from components.sidebar import build_sidebar
from services.api_client import BackendClient
from utils.formatters import format_currency
from components.charts import plot_timeline

# --- Configuração da Página ---
# Usamos "wide" para um layout de dashboard mais moderno
st.set_page_config(
    page_title="Auditor NF-e | Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Carregar CSS Customizado ---
# Injetando CSS diretamente como solicitado
def load_css():
    """Carrega o CSS customizado para aplicar estilos."""
    st.markdown("""
        <style>
            /* --- Métricas (Cards) --- */
            /* Targeta os cards de métrica do Streamlit */
            div[data-testid="stMetric"] {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease-in-out;
            }
            
            div[data-testid="stMetric"]:hover {
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
                transform: translateY(-2px);
            }
            
            /* Valor da métrica */
            div[data-testid="stMetricValue"] {
                font-size: 2.5em;
                font-weight: 600;
                color: #1f77b4; /* Cor primária */
            }
            
            /* Label da métrica */
            div[data-testid="stMetricLabel"] {
                font-size: 1.1em;
                font-weight: 500;
                color: #555;
            }

            /* --- Botões --- */
            .stButton > button {
                border-radius: 8px;
                font-weight: 600;
                padding: 10px 20px;
                transition: all 0.3s ease;
            }
            
            /* Botão primário */
            .stButton > button[kind="primary"] {
                background-color: #1f77b4;
                color: white;
                border: 2px solid #1f77b4;
            }
            .stButton > button[kind="primary"]:hover {
                background-color: #155a8a;
                border-color: #155a8a;
            }
            
            /* Botão secundário */
            .stButton > button[kind="secondary"] {
                background-color: transparent;
                color: #1f77b4;
                border: 2px solid #1f77b4;
            }
            .stButton > button[kind="secondary"]:hover {
                background-color: #f0f2f6;
                color: #155a8a;
                border-color: #155a8a;
            }

            /* --- Tabelas (Dataframes) --- */
            .stDataFrame {
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
            }
            
            /* --- Sidebar --- */
            div[data-testid="stSidebarNav"] {
                /* Adiciona um espaçamento no topo do menu de navegação */
                margin-top: 100px; 
            }
        </style>
    """, unsafe_allow_html=True)

load_css()

# --- Inicialização do Session State ---
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = {
        "name": "Usuário Mock",
        "role": "Auditor Fiscal",
        "last_login": (datetime.now() - timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")
    }
if 'api_client' not in st.session_state:
    st.session_state['api_client'] = BackendClient()

# --- Constrói a Sidebar ---
# A função build_sidebar é chamada em todas as páginas
build_sidebar()

# --- Cache de Dados ---

# 1. Função Async (sem decorator)
async def _fetch_dashboard_summary_async():
    """Busca dados resumidos do dashboard no backend."""
    client = st.session_state['api_client']
    return await client.get_dashboard_summary()

# 2. Função Sync (com decorator) que chama a async
@st.cache_data(ttl=600)  # Cache de 10 minutos
def get_dashboard_summary_cached():
    """
    Wrapper síncrono para cachear os dados do dashboard.
    Usa asyncio.run() internamente para executar o código async.
    """
    try:
        return asyncio.run(_fetch_dashboard_summary_async())
    except Exception as e:
        st.error(f"Erro interno no asyncio.run: {e}")
        return None # Retorna None para o chamador tratar

# --- Título da Página ---
st.title("🏠 Painel de Controle Principal")
st.markdown("Visão geral do status de auditoria das notas fiscais da sua empresa.")

# --- Carregamento dos Dados ---
summary_data = None
with st.spinner("Carregando métricas do dashboard..."):
    # 3. Chamamos a função síncrona cacheada
    summary_data = get_dashboard_summary_cached()

# --- Métricas Principais (KPIs) ---
st.header("Métricas Chave", divider="blue")

if summary_data and "kpis" in summary_data:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total NFs Processadas",
            value=summary_data["kpis"].get("total_nfs", 0)
        )
    with col2:
        approval_rate = summary_data["kpis"].get("approval_rate", 0.0)
        st.metric(
            label="Taxa de Aprovação",
            value=f"{approval_rate:.1%}",
            delta=f"{(approval_rate - 0.9):.1%}", # Delta mockado
            delta_color="normal"
        )
    with col3:
        st.metric(
            label="NFs Pendentes",
            value=summary_data["kpis"].get("pending_nfs", 0),
            delta=summary_data["kpis"].get("pending_delta", "0"),
            delta_color="inverse"
        )
    with col4:
        st.metric(
            label="Auditadas (Últimas 24h)",
            value=summary_data["kpis"].get("last_24h", 0)
        )
else:
    st.error("Falha ao carregar os KPIs do dashboard. Verifique a conexão com o backend ou os dados mockados.")

st.divider()

# --- Gráficos e Tabelas ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Volume de Auditoria (Últimos 7 dias)")
    if summary_data and "timeline_data" in summary_data and summary_data["timeline_data"]:
        df_timeline = pd.DataFrame(summary_data["timeline_data"])
        df_timeline['data'] = pd.to_datetime(df_timeline['data'])
        
        # Usando o componente de gráfico
        fig = plot_timeline(df_timeline, x_col='data', y_col='volume', color_col='status')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de timeline para exibir.")

with col2:
    st.subheader("Atividade Recente")
    if summary_data and "recent_activity" in summary_data and summary_data["recent_activity"]:
        df_recent = pd.DataFrame(summary_data["recent_activity"])
        
        # Formatando para exibição
        df_recent_display = df_recent.copy()
        if 'valor' in df_recent_display.columns:
            df_recent_display['valor'] = df_recent_display['valor'].apply(format_currency)
        
        st.dataframe(
            df_recent_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.TextColumn("ID"),
                "status": st.column_config.TextColumn("Status"),
                "valor": st.column_config.TextColumn("Valor"),
            }
        )
    else:
        st.info("Nenhuma atividade recente.")

# --- Links Rápidos (CORREÇÃO AQUI) ---
st.header("Ações Rápidas", divider="blue")
col1, col2, col3 = st.columns(3)

with col1:
    # Correção: Removido "pages/" do caminho
    if st.button("📤 Enviar Nova NF-e", use_container_width=True, type="primary"):
        st.switch_page("pages/02_Upload_NF.py")
with col2:
    # Correção: Removido "pages/" do caminho
    if st.button("🔍 Consultar Auditorias", use_container_width=True):
        st.switch_page("pages/03_Auditoria.py")
with col3:
    # Correção: Removido "pages/" do caminho
    if st.button("📈 Ver Relatórios", use_container_width=True):
        st.switch_page("pages/05_Relatorios.py")