import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio
from datetime import datetime, timedelta
from io import BytesIO

# Importações locais
from components.sidebar import build_sidebar
from services.api_client import BackendClient
from components.charts import (
    plot_status_distribution,
    plot_top_suppliers,
    plot_timeline
)
from utils.formatters import format_currency

# --- Configuração da Página ---
st.set_page_config(
    page_title="Relatórios e Análises",
    page_icon="📈",
    layout="wide"
)

# --- Sidebar ---
build_sidebar()

# --- Inicialização ---
if 'api_client' not in st.session_state:
    st.session_state['api_client'] = BackendClient()

client = st.session_state['api_client']

# --- Cache de Dados ---
@st.cache_data(ttl=900)
def fetch_report_data(start_date, end_date):
    """Busca dados consolidados para os relatórios (versão síncrona)."""
    filters = {"start_date": str(start_date), "end_date": str(end_date)}
    return asyncio.run(client.get_detailed_analytics(filters))

# --- Função para Excel ---
@st.cache_data
def generate_excel_report(data_dict):
    """Gera um relatório Excel com múltiplas abas."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(data_dict["metrics"]).to_excel(writer, index=False, sheet_name='Metricas_Consolidadas')
        pd.DataFrame(data_dict["status_distribution"]).to_excel(writer, index=False, sheet_name='Distribuicao_Status')
        pd.DataFrame(data_dict["top_suppliers_value"]).to_excel(writer, index=False, sheet_name='Top_Fornecedores_Valor')
        pd.DataFrame(data_dict["top_suppliers_issues"]).to_excel(writer, index=False, sheet_name='Top_Fornecedores_Rejeitadas')
        pd.DataFrame(data_dict["timeline_data"]).to_excel(writer, index=False, sheet_name='Evolucao_Temporal')
        pd.DataFrame(data_dict["geo_data"]).to_excel(writer, index=False, sheet_name='Dados_Geograficos')
    return output.getvalue()

# --- Título e Filtros ---
st.title("📈 Relatórios e Análises")
st.markdown("Gere relatórios consolidados e analise tendências de auditoria.")

# Filtros de Período
st.subheader("Selecione o Período do Relatório", divider="blue")
end_date = datetime.now().date()
start_date = end_date - timedelta(days=90) # Padrão de 90 dias

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    start_date = st.date_input("Data Inicial", start_date)
with col2:
    end_date = st.date_input("Data Final", end_date)

# Botão para gerar
if st.button("Gerar Relatório", type="primary"):
    if start_date > end_date:
        st.error("Erro: A data inicial não pode ser posterior à data final.")
    else:
        # --- Carregamento dos Dados ---
        with st.spinner(f"Gerando relatório de {start_date} até {end_date}..."):
            report_data = asyncio.run(fetch_report_data(start_date, end_date))
            st.session_state['report_data'] = report_data

# --- Exibição dos Relatórios ---
if 'report_data' in st.session_state:
    report_data = st.session_state['report_data']
    
    # --- Métricas Consolidadas ---
    st.subheader("Métricas Consolidadas", divider="blue")
    metrics = report_data.get('metrics', {})
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total NFs no Período", metrics.get('total_nfs', 0))
    col2.metric("Valor Total Auditado", format_currency(metrics.get('total_value', 0)))
    col3.metric("Total Rejeitado", format_currency(metrics.get('total_rejected_value', 0)))
    col4.metric("Taxa de Rejeição (Valor)", f"{metrics.get('rejection_rate_value', 0):.2%}")

    st.divider()

    # --- Abas (Tabs) com Gráficos ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Distribuição de Status",
        "🏭 Top Fornecedores",
        "📉 Evolução Temporal",
        "🗺️ Análise Geográfica (Heatmap)"
    ])

    with tab1:
        st.subheader("Distribuição de Status (Consolidado)")
        df_status = pd.DataFrame(report_data["status_distribution"])
        fig_pie = plot_status_distribution(df_status, 
                                           names_col='status', 
                                           values_col='count',
                                           title="Status de Auditoria no Período")
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.subheader("Top Fornecedores por Valor Total")
        df_suppliers = pd.DataFrame(report_data["top_suppliers_value"])
        fig_bar = plot_top_suppliers(df_suppliers, 
                                     x_col='valor_total', 
                                     y_col='fornecedor',
                                     title="Top 10 Fornecedores (Valor)",
                                     orientation='h')
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.subheader("Evolução Temporal do Volume Auditado")
        df_timeline = pd.DataFrame(report_data["timeline_data"])
        df_timeline['data'] = pd.to_datetime(df_timeline['data'])
        
        fig_line = plot_timeline(df_timeline, 
                                 x_col='data', 
                                 y_col='volume', 
                                 color_col='status',
                                 title="Volume de NFs por Dia e Status")
        st.plotly_chart(fig_line, use_container_width=True)
    
    with tab4:
        st.subheader("Heatmap de Volume por Estado (Mock)")
        st.info("Esta visualização (Choropleth) requer um GeoJSON do Brasil.")
        
        df_map_data = pd.DataFrame(report_data["geo_data"])
        # Mock de Heatmap
        fig_map = px.bar(
            df_map_data,
            x='uf',
            y='volume',
            color='uf',
            title="Volume de NFs por Estado (Gráfico de Barras - Mock)"
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # --- Exportação ---
    st.subheader("Exportar Relatório Completo", divider="blue")
    st.markdown("Baixe todos os dados consolidados deste relatório em um único arquivo Excel.")
    
    excel_file = generate_excel_report(report_data)
    
    st.download_button(
        label="Baixar Relatório Completo (.xlsx)",
        data=excel_file,
        file_name=f"Relatorio_Auditoria_{start_date}_a_{end_date}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )