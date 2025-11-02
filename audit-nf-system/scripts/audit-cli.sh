#!/bin/bash

# Script auxiliar para gerenciar o sistema de auditoria
# Uso: ./scripts/audit-cli.sh [comando]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

COMPOSE_FILE="docker/docker-compose.yml"

function print_help() {
    echo "🚀 Sistema de Auditoria de Notas Fiscais - CLI Helper"
    echo ""
    echo "Uso: ./scripts/audit-cli.sh [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo ""
    echo "  setup              - Configuração inicial do projeto"
    echo "  start              - Iniciar todos os serviços"
    echo "  stop               - Parar todos os serviços"
    echo "  restart            - Reiniciar todos os serviços"
    echo "  rebuild            - Rebuild e restart de todos os serviços"
    echo "  logs               - Ver logs de todos os serviços"
    echo "  logs [serviço]     - Ver logs de um serviço específico"
    echo "  status             - Ver status de todos os serviços"
    echo "  health             - Verificar saúde de todos os serviços"
    echo ""
    echo "  test               - Rodar todos os testes"
    echo "  test:unit          - Rodar apenas testes unitários"
    echo "  test:integration   - Rodar testes de integração"
    echo "  test:e2e           - Rodar testes E2E"
    echo "  test:load          - Rodar testes de carga (Locust)"
    echo "  test:coverage      - Rodar testes com relatório de cobertura"
    echo ""
    echo "  shell [serviço]    - Abrir shell em um serviço"
    echo "  db                 - Abrir psql no PostgreSQL"
    echo "  redis              - Abrir redis-cli"
    echo ""
    echo "  clean              - Limpar containers e volumes"
    echo "  clean:all          - Limpar tudo incluindo imagens"
    echo ""
    echo "  help               - Mostrar esta mensagem"
    echo ""
}

function setup() {
    echo -e "${GREEN}🔧 Configurando ambiente...${NC}"
    
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Criando arquivo .env...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠️  ATENÇÃO: Edite o arquivo .env com suas API keys!${NC}"
        echo -e "${YELLOW}Execute: nano .env${NC}"
        exit 0
    else
        echo -e "${GREEN}✅ Arquivo .env já existe${NC}"
    fi
    
    echo -e "${GREEN}✅ Setup completo!${NC}"
}

function start() {
    echo -e "${GREEN}🚀 Iniciando serviços...${NC}"
    docker-compose -f $COMPOSE_FILE up -d
    echo -e "${GREEN}✅ Serviços iniciados!${NC}"
    echo -e "${YELLOW}Aguarde alguns segundos para os healthchecks...${NC}"
    sleep 5
    status
}

function stop() {
    echo -e "${YELLOW}⏸️  Parando serviços...${NC}"
    docker-compose -f $COMPOSE_FILE down
    echo -e "${GREEN}✅ Serviços parados!${NC}"
}

function restart() {
    echo -e "${YELLOW}🔄 Reiniciando serviços...${NC}"
    docker-compose -f $COMPOSE_FILE restart
    echo -e "${GREEN}✅ Serviços reiniciados!${NC}"
}

function rebuild() {
    echo -e "${YELLOW}🔨 Rebuilding e reiniciando...${NC}"
    docker-compose -f $COMPOSE_FILE up -d --build
    echo -e "${GREEN}✅ Rebuild completo!${NC}"
}

function logs() {
    if [ -z "$1" ]; then
        docker-compose -f $COMPOSE_FILE logs -f
    else
        docker-compose -f $COMPOSE_FILE logs -f "$1"
    fi
}

function status() {
    echo -e "${GREEN}📊 Status dos serviços:${NC}"
    docker-compose -f $COMPOSE_FILE ps
}

function health() {
    echo -e "${GREEN}🏥 Verificando saúde dos serviços...${NC}"
    echo ""
    
    services=("backend:8080" "frontend:8501" "rag:8001" "agents:8002" "mcp:8003")
    
    for service in "${services[@]}"; do
        name="${service%%:*}"
        port="${service##*:}"
        
        if docker-compose -f $COMPOSE_FILE exec -T "$name" curl -f "http://localhost:$port/health" 2>/dev/null; then
            echo -e "${GREEN}✅ $name está healthy${NC}"
        else
            echo -e "${RED}❌ $name não está respondendo${NC}"
        fi
    done
}

function run_tests() {
    case "$1" in
        "unit")
            echo -e "${GREEN}🧪 Rodando testes unitários...${NC}"
            docker-compose -f $COMPOSE_FILE --profile testing run --rm tests pytest tests/unit/ -v
            ;;
        "integration")
            echo -e "${GREEN}🧪 Rodando testes de integração...${NC}"
            docker-compose -f $COMPOSE_FILE --profile testing run --rm tests pytest tests/integration/ -v
            ;;
        "e2e")
            echo -e "${GREEN}🧪 Rodando testes E2E...${NC}"
            docker-compose -f $COMPOSE_FILE --profile testing run --rm tests pytest tests/e2e/ -v
            ;;
        "load")
            echo -e "${GREEN}🧪 Rodando testes de carga...${NC}"
            echo -e "${YELLOW}Acesse http://localhost:8089 no navegador${NC}"
            docker-compose -f $COMPOSE_FILE --profile testing run --rm -p 8089:8089 tests \
                locust -f tests/load/locustfile.py --host=http://backend:8080 --web-host=0.0.0.0
            ;;
        "coverage")
            echo -e "${GREEN}🧪 Rodando testes com cobertura...${NC}"
            docker-compose -f $COMPOSE_FILE --profile testing run --rm tests \
                pytest --cov=. --cov-report=html --cov-report=term
            
            mkdir -p ./test-reports
            docker cp audit-tests:/app/htmlcov ./test-reports/coverage 2>/dev/null || true
            echo -e "${GREEN}✅ Relatório de cobertura em: ./test-reports/coverage/index.html${NC}"
            ;;
        *)
            echo -e "${GREEN}🧪 Rodando todos os testes...${NC}"
            docker-compose -f $COMPOSE_FILE --profile testing run --rm tests pytest -v
            ;;
    esac
}

function open_shell() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ Especifique um serviço: backend, frontend, rag, agents, mcp${NC}"
        exit 1
    fi
    
    docker-compose -f $COMPOSE_FILE exec "$1" bash
}

function open_db() {
    echo -e "${GREEN}🗄️  Abrindo PostgreSQL...${NC}"
    docker-compose -f $COMPOSE_FILE exec postgres psql -U audit_user -d audit_nf_db
}

function open_redis() {
    echo -e "${GREEN}📦 Abrindo Redis CLI...${NC}"
    docker-compose -f $COMPOSE_FILE exec redis redis-cli
}

function clean() {
    echo -e "${YELLOW}🧹 Limpando containers e volumes...${NC}"
    docker-compose -f $COMPOSE_FILE down -v
    echo -e "${GREEN}✅ Limpeza completa!${NC}"
}

function clean_all() {
    echo -e "${RED}🧹 Limpando TUDO (containers, volumes, imagens)...${NC}"
    echo -e "${RED}⚠️  Esta ação é irreversível!${NC}"
    read -p "Tem certeza? (yes/no): " confirm
    if [ "$confirm" == "yes" ]; then
        docker-compose -f $COMPOSE_FILE down -v --rmi all
        echo -e "${GREEN}✅ Limpeza total completa!${NC}"
    else
        echo -e "${YELLOW}Operação cancelada${NC}"
    fi
}

# Parse comando
case "$1" in
    "setup")
        setup
        ;;
    "start")
        start
        ;;
    "stop")
        stop
        ;;
    "restart")
        restart
        ;;
    "rebuild")
        rebuild
        ;;
    "logs")
        logs "$2"
        ;;
    "status")
        status
        ;;
    "health")
        health
        ;;
    "test")
        run_tests
        ;;
    "test:unit")
        run_tests "unit"
        ;;
    "test:integration")
        run_tests "integration"
        ;;
    "test:e2e")
        run_tests "e2e"
        ;;
    "test:load")
        run_tests "load"
        ;;
    "test:coverage")
        run_tests "coverage"
        ;;
    "shell")
        open_shell "$2"
        ;;
    "db")
        open_db
        ;;
    "redis")
        open_redis
        ;;
    "clean")
        clean
        ;;
    "clean:all")
        clean_all
        ;;
    "help"|"")
        print_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconhecido: $1${NC}"
        echo ""
        print_help
        exit 1
        ;;
esac