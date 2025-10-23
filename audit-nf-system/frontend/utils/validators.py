import re
from streamlit.runtime.uploaded_file_manager import UploadedFile # type: ignore

def validate_xml_file(file: UploadedFile) -> bool:
    """
    Validação básica de arquivo XML (pode ser expandida).
    """
    if file.name.lower().endswith(".xml") and \
       (file.type == "text/xml" or file.type == "application/xml"):
        # Poderia adicionar uma verificação rápida de <xml> tag
        return True
    return False

def validate_pdf_file(file: UploadedFile) -> bool:
    """
    Validação básica de arquivo PDF.
    """
    if file.name.lower().endswith(".pdf") and file.type == "application/pdf":
        return True
    return False

def validate_cnpj_format(cnpj: str) -> bool:
    """
    Valida se a string CNPJ contém 14 dígitos.
    """
    if not cnpj or not isinstance(cnpj, str):
        return False
        
    # Remove todos os caracteres não numéricos
    clean_cnpj = re.sub(r'\D', '', cnpj)
    
    return len(clean_cnpj) == 14
