# ✅ Checklist Rápido - Primeiros Passos

**Use este checklist para não se perder!**

---

## 📋 Setup Inicial (Fazer UMA VEZ)

### 1. Acesso ao GitHub
- [ ] Recebi email de convite do GitHub
- [ ] Aceitei o convite
- [ ] Consigo acessar o repositório
- [ ] Sei qual é meu branch: `branch/[MEU-MODULO]`

### 2. Instalação de Ferramentas
- [ ] Git instalado (`git --version`)
- [ ] Python 3.11+ instalado (`python --version`)
- [ ] Editor de código (VS Code recomendado)
- [ ] Docker instalado (opcional)

### 3. Configuração do Git
```bash
# Configure seu nome e email (uma vez só)
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```
- [ ] Git configurado com meu nome e email

### 4. Clone do Repositório
```bash
# Clone o repositório
git clone https://github.com/[ORGANIZAÇÃO]/audit-nf-system.git
cd audit-nf-system

# Veja todos os branches
git branch -a

# Entre no seu branch
git checkout branch/[SEU-MODULO]
```
- [ ] Repositório clonado
- [ ] Estou no meu branch correto

### 5. Ambiente Python
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate

# Instalar dependências do seu módulo
cd [SEU-MODULO]
pip install -r requirements.txt
```
- [ ] Ambiente virtual criado
- [ ] Ambiente ativado
- [ ] Dependências instaladas

---

## 📖 Estudo (até Segunda/Terça)

### Time Técnico
- [ ] Li `README.md` completo
- [ ] Li `docs/RAG_MCP_GUIDE.md`
- [ ] Entendi o conceito de RAG
- [ ] Entendi o conceito de MCP
- [ ] Vi exemplos de código
- [ ] Estudei o repositório llm-examples

**Tarefas Específicas:**
- [ ] Propus arquitetura do meu módulo
- [ ] Listei tecnologias/bibliotecas necessárias
- [ ] Identifiquei APIs externas úteis
- [ ] Criei esboço em `docs/ARCHITECTURE.md`

### Time Regras de Negócio
- [ ] Li `README.md` completo
- [ ] Li seção de RAG e MCP
- [ ] Entendi papel do RAG no sistema
- [ ] Entendi papel do MCP no sistema
- [ ] Vi exemplos práticos

**Tarefas Específicas:**
- [ ] Listei documentos fiscais para RAG
- [ ] Identifiquei APIs externas úteis
- [ ] Documentei regras de auditoria
- [ ] Criei esboço em `docs/BUSINESS_RULES.md`

---

## 💻 Desenvolvimento Diário

### Antes de Começar
```bash
# 1. Ativar ambiente virtual
source venv/bin/activate  # ou venv\Scripts\activate no Windows

# 2. Ir para seu branch
git checkout branch/[SEU-MODULO]

# 3. Atualizar com últimas mudanças
git pull origin branch/[SEU-MODULO]
```
- [ ] Ambiente ativado
- [ ] No branch correto
- [ ] Branch atualizado

### Durante o Desenvolvimento
- [ ] Código funcionando localmente
- [ ] Testes passando (se houver)
- [ ] Código documentado

### Ao Terminar o Dia
```bash
# 1. Ver o que mudou
git status

# 2. Adicionar arquivos
git add .
# ou específicos: git add arquivo1.py arquivo2.py

# 3. Commitar com mensagem clara
git commit -m "feat: implementa validação de XML"

# 4. Enviar para GitHub
git push origin branch/[SEU-MODULO]
```
- [ ] Mudanças commitadas
- [ ] Push feito com sucesso
- [ ] Verificado no GitHub que apareceu

---

## 🔄 Pull Request (Quando Módulo Pronto)

### Preparação
```bash
# 1. Certifique-se que está atualizado
git pull origin branch/[SEU-MODULO]

# 2. Verifique se tudo funciona
# Execute testes, rode a aplicação

# 3. Faça último commit se necessário
git add .
git commit -m "docs: atualiza README do módulo"
git push origin branch/[SEU-MODULO]
```
- [ ] Branch atualizado
- [ ] Tudo testado e funcionando
- [ ] Documentação atualizada

### Criar PR no GitHub
1. Acesse: https://github.com/[ORGANIZAÇÃO]/audit-nf-system
2. Clique "Pull Requests" > "New Pull Request"
3. Base: `main` | Compare: `branch/[SEU-MODULO]`
4. Título: `[MÓDULO] Descrição breve`
5. Descrição detalhada do que foi feito
6. Create Pull Request

- [ ] PR criado no GitHub
- [ ] Descrição clara do que foi implementado
- [ ] Aguardando revisão

---

## 🆘 Troubleshooting

### Não consigo fazer push
```bash
# Erro: "Updates were rejected"
# Solução: Fazer pull primeiro
git pull origin branch/[SEU-MODULO]
# Resolver conflitos se houver
git push origin branch/[SEU-MODULO]
```

### Fiz commit errado
```bash
# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Fazer novo commit correto
git add .
git commit -m "mensagem correta"
git push origin branch/[SEU-MODULO]
```

### Não sei em qual branch estou
```bash
# Ver branch atual
git branch

# Ver todos os branches
git branch -a

# Trocar de branch
git checkout branch/[SEU-MODULO]
```

### Erro ao instalar dependências
```bash
# Atualizar pip
pip install --upgrade pip

# Instalar novamente
pip install -r requirements.txt

# Se ainda falhar, verificar versão do Python
python --version  # Deve ser 3.11+
```

### Docker não funciona
```bash
# Verificar se Docker está rodando
docker --version
docker ps

# Iniciar Docker (Windows/Mac)
# Abrir Docker Desktop

# Linux
sudo systemctl start docker
```

---

## 📞 Pedir Ajuda

### Onde Pedir Ajuda

**Git/GitHub:**
- WhatsApp do grupo
- Tag: @[coordenador] ou @[responsavel-tecnico]

**Dúvida Técnica:**
- Criar Issue no GitHub
- WhatsApp (para coisas rápidas)

**Não tenho certeza sobre implementação:**
- Perguntar ANTES de implementar
- Melhor perguntar do que fazer errado

### Template para Pedir Ajuda

```
🆘 AJUDA: [Título do problema]

O QUE ESTOU TENTANDO FAZER:
[Descrever]

O QUE ACONTECE:
[Erro ou problema]

O QUE JÁ TENTEI:
1. [Tentativa 1]
2. [Tentativa 2]

ANEXOS:
[Print do erro, código, etc]
```

---

## 🎯 Objetivos Esta Semana

### Todos
- [ ] Setup completo (Git, Python, Docker)
- [ ] Primeiro commit no meu branch
- [ ] Entendimento de RAG e MCP
- [ ] Proposta de arquitetura/regras (até terça)

### Time Técnico Extra
- [ ] Dockerfile do meu módulo funcionando
- [ ] Mock básico implementado
- [ ] Estrutura de pastas criada

### Time Regras de Negócio Extra
- [ ] Lista de documentos fiscais
- [ ] Lista de APIs externas
- [ ] Regras de validação documentadas

---

## ⏰ Prazos

| Tarefa | Prazo | Status |
|--------|-------|--------|
| Setup inicial | Hoje | [ ] |
| Estudo RAG/MCP | Fim de semana | [ ] |
| Proposta arquitetura | Segunda/Terça | [ ] |
| Implementação | Semana 3-4 | [ ] |

---

## 📱 Comandos Git - Cola

**Comandos Mais Usados:**
```bash
# Atualizar
git pull origin branch/[SEU-MODULO]

# Ver status
git status

# Adicionar tudo
git add .

# Commitar
git commit -m "feat: descrição"

# Enviar
git push origin branch/[SEU-MODULO]

# Ver histórico
git log --oneline --graph

# Trocar branch
git checkout branch/[SEU-MODULO]
```

**Salve esses comandos!** 📌

---

## ✅ Status Pessoal

**Seu Nome:** _______________  
**Seu Módulo:** _______________  
**Seu Branch:** _______________  

**Hoje eu:**
- [ ] Fiz setup
- [ ] Clonei repositório
- [ ] Fiz primeiro commit
- [ ] Estudei documentação
- [ ] Entendi minha tarefa

**Próximo passo:**
- [ ] _______________

---

**Dúvidas? Pergunte no WhatsApp! 💬**

**Última atualização:** 18/10/2025