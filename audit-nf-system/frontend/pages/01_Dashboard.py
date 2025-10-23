import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime, timedelta

# Importações locais
from components.sidebar import build_sidebar
from services.api_client import BackendClient
from components.charts import plot_timeline, plot_status_distribution

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard Detalhado",
    page_icon="📊",
    layout="wide"
)

# --- Inicialização (Garante que o cliente API exista) ---
if 'api_client' not in st.session_state:
    # Isso pode acontecer se o usuário carregar esta página diretamente
    st.session_state['api_client'] = BackendClient()
    st.session_state['user_info'] = {
        "name": "Usuário Mock",
        "role": "Auditor Fiscal",
        "last_login": (datetime.now() - timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")
    }

# --- Constrói a Sidebar ---
build_sidebar()

# --- Cache de Dados (ESTA É A CORREÇÃO) ---
# Aplicando o MESMO padrão de wrapper do app.py

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
    """
    try:
        return asyncio.run(_fetch_dashboard_summary_async())
    except Exception as e:
        st.error(f"Erro interno no asyncio.run: {e}")
        return None

# --- Título da Página ---
st.title("📊 Dashboard Detalhado")
st.markdown("Análise aprofundada das métricas de auditoria.")

# --- Carregamento dos Dados ---
summary_data = None
with st.spinner("Carregando métricas do dashboard..."):
    # 3. Chamamos a função síncrona cacheada
    summary_data = get_dashboard_summary_cached()

if not summary_data:
    st.error("Não foi possível carregar os dados do dashboard. Verifique o backend.")
    st.stop()

# --- Métricas Principais (KPIs) ---
st.header("Métricas Chave", divider="blue")

if "kpis" in summary_data:
    col1, col2, col3, col4 = st.columns(4)
    kpis = summary_data["kpis"]
    with col1:
        st.metric("Total NFs Processadas", kpis.get("total_nfs", 0))
    with col2:
        approval_rate = kpis.get("approval_rate", 0.0)
        st.metric("Taxa de Aprovação", f"{approval_rate:.1%}")
    with col3:
        st.metric("NFs Pendentes", kpis.get("pending_nfs", 0), delta=kpis.get("pending_delta", "0"), delta_color="inverse")
    with col4:
        st.metric("Auditadas (Últimas 24h)", kpis.get("last_24h", 0))
else:
    st.warning("KPIs não puderam ser carregados.")

st.divider()

# --- Gráficos Detalhados ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Volume de Auditoria (Últimos 7 dias)")
    if "timeline_data" in summary_data and summary_data["timeline_data"]:
        df_timeline = pd.DataFrame(summary_data["timeline_data"])
        df_timeline['data'] = pd.to_datetime(df_timeline['data'])
        
        fig_timeline = plot_timeline(df_timeline, x_col='data', y_col='volume', color_col='status')
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("Sem dados de timeline para exibir.")

with col2:
    st.subheader("Distribuição de Status (Geral)")
    if "timeline_data" in summary_data and summary_data["timeline_data"]:
        df_timeline = pd.DataFrame(summary_data["timeline_data"])
        
        # Agrupa os dados para o gráfico de pizza
        df_status_summary = df_timeline.groupby('status')['volume'].sum().reset_index()
        
        fig_pie = plot_status_distribution(df_status_summary, values_col='volume', names_col='status')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Sem dados de status para exibir.")