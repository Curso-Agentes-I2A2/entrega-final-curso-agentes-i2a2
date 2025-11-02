import streamlit as st # type: ignore
import pandas as pd # type: ignore
import asyncio
from datetime import datetime, timedelta
from io import BytesIO

# Importações locais
from components.sidebar import build_sidebar
from services.api_client import BackendClient
from utils.formatters import format_currency, format_cnpj, format_status, format_date
from components.charts import plot_status_distribution

# --- Configuração da Página ---
st.set_page_config(
    page_title="Consultar Auditorias",
    page_icon="🔍",
    layout="wide"
)

# --- Sidebar ---
build_sidebar()

# --- Inicialização ---
if 'api_client' not in st.session_state:
    st.session_state['api_client'] = BackendClient()

client = st.session_state['api_client']

# --- Cache de Dados ---
@st.cache_data(ttl=300)
def fetch_audits(filters):
    """Busca os dados das auditorias no backend (versão síncrona para cache)."""
    try:
        return asyncio.run(client.get_invoices(filters))
    except Exception as e:
        st.error(f"Erro ao buscar auditorias: {e}")
        return []

    """Busca os dados das auditorias no backend."""
    return asyncio.run(client.get_invoices(filters))


# --- Função para Excel ---
def to_excel(df):
    """Converte DataFrame para Excel em memória."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Auditorias')
    processed_data = output.getvalue()
    return processed_data

# --- Título ---
st.title("🔍 Consultar Auditorias Realizadas")
st.markdown("Filtre e analise o histórico de notas fiscais auditadas.")

# --- Filtros ---
st.subheader("Filtros de Busca", divider="blue")

# Usando um formulário para agrupar os filtros
with st.form(key="filter_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtro de Data (Range)
        default_start = datetime.now().date() - timedelta(days=30)
        default_end = datetime.now().date()
        date_range = st.date_input(
            "Período de Emissão",
            (default_start, default_end),
            help="Selecione o intervalo de datas de emissão das NFs."
        )
    
    with col2:
        # Filtro de Status
        status_options = ["Aprovada", "Rejeitada", "Pendente", "Em Análise"]
        selected_status = st.multiselect(
            "Status da Auditoria",
            options=status_options,
            default=status_options,  # Padrão: todos
            help="Filtre por um ou mais status."
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Filtro de CNPJ
        cnpj_emitter = st.text_input(
            "CNPJ do Emitente",
            placeholder="Digite o CNPJ (somente números)",
            help="Filtre por um CNPJ específico."
        )
    
    with col4:
        # Filtro de Valor
        min_value = st.number_input("Valor Mínimo (R$)", min_value=0.0, step=100.0)
        
    # Botão de submissão do formulário
    submit_button = st.form_submit_button(label="Buscar Auditorias", type="primary")

# --- Processamento e Exibição ---
if submit_button:
    # Preparando os filtros para a API
    filters = {
        "start_date": str(date_range[0]) if len(date_range) > 0 else str(default_start),
        "end_date": str(date_range[1]) if len(date_range) > 1 else str(default_end),
        "status": selected_status,
        "cnpj": cnpj_emitter,
        "min_value": min_value
    }
    
    with st.spinner("Buscando dados no backend..."):
        audit_data = fetch_audits(filters)
    
    if not audit_data:
        st.warning("Nenhum resultado encontrado para os filtros aplicados.")
    else:
        df = pd.DataFrame(audit_data)
        st.success(f"{len(df)} auditorias encontradas.")
        
        # --- Gráfico Rápido ---
        st.subheader("Distribuição de Status (Resultados)", divider="blue")
        
        # Agrupa dados para o gráfico
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        fig = plot_status_distribution(status_counts, 
                                       names_col='status', 
                                       values_col='count',
                                       title="Distribuição de Status da Busca")
        st.plotly_chart(fig, use_container_width=True)

        # --- Tabela de Resultados ---
        st.subheader("Resultados da Busca", divider="blue")
        
        # Preparando DataFrame para exibição
        df_display = df.copy()
        df_display['valor_total'] = df_display['valor_total'].apply(format_currency)
        df_display['emitente_cnpj'] = df_display['emitente_cnpj'].apply(format_cnpj)
        df_display['data_emissao'] = df_display['data_emissao'].apply(format_date)
        df_display['status_formatado'] = df_display['status'].apply(lambda x: format_status(x, return_icon_only=False))
        
        df_display = df_display[[
            'id', 'status_formatado', 'data_emissao', 'emitente_nome', 'emitente_cnpj', 'valor_total'
        ]]

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": "ID Auditoria",
                "status_formatado": "Status",
                "data_emissao": "Emissão",
                "emitente_nome": "Emitente",
                "emitente_cnpj": "CNPJ",
                "valor_total": "Valor (R$)"
            }
        )
        
        # --- Botão de Exportação ---
        excel_data = to_excel(df) # Usa o DataFrame original (sem formatação)
        st.download_button(
            label="Exportar Resultados para Excel",
            data=excel_data,
            file_name=f"auditorias_{default_start}_a_{default_end}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        # --- Detalhes (Expander) ---
        st.subheader("Detalhes da Auditoria", divider="blue")
        st.markdown("Selecione uma auditoria na tabela acima para ver os detalhes.")
        
        # Simulação de seleção (em um app real, usaria st.data_editor ou callbacks)
        # Por simplicidade, mostramos os detalhes da primeira
        if not df.empty:
            selected_audit = df.iloc[0].to_dict()
            
            with st.expander(f"Detalhes da Auditoria ID: {selected_audit['id']}"):
                st.json(selected_audit, expanded=True)
