#!/bin/bash

###############################################################################
# Script de Instalação Automatizada - Migração Mock para API Real
# Sistema de Auditoria NF-e
###############################################################################

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo ""
    echo "=============================================="
    echo "$1"
    echo "=============================================="
    echo ""
}

# Banner
clear
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   INSTALAÇÃO - MIGRAÇÃO PARA API REAL        ║"
echo "║   Sistema de Auditoria NF-e                  ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Verificar se está no diretório correto
if [ ! -f "api_client_fixed.py" ]; then
    print_error "Erro: arquivo api_client_fixed.py não encontrado"
    print_info "Execute este script no diretório onde extraiu os arquivos"
    exit 1
fi

print_info "Arquivos de migração encontrados!"
echo ""

# 1. Detectar estrutura do projeto
print_header "1. DETECTANDO ESTRUTURA DO PROJETO"

FRONTEND_DIR=""
BACKEND_DIR=""

# Procura por diretórios comuns
if [ -d "../frontend" ]; then
    FRONTEND_DIR="../frontend"
    print_success "Frontend encontrado: $FRONTEND_DIR"
elif [ -d "./frontend" ]; then
    FRONTEND_DIR="./frontend"
    print_success "Frontend encontrado: $FRONTEND_DIR"
else
    print_warning "Diretório frontend não encontrado automaticamente"
    read -p "Digite o caminho para o diretório frontend: " FRONTEND_DIR
fi

if [ -d "../backend" ]; then
    BACKEND_DIR="../backend"
    print_success "Backend encontrado: $BACKEND_DIR"
elif [ -d "./backend" ]; then
    BACKEND_DIR="./backend"
    print_success "Backend encontrado: $BACKEND_DIR"
else
    print_warning "Diretório backend não encontrado automaticamente"
    read -p "Digite o caminho para o diretório backend: " BACKEND_DIR
fi

# 2. Backup de arquivos existentes
print_header "2. CRIANDO BACKUP DOS ARQUIVOS EXISTENTES"

if [ -f "$FRONTEND_DIR/services/api_client.py" ]; then
    cp "$FRONTEND_DIR/services/api_client.py" "$FRONTEND_DIR/services/api_client.py.backup.$(date +%Y%m%d_%H%M%S)"
    print_success "Backup criado: api_client.py.backup"
else
    print_warning "Arquivo api_client.py não encontrado (pode ser instalação nova)"
fi

# 3. Copiar novo api_client.py
print_header "3. INSTALANDO NOVO CLIENTE API"

mkdir -p "$FRONTEND_DIR/services"
cp api_client_fixed.py "$FRONTEND_DIR/services/api_client.py"
print_success "Cliente API atualizado!"

# 4. Configurar .env
print_header "4. CONFIGURANDO VARIÁVEIS DE AMBIENTE"

ENV_FILE=""
if [ -f "$FRONTEND_DIR/.env" ]; then
    ENV_FILE="$FRONTEND_DIR/.env"
elif [ -f "../.env" ]; then
    ENV_FILE="../.env"
elif [ -f "./.env" ]; then
    ENV_FILE="./.env"
fi

if [ -z "$ENV_FILE" ]; then
    # Criar novo .env
    read -p "Criar novo arquivo .env? (s/n): " CREATE_ENV
    if [ "$CREATE_ENV" = "s" ] || [ "$CREATE_ENV" = "S" ]; then
        ENV_FILE="$FRONTEND_DIR/.env"
        
        read -p "URL do Backend [http://localhost:8000]: " BACKEND_URL
        BACKEND_URL=${BACKEND_URL:-http://localhost:8000}
        
        cat > "$ENV_FILE" << EOL
# Backend API Configuration
BACKEND_URL=$BACKEND_URL

# Mock Mode (set to "true" to force mock data, "false" to use real API)
USE_MOCK=false

# Database Configuration (for backend)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/nfe_audit

# API Settings
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:8501,http://localhost:3000
EOL
        print_success "Arquivo .env criado: $ENV_FILE"
    fi
else
    print_info "Arquivo .env já existe: $ENV_FILE"
    
    # Verificar se tem BACKEND_URL
    if ! grep -q "BACKEND_URL" "$ENV_FILE"; then
        print_warning "BACKEND_URL não encontrada no .env"
        read -p "Adicionar BACKEND_URL? (s/n): " ADD_URL
        if [ "$ADD_URL" = "s" ] || [ "$ADD_URL" = "S" ]; then
            echo "BACKEND_URL=http://localhost:8000" >> "$ENV_FILE"
            echo "USE_MOCK=false" >> "$ENV_FILE"
            print_success "Variáveis adicionadas ao .env"
        fi
    fi
fi

# 5. Instalar dependências
print_header "5. VERIFICANDO DEPENDÊNCIAS"

print_info "Verificando dependências do Python..."

# Lista de dependências necessárias
FRONTEND_DEPS="streamlit httpx python-dotenv pandas plotly"
BACKEND_DEPS="fastapi uvicorn sqlalchemy asyncpg python-dotenv"

read -p "Instalar/atualizar dependências do frontend? (s/n): " INSTALL_FRONTEND
if [ "$INSTALL_FRONTEND" = "s" ] || [ "$INSTALL_FRONTEND" = "S" ]; then
    print_info "Instalando dependências do frontend..."
    pip install $FRONTEND_DEPS
    print_success "Dependências do frontend instaladas!"
fi

read -p "Instalar/atualizar dependências do backend? (s/n): " INSTALL_BACKEND
if [ "$INSTALL_BACKEND" = "s" ] || [ "$INSTALL_BACKEND" = "S" ]; then
    print_info "Instalando dependências do backend..."
    pip install $BACKEND_DEPS
    print_success "Dependências do backend instaladas!"
fi

# 6. Opcionalmente adicionar rotas do dashboard
print_header "6. ENDPOINTS ADICIONAIS (OPCIONAL)"

read -p "Instalar endpoints do dashboard no backend? (s/n): " INSTALL_DASHBOARD
if [ "$INSTALL_DASHBOARD" = "s" ] || [ "$INSTALL_DASHBOARD" = "S" ]; then
    mkdir -p "$BACKEND_DIR/api/routes"
    cp dashboard_routes_example.py "$BACKEND_DIR/api/routes/dashboard_routes.py"
    print_success "Rotas do dashboard copiadas!"
    print_warning "ATENÇÃO: Você precisa registrar as rotas no main.py:"
    print_info "    from api.routes import dashboard_routes"
    print_info "    app.include_router(dashboard_routes.router)"
fi

# 7. Copiar script de teste
print_header "7. INSTALANDO FERRAMENTAS DE TESTE"

cp test_connectivity.py "$FRONTEND_DIR/test_connectivity.py"
chmod +x "$FRONTEND_DIR/test_connectivity.py"
print_success "Script de teste instalado!"

# 8. Copiar documentação
print_header "8. COPIANDO DOCUMENTAÇÃO"

cp GUIA_MIGRACAO.md "$FRONTEND_DIR/" 2>/dev/null || true
cp README.md "$FRONTEND_DIR/" 2>/dev/null || true
print_success "Documentação copiada!"

# 9. Resumo e próximos passos
print_header "✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"

echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. Inicie o Backend FastAPI:"
echo "   cd $BACKEND_DIR"
echo "   uvicorn main:app --reload"
echo ""
echo "2. Teste a conectividade:"
echo "   cd $FRONTEND_DIR"
echo "   python test_connectivity.py"
echo ""
echo "3. Inicie o Frontend Streamlit:"
echo "   cd $FRONTEND_DIR"
echo "   streamlit run app.py"
echo ""
echo "4. Acesse a aplicação:"
echo "   Frontend: http://localhost:8501"
echo "   Backend API: http://localhost:8000/docs"
echo ""
echo "📚 Documentação:"
echo "   - README.md - Guia rápido"
echo "   - GUIA_MIGRACAO.md - Guia completo"
echo ""

print_success "Sistema pronto para uso!"
print_info "Consulte README.md para troubleshooting"

echo ""
read -p "Pressione ENTER para finalizar..."