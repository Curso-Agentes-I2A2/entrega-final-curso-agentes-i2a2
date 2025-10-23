import httpx
import os
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import streamlit as st # Necessário para st.error e st.warning
from dotenv import load_dotenv

load_dotenv()

class BackendClient:
    """
    Cliente HTTP assíncrono para comunicação com a API de backend.
    Inclui lógica de retry e mocks para desenvolvimento frontend.
    """
    
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.timeout = 30.0
        # Configuração de retry
        self.transport = httpx.AsyncHTTPTransport(
            retries=3, 
            http2=True
        )

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Método helper para fazer requisições com retry."""
        async with httpx.AsyncClient(transport=self.transport, timeout=self.timeout) as client:
            try:
                response = await client.request(method, f"{self.base_url}/api/{endpoint}", **kwargs)
                response.raise_for_status()  # Levanta erro para status 4xx/5xx
                return response.json()
            except httpx.HTTPStatusError as e:
                # Erro do servidor (4xx, 5xx)
                st.error(f"Erro da API: {e.response.status_code} - {e.response.text}")
                return {"error": str(e), "status_code": e.response.status_code}
            except httpx.RequestError as e:
                # Erro de conexão, timeout, etc.
                st.warning(f"Não foi possível conectar ao backend: {e}. Usando dados mockados.")
                return {"error": "backend_offline", "details": str(e)}

    async def upload_invoice(self, file_bytes: bytes, filename: str) -> dict:
        """
        Upload de nota fiscal (XML ou PDF) para processamento.
        """
        files = {"file": (filename, file_bytes, "application/octet-stream")}
        
        # Simula uma chamada de API
        # Descomente a linha abaixo para tentar a chamada real
        # result = await self._make_request("POST", "invoices/upload", files=files)
        
        # Simulação de erro para forçar o mock
        result = {"error": "backend_offline"} 

        if "error" in result and result["error"] == "backend_offline":
            # Mock quando backend não disponível
            await asyncio.sleep(1.5) # Simula processamento
            status = random.choice(["Aprovada", "Rejeitada", "Pendente"])
            issues = []
            if status == "Rejeitada":
                issues = [
                    {"code": "E101", "description": "CNPJ do emitente inválido"},
                    {"code": "E205", "description": "Valor do ICMS difere do calculado"}
                ]
            
            return {
                "id": f"mock-{random.randint(1000, 9999)}",
                "filename": filename,
                "status": status,
                "confidence": random.uniform(0.6, 1.0) if status != "Rejeitada" else random.uniform(0.1, 0.5),
                "issues": issues,
                "message": "Upload realizado com sucesso (mock)"
            }
        return result

    async def get_invoices(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca lista de notas fiscais auditadas com base em filtros.
        """
        # Descomente para chamada real
        # result = await self._make_request("GET", "invoices", params=filters)
        
        # Simulação de erro para forçar o mock
        result = {"error": "backend_offline"}

        if "error" in result and result["error"] == "backend_offline":
            # Mock de lista de NFs
            await asyncio.sleep(0.5)
            data = []
            for i in range(20):
                status = random.choice(["Aprovada", "Rejeitada", "Pendente"])
                data.append({
                    "id": f"NF-MOCK-{1000 + i}",
                    "data_emissao": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    "emitente_nome": f"Fornecedor Mock {chr(65 + i)}",
                    "emitente_cnpj": f"12.345.67{i:02}/0001-99",
                    "valor_total": random.uniform(100.0, 5000.0),
                    "status": status
                })
            return data
        
        return result.get("invoices", []) # Supondo que a API retorna {"invoices": [...]}

    async def get_audit_result(self, invoice_id: str) -> Dict[str, Any]:
        """
        Busca o resultado detalhado de uma auditoria específica.
        """
        # Descomente para chamada real
        # result = await self._make_request("GET", f"audits/{invoice_id}")
        
        # Simulação de erro para forçar o mock
        result = {"error": "backend_offline"}

        if "error" in result and result["error"] == "backend_offline":
            await asyncio.sleep(0.3)
            status = random.choice(["Aprovada", "Rejeitada", "Pendente"])
            issues = []
            if status == "Rejeitada":
                issues = [
                    {"code": "E101", "description": "CNPJ do emitente inválido"},
                    {"code": "E205", "description": "Valor do ICMS difere do calculado"}
                ]
            
            return {
                "id": invoice_id,
                "status": status,
                "confidence": random.uniform(0.6, 1.0) if status != "Rejeitada" else random.uniform(0.1, 0.5),
                "issues": issues,
                "timestamp": datetime.now().isoformat(),
                "details": "Auditoria realizada (mock) sobre dados fictícios.",
                "history": [
                    {"timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(), "action": "Upload Recebido"},
                    {"timestamp": (datetime.now() - timedelta(minutes=3)).isoformat(), "action": "Auditoria Iniciada"},
                    {"timestamp": (datetime.now() - timedelta(minutes=1)).isoformat(), "action": f"Resultado: {status}"}
                ]
            }
        return result

    async def generate_synthetic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solicita a geração de NFs sintéticas para teste.
        """
        # Descomente para chamada real
        # result = await self._make_request("POST", "synthetic", json=params)

        # Simulação de erro para forçar o mock
        result = {"error": "backend_offline"}
        
        if "error" in result and result["error"] == "backend_offline":
            await asyncio.sleep(1) # Simula geração
            
            generated_nfs = []
            for i in range(params.get("quantidade", 1)):
                generated_nfs.append({
                    "id": f"SYNTH-{random.randint(10000, 99999)}",
                    "tipo": params.get("tipo", "valida"),
                    "valor": random.uniform(100.0, params.get("valor_maximo", 5000.0)),
                    "uf": params.get("estado", "SP")
                })
            
            return {
                "message": f"{len(generated_nfs)} NFs sintéticas geradas (mock)",
                "zip_file_url": f"http://mockserver.com/downloads/synthetic_batch_{random.randint(100,999)}.zip",
                "preview_data": generated_nfs
            }
        return result

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Busca dados resumidos para o dashboard principal.
        Este é o método que estava faltando.
        """
        # Descomente para chamada real
        # result = await self._make_request("GET", "dashboard/summary")
        
        # Simulação de erro para forçar o mock
        result = {"error": "backend_offline"}

        if "error" in result and result["error"] == "backend_offline":
            # CORREÇÃO AQUI:
            # Trocado 'await asyncio.loop.create_task(asyncio.sleep(0.5))'
            # por 'await asyncio.sleep(0.5)' que é a forma correta.
            await asyncio.sleep(0.5) # Simula espera da rede
            
            timeline = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).isoformat()
                timeline.append({"data": date, "volume": random.randint(100, 200), "status": "Aprovada"})
                timeline.append({"data": date, "volume": random.randint(10, 30), "status": "Rejeitada"})
                timeline.append({"data": date, "volume": random.randint(5, 15), "status": "Pendente"})
            
            recent = []
            for i in range(5):
                recent.append({
                    "id": f"NF-{9501 + i}",
                    "status": random.choice(["Aprovada", "Pendente", "Rejeitada"]),
                    "valor": random.uniform(500.0, 3000.0)
                })

            # Mock data que BATE com o que app.py espera
            return {
                "kpis": {
                    "total_nfs": 1250,
                    "approval_rate": 0.952,
                    "pending_nfs": 88,
                    "pending_delta": "+5",
                    "last_24h": 150
                },
                "timeline_data": timeline,
                "recent_activity": recent
            }
        return result

