import streamlit as st
import pandas as pd
from utils.formatters import format_currency, format_cnpj, format_date, format_status

def display_responsive_table(df: pd.DataFrame, column_config: dict = None):
    """
    Exibe um DataFrame do Streamlit com configurações padrão para
    responsividade e boa visualização.
    """
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config
    )

def get_audit_column_config() -> dict:
    """
    Retorna uma configuração de coluna padrão para tabelas de auditoria.
    """
    return {
        "id": st.column_config.TextColumn(
            "ID Auditoria",
            help="Identificador único da auditoria"
        ),
        "status": st.column_config.TextColumn(
            "Status"
        ),
        "status_formatado": st.column_config.TextColumn(
            "Status"
        ),
        "data_emissao": st.column_config.DateColumn(
            "Emissão",
            format="DD/MM/YYYY",
            help="Data de emissão da NF-e"
        ),
        "emitente_nome": st.column_config.TextColumn(
            "Emitente"
        ),
        "emitente_cnpj": st.column_config.TextColumn(
            "CNPJ"
        ),
        "valor_total": st.column_config.NumberColumn(
            "Valor (R$)",
            format="R$ %.2f",
            help="Valor total da nota fiscal"
        ),
        "valor": st.column_config.NumberColumn(
            "Valor (R$)",
            format="R$ %.2f"
        ),
    }

def display_audit_table(df: pd.DataFrame):
    """
    Exibe uma tabela de auditoria com formatação e colunas pré-definidas.
    
    Assume que o DataFrame 'df' pode conter colunas como:
    'id', 'status', 'data_emissao', 'emitente_nome', 'emitente_cnpj', 'valor_total'
    """
    
    # Prepara o DataFrame para exibição
    df_display = df.copy()
    
    if 'valor_total' in df_display.columns:
        df_display['valor_total_fmt'] = df_display['valor_total']
    
    if 'data_emissao' in df_display.columns:
        # st.dataframe lida bem com datetime, mas garantimos
        df_display['data_emissao'] = pd.to_datetime(df_display['data_emissao'])

    if 'emitente_cnpj' in df_display.columns:
        df_display['emitente_cnpj_fmt'] = df_display['emitente_cnpj'].apply(format_cnpj)
        
    if 'status' in df_display.columns:
        df_display['status_formatado'] = df_display['status'].apply(lambda x: format_status(x, return_icon_only=False))

    # Define as colunas a serem mostradas e sua ordem
    display_columns = [
        'id', 
        'status_formatado', 
        'data_emissao', 
        'emitente_nome', 
        'emitente_cnpj_fmt', 
        'valor_total_fmt'
    ]
    
    # Filtra colunas que realmente existem no df_display
    final_columns = [col for col in display_columns if col in df_display.columns]
    
    # Obtém a configuração de coluna
    config = get_audit_column_config()
    
    # Renomeia colunas no config para bater com o df_display
    config['valor_total_fmt'] = config.pop('valor_total')
    config['emitente_cnpj_fmt'] = config.pop('emitente_cnpj')
    
    st.dataframe(
        df_display[final_columns],
        use_container_width=True,
        hide_index=True,
        column_config=config
    )