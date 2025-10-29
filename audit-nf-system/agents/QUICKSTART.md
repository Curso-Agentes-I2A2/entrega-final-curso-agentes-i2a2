# ⚡ INÍCIO RÁPIDO - 5 Minutos

Comece a usar o sistema em 5 minutos!

## 🚀 Setup Automático

```bash
# 1. Execute o script de setup
chmod +x setup.sh
./setup.sh

# 2. Configure sua API Key
nano .env
# Adicione: ANTHROPIC_API_KEY=sk-ant-api03-sua-chave-aqui

# 3. Inicie o servidor
uvicorn main:app --reload --port 8002
```

**Pronto!** Servidor rodando em http://localhost:8002

---

## 📝 Teste Rápido via cURL

### 1. Auditar Nota Fiscal

```bash
curl -X POST http://localhost:8002/api/v1/audit \
  -H "Content-Type: application/json" \
  -d @test_invoice.json
```

### 2. Gerar Nota Sintética

```bash
curl -X POST http://localhost:8002/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "valida",
    "valor_max": 5000.0,
    "estado": "SP"
  }'
```

### 3. Health Check

```bash
curl http://localhost:8002/health
```

---

## 🐍 Teste via Python

```python
import httpx
import asyncio

async def testar_auditoria():
    async with httpx.AsyncClient() as client:
        # Gerar nota sintética
        response = await client.post(
            "http://localhost:8002/api/v1/generate",
            json={"tipo": "valida", "valor_max": 1000.0}
        )
        nota = response.json()["invoice"]
        
        # Auditar nota gerada
        response = await client.post(
            "http://localhost:8002/api/v1/audit",
            json={"invoice": nota}
        )
        
        resultado = response.json()
        print(f"✅ Aprovada: {resultado['aprovada']}")
        print(f"📊 Confiança: {resultado['confianca']:.2%}")
        print(f"⚠️  Irregularidades: {len(resultado['irregularidades'])}")

# Executar
asyncio.run(testar_auditoria())
```

---

## 🧪 Executar Testes

```bash
# Testes básicos
python test_agents.py

# Testes com pytest
pytest test_agents.py -v

# Teste específico
pytest test_agents.py::test_audit_agent -v
```

---

## 📚 Documentação Interativa

Acesse no navegador:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

Lá você pode:
- Ver todos os endpoints
- Testar diretamente no navegador
- Ver exemplos de request/response

---

## 🔧 Exemplos de Notas

### Nota Válida

```json
{
  "invoice": {
    "numero": "000123",
    "serie": "1",
    "data_emissao": "2025-10-27",
    "cnpj_emitente": "12345678000190",
    "cnpj_destinatario": "98765432000199",
    "cfop": "5102",
    "valor_produtos": 1000.00,
    "valor_total": 1180.00,
    "base_calculo_icms": 1000.00,
    "aliquota_icms": 18.0,
    "valor_icms": 180.00
  }
}
```

### Nota Inválida (CFOP)

```json
{
  "invoice": {
    "numero": "000124",
    "cfop": "9999",
    ...
  }
}
```

### Nota Inválida (ICMS)

```json
{
  "invoice": {
    "numero": "000125",
    "valor_icms": 150.00,  // Deveria ser 180
    ...
  }
}
```

---

## 🎯 Fluxo de Uso

```
1. Gerar Nota de Teste
   POST /api/v1/generate
   
2. Auditar Nota
   POST /api/v1/audit
   
3. Verificar Resultado
   - aprovada: true/false
   - irregularidades: []
   - confianca: 0.0-1.0
   
4. Corrigir se Necessário
   (baseado nas irregularidades)
   
5. Re-auditar
   POST /api/v1/audit
```

---

## 💡 Dicas

### Development Mode

```env
# No arquivo .env
DEBUG=True
MOCK_EXTERNAL_SERVICES=True  # Usa mocks para desenvolvimento
```

### Production Mode

```env
DEBUG=False
MOCK_EXTERNAL_SERVICES=False
```

### Ajustar Confiança

```env
AUDIT_CONFIDENCE_THRESHOLD=0.85  # 85% de confiança mínima
```

---

## 🐛 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| "API key not found" | Configure `ANTHROPIC_API_KEY` no `.env` |
| "Module not found" | Execute `pip install -r requirements.txt` |
| "Connection refused" | Inicie o servidor com `uvicorn main:app` |
| "Timeout" | Configure `MOCK_EXTERNAL_SERVICES=True` |

---

## 📊 Resultados Esperados

**Nota Válida:**
```json
{
  "aprovada": true,
  "irregularidades": [],
  "confianca": 0.95,
  "justificativa": "Nota fiscal aprovada. Todos os campos válidos..."
}
```

**Nota Inválida:**
```json
{
  "aprovada": false,
  "irregularidades": [
    "[AUDITORIA] CFOP 9999 não existe na tabela oficial"
  ],
  "confianca": 0.98,
  "justificativa": "Nota fiscal reprovada..."
}
```

---

## 🎉 Pronto!

Você está pronto para usar o sistema!

**Próximos Passos:**
1. Explorar a documentação: http://localhost:8002/docs
2. Testar com seus dados reais
3. Integrar com seu sistema

**Dúvidas?** Consulte o [README.md](README.md) completo.
