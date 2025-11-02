 #QUICK_FIX.sh
 
 #!/bin/bash

# SOLUÇÃO ULTRA-RÁPIDA para erro de build do RAG
# Uso: bash QUICK_FIX.sh

echo "🔧 QUICK FIX - Corrigindo RAG..."
echo ""

# 1. Limpar Docker (libera ~2-4GB)
echo "🧹 Limpando cache do Docker..."
docker system prune -af --volumes
echo "✅ Limpeza completa"
echo ""

# 2. Atualizar requirements do RAG (versão LITE)
echo "📦 Atualizando RAG requirements (LITE - sem torch)..."
cat > rag/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
chromadb==0.4.18
openai==1.3.7
langchain==0.0.340
langchain-community==0.0.1
pypdf==3.17.1
python-docx==1.1.0
numpy==1.26.2
pandas==2.1.3
httpx==0.25.2
python-dotenv==1.0.0
tiktoken==0.5.2
EOF
echo "✅ RAG requirements atualizado"
echo ""

# 3. Verificar espaço
echo "💾 Espaço disponível:"
df -h / | grep -v Filesystem
echo ""

# 4. Build apenas o RAG
echo "🔨 Building RAG..."
docker-compose build rag
echo "✅ Build completo"
echo ""

# 5. Start tudo
echo "🚀 Iniciando todos os serviços..."
docker-compose up -d
echo "✅ Serviços iniciados"
echo ""

# 6. Status
echo "📊 Status dos containers:"
sleep 5
docker-compose ps
echo ""

echo "✨ PRONTO!"
echo ""
echo "🌐 Acesse: http://localhost:8501"
echo "📝 Ver logs: docker-compose logs -f"