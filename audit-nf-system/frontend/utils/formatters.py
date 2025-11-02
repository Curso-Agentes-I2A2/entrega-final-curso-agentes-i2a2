import re
from datetime import datetime

def format_currency(value: float) -> str:
    """
    Formata um valor float para a moeda brasileira (BRL).
    Ex: 10000.50 -> "R$ 10.000,50"
    """
    if value is None:
        value = 0.0
    try:
        # Usa f-string com formatação de milhar e 2 casas decimais
        # Troca ',' por 'v' (vírgula temporária), '.' por ',' e 'v' por '.'
        formatted_value = f"{value:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
        return f"R$ {formatted_value}"
    except (ValueError, TypeError):
        return "R$ 0,00"

def format_cnpj(cnpj: str) -> str:
    """
    Formata uma string de CNPJ (com ou sem máscara) para o formato padrão.
    Ex: "12345678000190" -> "12.345.678/0001-90"
    """
    if not cnpj or not isinstance(cnpj, str):
        return "N/A"
    
    # Remove todos os caracteres não numéricos
    clean_cnpj = re.sub(r'\D', '', cnpj)
    
    # Aplica a máscara se tiver 14 dígitos
    if len(clean_cnpj) == 14:
        return f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:]}"
    else:
        return cnpj # Retorna o original se não for um CNPJ válido

def format_date(date_str: str, input_format: str = '%Y-%m-%d') -> str:
    """
    Formata uma string de data (ISO) para o formato brasileiro.
    Ex: "2024-10-18" -> "18/10/2024"
    """
    if not date_str:
        return "N/A"
    try:
        # Tenta extrair apenas a data (ignora T HH:MM:SS se houver)
        date_part = date_str.split('T')[0]
        date_obj = datetime.strptime(date_part, input_format).date()
        return date_obj.strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return date_str # Retorna o original se falhar

def format_status(status: str, return_icon_only: bool = False) -> str:
    """
    Adiciona um ícone de status (emoji) para exibição.
    """
    status_lower = str(status).lower()
    icon = "⚪" # Padrão
    
    if "aprovada" in status_lower:
        icon = "✅"
    elif "rejeitada" in status_lower:
        icon = "❌"
    elif "pendente" in status_lower:
        icon = "⏳"
    elif "análise" in status_lower or "processando" in status_lower:
        icon = "⚙️"
    elif "erro" in status_lower or "falha" in status_lower:
        icon = "🔥"
        
    if return_icon_only:
        return icon
    
    return f"{icon} {status.capitalize()}"
