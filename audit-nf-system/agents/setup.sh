#!/bin/bash

# ============================================================================
# Script de Setup Rápido - Sistema de Auditoria NF-e
# ============================================================================

echo "=================================="
echo "🚀 SETUP - Sistema de Auditoria"
echo "=================================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "\n${YELLOW}1. Verificando Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python encontrado: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 não encontrado. Instale Python 3.9+${NC}"
    exit 1
fi

# Criar ambiente virtual
echo -e "\n${YELLOW}2. Criando ambiente virtual...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Ambiente virtual criado${NC}"
else
    echo -e "${GREEN}✓ Ambiente virtual já existe${NC}"
fi

# Ativar ambiente virtual
echo -e "\n${YELLOW}3. Ativando ambiente virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Ambiente virtual ativado${NC}"

# Instalar dependências
echo -e "\n${YELLOW}4. Instalando dependências...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependências instaladas${NC}"

# Verificar .env
echo -e "\n${YELLOW}5. Verificando arquivo .env...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado${NC}"
    echo -e "${YELLOW}   Copiando .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  IMPORTANTE: Edite .env e adicione sua ANTHROPIC_API_KEY${NC}"
else
    echo -e "${GREEN}✓ Arquivo .env encontrado${NC}"
fi

# Executar testes rápidos
echo -e "\n${YELLOW}6. Executando testes básicos...${NC}"
python -c "from config import settings; print('✓ Configurações carregadas')" 2>/dev/null && \
    echo -e "${GREEN}✓ Sistema configurado corretamente${NC}" || \
    echo -e "${RED}✗ Erro na configuração - verifique .env${NC}"

# Instruções finais
echo -e "\n=================================="
echo -e "${GREEN}✅ SETUP CONCLUÍDO!${NC}"
echo -e "=================================="

echo -e "\n${YELLOW}📝 PRÓXIMOS PASSOS:${NC}"
echo ""
echo "1. Configure sua API key:"
echo "   nano .env"
echo "   (Adicione: ANTHROPIC_API_KEY=sk-ant-...)"
echo ""
echo "2. Inicie o servidor:"
echo "   uvicorn main:app --reload --port 8002"
echo ""
echo "3. Acesse a documentação:"
echo "   http://localhost:8002/docs"
echo ""
echo "4. Teste com exemplo:"
echo "   curl -X POST http://localhost:8002/api/v1/audit \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d @test_invoice.json"
echo ""
echo -e "${GREEN}Boa auditoria! 🎉${NC}"
