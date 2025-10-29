# main.py

import logging
import sys
from pathlib import Path

# Adiciona o diretório do projeto ao PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# MUDANÇA: A importação agora aponta para o seu novo módulo
try:
    from mcp_module.audit_servers.audit_server import audit_server
    from mcp_module.audit_servers.nf_context_server import nf_server
except ImportError as e:
    print(f"Erro de importação: {e}")
    print("Verifique se os arquivos __init__.py existem em 'mcp_module' e 'mcp_module/audit_servers'")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ... (O resto do seu 'main.py' refatorado continua igual) ...
def main():
    # ... (lógica de seleção de 'selected_server') ...
    
    server_name = "audit" # Padrão
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--server="):
                server_name = arg.split("=")[1]
    
    if server_name == "audit":
        selected_server = audit_server
        logger.info("🔧 Iniciando Audit Server...")
    elif server_name in ["nf-context", "nf_context", "nf"]:
        selected_server = nf_server
        logger.info("📚 Iniciando NF Context Server...")
    else:
        logger.error(f"❌ Servidor desconhecido: {server_name}")
        print(f"Servidores disponíveis: audit, nf-context")
        sys.exit(1)

    logger.info(f"✅ Servidor '{selected_server.name}' iniciando via stdio...")
    selected_server.run(transport="stdio")

if __name__ == "__main__":
    # ... (bloco try/except final) ...
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Servidor MCP encerrado pelo usuário")
    except Exception as e:
        logger.error(f"💥 Erro fatal: {e}", exc_info=True)
        sys.exit(1)