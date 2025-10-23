import streamlit as st # type: ignore
import pandas as pd # type: ignore
import asyncio
from io import BytesIO

# Importações locais
from components.sidebar import build_sidebar
from services.api_client import BackendClient
from utils.formatters import format_currency

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gerador de NFs Sintéticas",
    page_icon="🧪",
    layout="centered" # Layout centrado para formulários
)

# --- Sidebar ---
build_sidebar()

# --- Inicialização ---
if 'api_client' not in st.session_state:
    st.session_state['api_client'] = BackendClient()
if 'synthetic_results' not in st.session_state:
    st.session_state['synthetic_results'] = None

client = st.session_state['api_client']

# --- Título ---
st.title("🧪 Gerador de NFs Sintéticas")
st.markdown("Crie dados de teste (NFs válidas, inválidas ou suspeitas) "
            "para testar os pipelines de auditoria.")

# --- Formulário de Configuração ---
with st.form("synthetic_form"):
    st.subheader("Parâmetros de Geração")
    
    # Tipo de NF
    nf_type = st.selectbox(
        "Tipo de NF a Gerar",
        options=["Válida", "Inválida (Schema)", "Suspeita (Regra de Negócio)", "Misto"],
        index=3,
        help="Define o perfil das NFs a serem geradas."
    )
    
    # Quantidade
    quantity = st.number_input(
        "Quantidade de NFs",
        min_value=1,
        max_value=1000,
        value=10,
        step=10,
        help="Número de notas fiscais a serem criadas no lote."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Valor Máximo
        max_value = st.number_input(
            "Valor Máximo (R$)",
            min_value=100.0,
            max_value=1000000.0,
            value=50000.0,
            step=1000.0
        )
        
    with col2:
        # Estado (UF)
        states_br = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO", "Todas"]
        state_uf = st.selectbox(
            "Estado (UF) do Emitente",
            options=states_br,
            index=states_br.index("Todas"),
            help="Define o estado de origem. 'Todas' usa UFs aleatórias."
        )

    # Botão de Envio
    submitted = st.form_submit_button("Gerar Lote de NFs", type="primary")

# --- Processamento e Exibição dos Resultados ---
if submitted:
    params = {
        "type": nf_type.lower(),
        "quantity": quantity,
        "max_value": max_value,
        "state_uf": state_uf
    }
    
    with st.spinner(f"Gerando {quantity} NFs sintéticas do tipo '{nf_type}'..."):
        results = asyncio.run(client.generate_synthetic(params))
        st.session_state['synthetic_results'] = results

# --- Exibição dos Resultados ---
if st.session_state['synthetic_results']:
    results = st.session_state['synthetic_results']
    st.success(f"✅ {results.get('message', 'Lote gerado com sucesso!')}")
    
    # Estatísticas do Lote
    st.subheader("Estatísticas do Lote Gerado", divider="blue")
    stats = results.get('statistics', {})
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Gerado", stats.get('total_generated', 0))
    col2.metric("Valor Total", format_currency(stats.get('total_value', 0)))
    col3.metric("Média por NF", format_currency(stats.get('average_value', 0)))

    # Preview dos Dados
    st.subheader("Preview das NFs Geradas (Amostra)", divider="blue")
    preview_data = results.get('preview_data', [])
    if preview_data:
        df_preview = pd.DataFrame(preview_data)
        
        # Formatando
        df_preview_display = df_preview.copy()
        df_preview_display['valor'] = df_preview_display['valor'].apply(format_currency)
        
        st.dataframe(
            df_preview_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id_sintetico": "ID Sintético",
                "tipo": "Tipo",
                "uf": "UF",
                "valor": "Valor (R$)"
            }
        )
    else:
        st.info("Nenhum preview disponível.")

    # Download do Lote (ZIP)
    zip_data = results.get('zip_data_base64')
    if zip_data:
        # Decodifica Base64 (API mock retorna string, simulamos bytes)
        # Em um caso real, seria: data=base64.b64decode(zip_data)
        st.download_button(
            label="Baixar Lote de NFs (.zip)",
            data=b"Simulacao_de_arquivo_zip", # Mock
            file_name=results.get('zip_filename', 'lote_sintetico.zip'),
            mime="application/zip",
            use_container_width=True
        )
