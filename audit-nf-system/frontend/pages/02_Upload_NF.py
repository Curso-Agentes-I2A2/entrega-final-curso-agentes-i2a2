import streamlit as st # type: ignore
import asyncio
import time

# Importações locais
from components.sidebar import build_sidebar
from services.api_client import BackendClient
from utils.validators import validate_xml_file, validate_pdf_file
from utils.formatters import format_status, format_currency

# --- Configuração da Página ---
st.set_page_config(
    page_title="Upload de NF-e",
    page_icon="📤",
    layout="wide"
)

# --- Sidebar ---
build_sidebar()

# --- Inicialização ---
if 'api_client' not in st.session_state:
    st.session_state['api_client'] = BackendClient()
if 'upload_results' not in st.session_state:
    st.session_state['upload_results'] = []

client = st.session_state['api_client']

# --- Título ---
st.title("📤 Upload de Notas Fiscais (NF-e)")
st.markdown("Envie um ou mais arquivos XML ou PDF para processamento e auditoria.")

# --- Componente de Upload ---
uploaded_files = st.file_uploader(
    "Escolha os arquivos XML ou PDF",
    type=["xml", "pdf"],
    accept_multiple_files=True,  # Suporte a múltiplos arquivos
    help="Você pode arrastar e soltar múltiplos arquivos aqui."
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} arquivo(s) carregado(s) com sucesso!")

    # --- Opções de Processamento ---
    with st.expander("⚙️ Opções de Processamento", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            validate_schema = st.checkbox("Validar Schema XML/PDF", value=True, 
                                        help="Verifica a estrutura básica do arquivo.")
        with col2:
            run_audit = st.checkbox("Executar Auditoria Completa", value=True,
                                    help="Cruza dados com regras de negócio e Sefaz.")
        with col3:
            generate_report = st.checkbox("Gerar Relatório de Auditoria", value=False,
                                        help="Gera um PDF com o resultado da análise.")

    # --- Botão de Processamento ---
    if st.button("🚀 Processar Arquivos", type="primary", use_container_width=True):
        st.session_state['upload_results'] = []  # Limpa resultados anteriores
        
        # Barra de progresso
        progress_bar = st.progress(0, text="Iniciando processamento...")
        
        results = []
        total_files = len(uploaded_files)
        
        # Loop para processar cada arquivo
        for i, file in enumerate(uploaded_files):
            # Validação frontend básica
            if file.type == "text/xml" and not validate_xml_file(file):
                results.append({"filename": file.name, "status": "Erro de Formato", "issues": ["Arquivo XML inválido"]})
                continue
            if file.type == "application/pdf" and not validate_pdf_file(file):
                results.append({"filename": file.name, "status": "Erro de Formato", "issues": ["Arquivo PDF inválido"]})
                continue

            # Atualiza barra de progresso
            progress_text = f"Processando: {file.name} ({i+1}/{total_files})"
            progress_bar.progress((i + 1) / total_files, text=progress_text)
            
            # Chama a API (simulação assíncrona)
            try:
                # Lê os bytes do arquivo
                file_bytes = file.getvalue()
                
                # Prepara parâmetros para a API
                params = {
                    "validate_schema": validate_schema,
                    "run_audit": run_audit,
                    "generate_report": generate_report
                }
                
                # Chama o cliente API
                result = asyncio.run(client.upload_invoice(file_bytes, file.name, params))
                result["filename"] = file.name # Garante que o nome do arquivo esteja no resultado
                results.append(result)
                
            except Exception as e:
                st.error(f"Falha ao processar {file.name}: {e}")
                results.append({"filename": file.name, "status": "Falha no Upload", "issues": [str(e)]})
        
        progress_bar.progress(1.0, text="Processamento concluído!")
        st.session_state['upload_results'] = results

# --- Exibição dos Resultados ---
if st.session_state['upload_results']:
    st.header("Resultados do Processamento", divider="blue")
    
    # Métricas de resumo do lote
    results = st.session_state['upload_results']
    total = len(results)
    aprovadas = sum(1 for r in results if r.get('status', '').lower() == 'aprovada')
    rejeitadas = sum(1 for r in results if r.get('status', '').lower() == 'rejeitada')
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Processado", f"{total}")
    col2.metric("Aprovadas", f"{aprovadas}", delta=f"{aprovadas/total:.0%}" if total > 0 else "0%")
    col3.metric("Rejeitadas", f"{rejeitadas}", delta=f"-{rejeitadas/total:.0%}" if total > 0 else "0%", delta_color="inverse")
    
    st.divider()

    # Resultados individuais em expanders
    for res in st.session_state['upload_results']:
        status = res.get('status', 'N/A')
        icon = format_status(status, return_icon_only=True)
        
        with st.expander(f"{icon} {res.get('filename', 'Nome desconhecido')} - Status: **{status.upper()}**"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score de Confiança", f"{res.get('confidence_score', 0):.0%}")
            with col2:
                st.metric("Valor da Nota", format_currency(res.get('value', 0)))
            with col3:
                st.metric("Irregularidades", len(res.get('issues', [])))

            # Lista de Irregularidades
            issues = res.get('issues', [])
            if issues:
                st.subheader("Irregularidades Encontradas:")
                for issue in issues:
                    st.warning(f"**{issue.get('code', 'Geral')}:** {issue.get('description', 'Erro desconhecido')}")
            else:
                st.success("Nenhuma irregularidade encontrada.")
            
            # Botão de Download do Relatório (se disponível)
            if res.get('report_url'):
                # Em um cenário real, 'report_url' seria uma URL para baixar
                # Aqui, simulamos com dados mock
                st.download_button(
                    label="Baixar Relatório de Auditoria (PDF)",
                    data=b"Simulacao de PDF", # Mock
                    file_name=f"relatorio_{res.get('id', 'mock')}.pdf",
                    mime="application/pdf"
                )
