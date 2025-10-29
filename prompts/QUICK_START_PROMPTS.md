# ⚡ Quick Start - Gerando Seu Código em 10 Minutos

**Para:** Todos os colaboradores  
**Objetivo:** Gerar o código inicial do seu módulo rapidamente

---

## 🎯 Passo a Passo Rápido

### 1️⃣ Identifique Seu Módulo (1 min)

Qual é seu módulo?
- [ ] Backend
- [ ] RAG
- [ ] Agents
- [ ] MCP
- [ ] Frontend
- [ ] Tests

### 2️⃣ Acesse o Claude (1 min)

🔗 **Acesse:** https://claude.ai

Se não tiver conta:
1. Criar conta gratuita
2. Login
3. Começar nova conversa

### 3️⃣ Copie o Prompt (1 min)

Abra o documento: **"Guia Completo - Prompts para Gerar Código"**

Encontre a seção do seu módulo e copie o prompt completo.

**Exemplo para Backend:**
- Procure "## 1. Backend (FastAPI)"
- Clique em "Ver artefato"
- Copie TODO o texto dentro da caixa "PROMPT:"

### 4️⃣ Cole no Claude (1 min)

1. Cole o prompt no chat do Claude
2. Pressione Enter
3. Aguarde (2-3 minutos)

Claude vai gerar TODOS os arquivos do seu módulo!

### 5️⃣ Copie os Arquivos (3 min)

Claude vai retornar algo como:

```
# backend/main.py
from fastapi import FastAPI
...

# backend/config.py
from pydantic_settings import BaseSettings
...

# backend/models/invoice.py
...
```

**Para cada arquivo:**
1. Crie a pasta correspondente
2. Crie o arquivo
3. Cole o código
4. Salve

**Dica:** Use o comando de criar estrutura de pastas que já temos!

### 6️⃣ Instale Dependências (2 min)

```bash
cd [seu-modulo]
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 7️⃣ Configure (1 min)

Crie arquivo `.env`:
```bash
# Exemplo para Backend
cp .env.example .env
# Edite .env com suas configurações
```

### 8️⃣ Teste (1 min)

**Backend/RAG/Agents/MCP:**
```bash
uvicorn main:app --reload
# Acesse: http://localhost:8000/docs
```

**Frontend:**
```bash
streamlit run app.py
# Acesse: http://localhost:8501
```

**Tests:**
```bash
pytest -v
```

---

## ✅ Checklist de Verificação

Após gerar e testar:

- [ ] Todos os arquivos foram criados
- [ ] Dependências instaladas sem erro
- [ ] Aplicação roda sem erro
- [ ] Entendo a estrutura do código
- [ ] Fiz primeiro commit no meu branch

---

## 🎥 Exemplo Prático - Backend

**Tempo total: ~10 minutos**

### 1. Abrir Claude
```
https://claude.ai
```

### 2. Copiar Prompt
Ir em "Prompt - Backend (FastAPI)" e copiar tudo

### 3. Colar no Claude e Aguardar
Claude gera ~15 arquivos

### 4. Criar Estrutura
```bash
cd audit-nf-system
mkdir -p backend/src/invoice_processing
mkdir -p backend/api/routes
# ... etc
```

### 5. Copiar Arquivos
Para cada arquivo que Claude gerou:
- Criar o arquivo
- Colar o código
- Salvar

### 6. Instalar
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 7. Configurar
```bash
echo "DATABASE_URL=sqlite:///./test.db" > .env
echo "RAG_URL=http://localhost:8001" >> .env
```

### 8. Rodar
```bash
uvicorn main:app --reload
```

### 9. Testar
Abrir: http://localhost:8000/docs

### 10. Commitar
```bash
git add .
git commit -m "feat: adiciona estrutura inicial do backend"
git push origin branch/backend
```

**Pronto! ✅**

---

## 🔥 Dicas Pro

### Dica 1: Use Auto-Create de Pastas
Em vez de criar pasta por pasta, use:

```bash
# Linux/Mac
mkdir -p backend/{src/{invoice_processing,validation,synthetic_nf},api/{routes,controllers,middlewares},models,services,database,schemas}

# Ou use o script de geração de estrutura que já temos!
python generate_structure.py
```

### Dica 2: Peça Ajustes ao Claude
Se algo não ficou bom:

```
Você: "Regenere o arquivo main.py mas adicione suporte 
para CORS e documentação automática mais detalhada"
```

Claude gera novamente, ajustado!

### Dica 3: Gere em Partes
Se estiver com pressa:

**Primeira iteração:**
```
Você: "Gere apenas os arquivos principais: main.py, 
config.py, e requirements.txt"
```

**Depois:**
```
Você: "Agora gere os modelos e schemas"
```

### Dica 4: Use Templates
Salve seus prompts customizados:
```
Meu Prompt = Prompt Original + Minhas Customizações

Exemplo:
"[Prompt do Backend]

ADICIONAL:
- Adicione suporte para PostgreSQL em vez de SQLite
- Use Alembic para migrações
- Adicione autenticação com OAuth2"
```

---

## ❌ Erros Comuns e Soluções

### Erro: "Module not found"
**Causa:** Ambiente virtual não ativado ou dependências não instaladas

**Solução:**
```bash
source venv/bin/activate  # Ativar venv
pip install -r requirements.txt  # Instalar dependências
```

### Erro: "Port already in use"
**Causa:** Outra aplicação rodando na mesma porta

**Solução:**
```bash
# Usar porta diferente
uvicorn main:app --reload --port 8001

# Ou matar processo na porta
# Linux/Mac:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID [número] /F
```

### Erro: Código não compila
**Causa:** Python < 3.11 ou erro no código gerado

**Solução:**
1. Verificar versão Python: `python --version`
2. Se < 3.11, instalar Python 3.11+
3. Se erro persiste, regenerar arquivo específico

### Claude não responde ou demora muito
**Causa:** Prompt muito grande ou API sobrecarregada

**Solução:**
1. Dividir prompt em partes menores
2. Tentar novamente em alguns minutos
3. Usar GPT-4 como alternativa

---

## 🎓 Vídeo Tutorial (Futuro)

```
[ ] Gravar vídeo mostrando processo completo
[ ] Upload no YouTube/Drive do grupo
[ ] Compartilhar link no WhatsApp
```

---

## 📞 Precisa de Ajuda?

### Passo a passo não funcionou?
1. Verificar se seguiu TODOS os passos
2. Ler seção de erros comuns acima
3. Perguntar no WhatsApp com print do erro

### Claude gerou código com erro?
1. Tentar regenerar
2. Pedir ajuste específico ao Claude
3. Pedir ajuda do responsável técnico

### Não entendi o código gerado?
1. Perguntar ao Claude: "Explique o que faz o arquivo X.py"
2. Ler comentários no código
3. Consultar documentação oficial
4. Perguntar no WhatsApp

---

## 🎯 Meta

**Objetivo:** Todos os colaboradores devem ter código inicial gerado e rodando até **segunda-feira**.

**Status atual:**
- [ ] Código gerado
- [ ] Rodando localmente
- [ ] Primeiro commit feito
- [ ] Entendo a estrutura

---

## 📊 Timeline Sugerida

### Hoje (Sexta)
- Gerar código do seu módulo
- Fazer rodar localmente
- Entender estrutura básica

### Fim de semana
- Estudar código gerado
- Fazer pequenos ajustes
- Adicionar funcionalidades específicas

### Segunda
- Commit final do código base
- Início das customizações
- Discussão de integração

### Terça
- Proposta de arquitetura pronta
- Início da integração entre módulos

---

**Bora gerar código! 🚀**

Se tiver dúvida, PERGUNTE! Melhor perguntar do que ficar travado.