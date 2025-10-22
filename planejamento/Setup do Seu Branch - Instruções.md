# 🔧 Setup do Seu Branch - Instruções

**Para:** Todos os colaboradores  
**Tempo:** 2 minutos

---

## 📋 Você Escolhe o Que Fazer

Seu branch já existe. Agora você decide:

### Opção A: Pegar Tudo da Main

```bash
# 1. Entre no seu branch
git checkout [seu-branch]

# 2. Traga tudo da main
git merge main --no-edit

# 3. Suba
git push
```

**Resultado:** Você tem todas as pastas (backend, rag, agents, mcp, frontend, tests, security, etc)

---

### Opção B: Pegar Só Sua Pasta (Recomendado)

Escolha os comandos do **seu módulo**:

#### Backend
```bash
git checkout [seu-branch]
git fetch origin main
git checkout origin/main -- backend/ docker/ shared/ .gitignore README.md Makefile
git add .
git commit -m "chore: estrutura backend"
git push
```

#### RAG
```bash
git checkout [seu-branch]
git fetch origin main
git checkout origin/main -- rag/ docker/ shared/ .gitignore README.md Makefile
git add .
git commit -m "chore: estrutura rag"
git push
```

#### Agents
```bash
git checkout [seu-branch]
git fetch origin main
git checkout origin/main -- agents/ docker/ shared/ .gitignore README.md Makefile
git add .
git commit -m "chore: estrutura agents"
git push
```

#### MCP
```bash
git checkout [seu-branch]
git fetch origin main
git checkout origin/main -- mcp/ docker/ shared/ .gitignore README.md Makefile
git add .
git commit -m "chore: estrutura mcp"
git push
```

#### Frontend
```bash
git checkout [seu-branch]
git fetch origin main
git checkout origin/main -- frontend/ docker/ shared/ .gitignore README.md Makefile
git add .
git commit -m "chore: estrutura frontend"
git push
```

#### Tests
```bash
git checkout [seu-branch]
git fetch origin main
git checkout origin/main -- tests/ docker/ shared/ .gitignore README.md Makefile
git add .
git commit -m "chore: estrutura tests"
git push
```

#### Security
```bash
git checkout [seu-branch]
git fetch origin main
git checkout origin/main -- security/ docker/ shared/ .gitignore README.md Makefile
git add .
git commit -m "chore: estrutura security"
git push
```

**Resultado:** Você tem apenas sua pasta + arquivos compartilhados

---

## ✅ Verificar

```bash
ls -la  # Ver se sua pasta apareceu
git status  # Ver status
```

---

## 🆘 Deu Erro?

### "Already up to date"
✅ Está tudo certo, pode continuar

### "Conflict"
```bash
git merge --abort
# Tentar Opção B em vez da A
```

### "Permission denied"
Falar com coordenador

---

## 📝 Próximo Passo

Após ter a estrutura:
1. Ir para `docs/QUICK_START_PROMPTS.md`
2. Gerar código do seu módulo
3. Começar a desenvolver

---

**Escolha Opção A ou B e execute. Pronto! ✅**