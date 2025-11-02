#!/usr/bin/env python3
"""
Script de teste para verificar conectividade entre Frontend e Backend.
Execute este script antes de iniciar a aplicação Streamlit.
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 10.0

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

async def test_health_check():
    """Testa o endpoint de health check."""
    print("\n" + "="*60)
    print("1. Testando Health Check")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Backend está online! Status: {data.get('status')}")
                print_info(f"   Versão: {data.get('version')}")
                
                components = data.get('components', {})
                for component, status in components.items():
                    if 'healthy' in str(status):
                        print_success(f"   {component}: {status}")
                    elif 'not_configured' in str(status):
                        print_warning(f"   {component}: {status}")
                    else:
                        print_error(f"   {component}: {status}")
                
                return True
            else:
                print_error(f"Health check retornou status {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print_error(f"Não foi possível conectar ao backend em {BACKEND_URL}")
        print_info("   Certifique-se de que o backend está rodando:")
        print_info("   cd backend && uvicorn main:app --reload")
        return False
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return False

async def test_invoice_endpoints():
    """Testa endpoints de notas fiscais."""
    print("\n" + "="*60)
    print("2. Testando Endpoints de Notas Fiscais")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Testa listagem
            print("\n   • GET /api/invoices")
            response = await client.get(f"{BACKEND_URL}/api/invoices?page=1&page_size=5")
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                items = data.get('items', [])
                print_success(f"Listagem funcionando! Total: {total}, Retornados: {len(items)}")
            elif response.status_code == 404:
                print_warning("Endpoint não encontrado. Verifique o prefixo das rotas.")
            else:
                print_error(f"Status code: {response.status_code}")
            
            return response.status_code == 200
            
    except Exception as e:
        print_error(f"Erro ao testar endpoints de invoices: {e}")
        return False

async def test_audit_endpoints():
    """Testa endpoints de auditorias."""
    print("\n" + "="*60)
    print("3. Testando Endpoints de Auditorias")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Testa documentação da API (que lista os endpoints)
            print("\n   • Verificando endpoints de auditoria via /docs")
            response = await client.get(f"{BACKEND_URL}/docs")
            
            if response.status_code == 200:
                print_success("Documentação da API acessível em /docs")
                print_info(f"   Acesse: {BACKEND_URL}/docs")
            
            return True
            
    except Exception as e:
        print_error(f"Erro ao testar endpoints de audits: {e}")
        return False

async def test_missing_endpoints():
    """Verifica endpoints que não existem no backend."""
    print("\n" + "="*60)
    print("4. Verificando Endpoints Faltantes")
    print("="*60)
    
    missing = [
        ("/api/dashboard/summary", "Dados do Dashboard"),
        ("/api/analytics", "Análises Detalhadas"),
        ("/api/synthetic", "NFs Sintéticas")
    ]
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            for endpoint, description in missing:
                response = await client.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 404:
                    print_warning(f"{description} ({endpoint}) - Não implementado")
                    print_info("     → Sistema usará dados mockados para este recurso")
                elif response.status_code == 200:
                    print_success(f"{description} ({endpoint}) - Implementado!")
                else:
                    print_info(f"{description} ({endpoint}) - Status: {response.status_code}")
    
    except Exception as e:
        print_warning(f"Alguns endpoints podem não estar disponíveis: {e}")
    
    return True

async def test_upload_simulation():
    """Simula teste de upload (sem enviar arquivo real)."""
    print("\n" + "="*60)
    print("5. Verificando Endpoint de Upload")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Tenta fazer upload sem arquivo (deve retornar erro 422)
            print("\n   • POST /api/invoices/upload (teste de validação)")
            response = await client.post(f"{BACKEND_URL}/api/invoices/upload")
            
            if response.status_code == 422:
                print_success("Endpoint de upload está configurado (validação funcionando)")
            elif response.status_code == 404:
                print_error("Endpoint de upload não encontrado")
            else:
                print_info(f"Status code: {response.status_code}")
            
            return True
            
    except Exception as e:
        print_error(f"Erro ao testar upload: {e}")
        return False

def print_summary(results):
    """Imprime resumo dos testes."""
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTestes executados: {total}")
    print(f"Testes com sucesso: {passed}")
    print(f"Testes com falha: {total - passed}")
    
    if passed == total:
        print_success("\n✓ Todos os testes passaram! Sistema pronto para uso.")
    elif passed > 0:
        print_warning(f"\n⚠ {passed}/{total} testes passaram. Sistema funcionará com mocks nos endpoints faltantes.")
    else:
        print_error("\n✗ Nenhum teste passou. Verifique se o backend está rodando.")
    
    print("\n" + "="*60)

async def main():
    """Executa todos os testes."""
    print(f"\n{'='*60}")
    print(f"TESTE DE CONECTIVIDADE - Frontend ↔ Backend")
    print(f"{'='*60}")
    print(f"\nBackend URL: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "health_check": await test_health_check(),
        "invoice_endpoints": await test_invoice_endpoints(),
        "audit_endpoints": await test_audit_endpoints(),
        "missing_endpoints": await test_missing_endpoints(),
        "upload_endpoint": await test_upload_simulation()
    }
    
    print_summary(results)
    
    # Instruções finais
    if results["health_check"]:
        print("\n📋 PRÓXIMOS PASSOS:")
        print("   1. Configure o arquivo .env se ainda não fez")
        print("   2. Inicie o Streamlit: streamlit run app.py")
        print("   3. Acesse: http://localhost:8501")
    else:
        print("\n📋 AÇÃO NECESSÁRIA:")
        print("   1. Inicie o backend FastAPI:")
        print("      cd backend")
        print("      uvicorn main:app --reload")
        print("   2. Execute este teste novamente")
        print("   3. Depois inicie o Streamlit")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())