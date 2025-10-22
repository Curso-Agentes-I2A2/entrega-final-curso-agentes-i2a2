"""
Script para inicializar o banco de dados.

Cria todas as tabelas e opcionalmente carrega dados de exemplo.
"""
import asyncio
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from database.connection import init_db, Base, async_engine
from models import Invoice, Audit, User
from config import settings


async def create_tables():
    """Cria todas as tabelas do banco de dados."""
    print("🔧 Criando tabelas no banco de dados...")
    
    try:
        await init_db()
        print("✅ Tabelas criadas com sucesso!")
        
        # Lista tabelas criadas
        async with async_engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(
                text("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """)
            )
            tables = result.fetchall()
            
            print(f"\n📊 Tabelas criadas ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False


async def create_sample_user():
    """Cria um usuário de exemplo para testes."""
    from database.connection import AsyncSessionLocal
    from passlib.context import CryptContext
    from models.user import User
    
    print("\n👤 Criando usuário de exemplo...")
    
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        async with AsyncSessionLocal() as session:
            # Verifica se já existe
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == "admin@example.com")
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print("⚠️  Usuário de exemplo já existe")
                return True
            
            # Cria usuário
            user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=pwd_context.hash("admin123"),
                full_name="Administrador",
                is_active=True,
                is_superuser=True
            )
            
            session.add(user)
            await session.commit()
            
            print("✅ Usuário criado com sucesso!")
            print(f"   Email: {user.email}")
            print(f"   Senha: admin123")
            print("   ⚠️  ALTERE A SENHA EM PRODUÇÃO!")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False


async def verify_database():
    """Verifica se o banco de dados está acessível."""
    from database.connection import async_engine
    from sqlalchemy import text
    
    print("🔍 Verificando conexão com banco de dados...")
    
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ PostgreSQL conectado: {version.split(',')[0]}")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        print(f"\n💡 Verifique suas configurações no .env:")
        print(f"   DATABASE_URL={settings.DATABASE_URL}")
        return False


async def main():
    """Função principal."""
    print("=" * 60)
    print("🚀 Inicialização do Banco de Dados")
    print("   Sistema de Auditoria de Notas Fiscais")
    print("=" * 60)
    print()
    
    # 1. Verifica conexão
    if not await verify_database():
        sys.exit(1)
    
    print()
    
    # 2. Cria tabelas
    if not await create_tables():
        sys.exit(1)
    
    # 3. Cria usuário de exemplo
    await create_sample_user()
    
    print()
    print("=" * 60)
    print("✅ Inicialização concluída com sucesso!")
    print()
    print("📖 Próximos passos:")
    print("   1. Inicie a API: uvicorn main:app --reload")
    print("   2. Acesse a documentação: http://localhost:8000/docs")
    print("   3. Faça upload de uma NF-e para testar")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())