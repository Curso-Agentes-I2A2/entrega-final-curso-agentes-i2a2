# 🎯 Guia Completo - Prompts para Gerar Código Inicial

Este documento contém todos os prompts para gerar o código inicial de cada módulo do projeto.

---

## 📋 Índice de Prompts

| # | Módulo | Responsável | Prompt | Prioridade |
|---|--------|-------------|--------|------------|
| 1 | Backend | Backend Dev | [Ver abaixo](#1-backend-fastapi) | ⭐⭐⭐ Alta |
| 2 | RAG | ML Engineer | [Ver abaixo](#2-rag-busca-vetorial) | ⭐⭐⭐ Alta |
| 3 | Agents | AI Developer | [Ver abaixo](#3-agents-agentes-de-ia) | ⭐⭐⭐ Alta |
| 4 | MCP | MCP Specialist | [Ver abaixo](#4-mcp-model-context-protocol) | ⭐⭐ Média |
| 5 | Frontend | Frontend Dev | [Ver abaixo](#5-frontend-streamlit) | ⭐⭐⭐ Alta |
| 6 | Tests | QA Engineer | [Ver abaixo](#6-tests-testes-automatizados) | ⭐⭐ Média |

---

## 🚀 Como Usar os Prompts

### Passo a Passo

1. **Escolha seu módulo** na tabela acima
2. **Copie o prompt completo** da seção correspondente
3. **Cole no Claude ou GPT-4**:
   - Claude: https://claude.ai
   - ChatGPT: https://chat.openai.com
4. **Receba o código gerado**
5. **Copie os arquivos** para seu projeto
6. **Teste e ajuste** conforme necessário

### Dicas Importantes

✅ **Use Claude Sonnet ou GPT-4** para melhores resultados  
✅ **Leia o código gerado** antes de usar  
✅ **Teste localmente** antes de fazer commit  
✅ **Ajuste configurações** (URLs, API keys, etc)  
✅ **Adicione seus próprios testes**  

---

## 1. Backend (FastAPI)

**Responsável:** Backend Developer  
**Prioridade:** ⭐⭐⭐ Alta  
**Tempo estimado:** 2-3 horas após gerar código

### O que será gerado:
- ✅ Aplicação FastAPI completa
- ✅ Modelos SQLAlchemy
- ✅ Schemas Pydantic
- ✅ Rotas e Controllers
- ✅ Serviços de negócio
- ✅ Cliente para RAG e Agents (com mocks)
- ✅ Configurações e requirements

### Prompt:
Ver artefato: **"Prompt - Backend (FastAPI)"**

### Após gerar:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# Acesse: http://localhost:8000/docs
```

---

## 2. RAG (Busca Vetorial)

**Responsável:** ML/RAG Engineer  
**Prioridade:** ⭐⭐⭐ Alta  
**Tempo estimado:** 3-4 horas após gerar código

### O que será gerado:
- ✅ Pipeline de indexação
- ✅ Sistema de embeddings (OpenAI + fallback local)
- ✅ Cliente ChromaDB
- ✅ Motor de busca semântica
- ✅ API FastAPI para consultas
- ✅ Chunking inteligente
- ✅ Documentos de exemplo

### Prompt:
Ver artefato: **"Prompt - RAG (Sistema de Busca Vetorial)"**

### Após gerar:
```bash
cd rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_rag.py  # Indexar documentos
uvicorn main:app --reload --port 8001
```

---

## 3. Agents (Agentes de IA)

**Responsável:** AI Developer  
**Prioridade:** ⭐⭐⭐ Alta  
**Tempo estimado:** 4-5 horas após gerar código

### O que será gerado:
- ✅ Agente de Auditoria
- ✅ Agente de Validação
- ✅ Agente Gerador de NFs Sintéticas
- ✅ Orquestrador
- ✅ Tools (RAG, MCP, Calculadora)
- ✅ Prompts otimizados
- ✅ API FastAPI

### Prompt:
Ver artefato: **"Prompt - Agentes de IA"**

### Após gerar:
```bash
cd agents
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Configurar .env com ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8002
```

---

## 4. MCP (Model Context Protocol)

**Responsável:** MCP Specialist  
**Prioridade:** ⭐⭐ Média  
**Tempo estimado:** 3-4 horas após gerar código

### O que será gerado:
- ✅ Servidor MCP de contexto
- ✅ Servidor MCP de ferramentas
- ✅ Tools de validação (CNPJ, chave de acesso, etc)
- ✅ Tools de cálculo (impostos)
- ✅ Integrações com APIs brasileiras (BrasilAPI, ReceitaWS)
- ✅ Resources de NFs

### Prompt:
Ver artefato: **"Prompt - MCP (Model Context Protocol)"**

### Após gerar:
```bash
cd mcp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 5. Frontend (Streamlit)

**Responsável:** Frontend Developer  
**Prioridade:** ⭐⭐⭐ Alta  
**Tempo estimado:** 3-4 horas após gerar código

### O que será gerado:
- ✅ App Streamlit multi-page
- ✅ Dashboard com métricas
- ✅ Página de upload
- ✅ Página de auditoria
- ✅ Geração de NFs sintéticas
- ✅ Relatórios e gráficos
- ✅ Cliente HTTP para Backend (com mocks)
- ✅ Componentes reutilizáveis

### Prompt:
Ver artefato: **"Prompt - Frontend (Streamlit)"**

### Após gerar:
```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
# Acesse: http://localhost:8501
```

---

## 6. Tests (Testes Automatizados)

**Responsável:** QA Engineer  
**Prioridade:** ⭐⭐ Média  
**Tempo estimado:** 2-3 horas após gerar código

### O que será gerado:
- ✅ Testes unitários (Backend, RAG, Agents)
- ✅ Testes de integração
- ✅ Testes E2E
- ✅ Testes de carga (Locust)
- ✅ Fixtures e mocks
- ✅ Configuração pytest
- ✅ Coverage setup

### Prompt:
Ver artefato: **"Prompt - Tests (Testes Automatizados)"**

### Após gerar:
```bash
cd tests
pip install -r requirements.txt
pytest -v
pytest --cov --cov-report=html
```

---

## 📊 Ordem de Desenvolvimento Recomendada

### Fase 1: Fundação (Semana 1)
1. ✅ **Backend** - Base da aplicação
2. ✅ **Frontend** - Interface para testar
3. ✅ **Tests** - Começar testes unitários

### Fase 2: Inteligência (Semana 2)
4. ✅ **RAG** - Base de conhecimento
5. ✅ **MCP** - Ferramentas externas
6. ✅ **Agents** - Lógica de IA

### Fase 3: Integração (Semana 3)
7. ✅ Integrar todos os módulos
8. ✅ Testes de integração
9. ✅ Ajustes finais

---

## 🎯 Checklist Pós-Geração

Para cada módulo gerado, verifique:

### Código
- [ ] Código gerado compila/roda sem erros
- [ ] Dependências instaladas corretamente
- [ ] Configurações ajustadas (.env, config.py)
- [ ] Mocks funcionando para desenvolvimento independente

### Testes
- [ ] Testes básicos passando
- [ ] Consegue rodar localmente
- [ ] Entende o que o código faz

### Git
- [ ] Código commitado no branch correto
- [ ] Mensagem de commit descritiva
- [ ] Push feito com sucesso

### Documentação
- [ ] README do módulo atualizado
- [ ] Comentários no código
- [ ] Exemplos de uso documentados

---

## 🔧 Troubleshooting Comum

### Problema: Código não compila
**Solução:**
1. Verificar versão do Python (3.11+)
2. Reinstalar dependências: `pip install -r requirements.txt`
3. Verificar se todas as pastas foram criadas

### Problema: Imports não funcionam
**Solução:**
1. Verificar se está no ambiente virtual
2. Verificar estrutura de pastas
3. Adicionar `__init__.py` em pastas faltando

### Problema: API keys não funcionam
**Solução:**
1. Criar arquivo `.env`
2. Copiar de `.env.example`
3. Adicionar suas keys reais
4. Verificar se python-dotenv está instalado

### Problema: Mocks não funcionam
**Solução:**
1. Verificar variável de ambiente `USE_MOCKS=true`
2. Conferir se serviços externos estão mockados
3. Olhar logs para entender o erro

---

## 💡 Dicas de Customização

### Ajustando Prompts

Você pode ajustar os prompts para:
- ✏️ Adicionar funcionalidades específicas
- ✏️ Mudar bibliotecas (ex: usar Weaviate em vez de ChromaDB)
- ✏️ Adicionar campos extras nos modelos
- ✏️ Customizar estilo de código

**Como:**
1. Copie o prompt original
2. Adicione sua customização no final
3. Exemplo: "Adicione também suporte para PostgreSQL"

### Regenerando Partes

Se uma parte do código não ficou boa:
1. Copie apenas a seção do prompt que quer regenerar
2. Adicione contexto: "Regenere apenas o arquivo X.py"
3. Cole no LLM
4. Substitua apenas aquele arquivo

---

## 📞 Suporte

**Dúvidas sobre os prompts?**
- Consulte o README.md principal
- Pergunte no WhatsApp do grupo
- Abra uma Issue no GitHub

**Código gerado com problemas?**
- Tente regenerar com prompt ajustado
- Peça ajuda do responsável técnico
- Consulte documentação oficial das bibliotecas

---

## 🎓 Próximos Passos

Após gerar todo o código:

1. **Testar individualmente** cada módulo
2. **Fazer integração** entre módulos
3. **Adicionar funcionalidades** específicas
4. **Refatorar** conforme necessário
5. **Documentar** mudanças importantes

---

## 📚 Recursos Adicionais

### Documentação Oficial
- FastAPI: https://fastapi.tiangolo.com/
- LangChain: https://python.langchain.com/
- Streamlit: https://docs.streamlit.io/
- Pytest: https://docs.pytest.org/

### Tutoriais Úteis
- RAG com LangChain: https://python.langchain.com/docs/use_cases/question_answering/
- MCP da Anthropic: https://modelcontextprotocol.io/
- Testes Async: https://pytest-asyncio.readthedocs.io/

---

**Última atualização:** 18/10/2025  
**Versão:** 1.0

Boa geração de código! 🚀