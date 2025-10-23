Frontend do Sistema de Auditoria de NF-e (Streamlit)

Este diretório contém o código-fonte do frontend web para o sistema de auditoria, construído com Streamlit.

Estrutura de Pastas

frontend/
├── app.py                     # Página inicial (Home/Dashboard)
├── pages/                     # Páginas da aplicação (Multi-Page App)
│   ├── 01_📊_Dashboard.py     # Dashboard detalhado
│   ├── 02_📤_Upload_NF.py     # Upload de notas fiscais
│   ├── 03_🔍_Auditoria.py     # Consulta de auditorias
│   ├── 04_🧪_NF_Sinteticas.py # Geração de NFs sintéticas
│   └── 05_📈_Relatorios.py    # Relatórios e análises
├── components/                # Componentes reutilizáveis (sidebar, gráficos)
│   ├── __init__.py
│   ├── sidebar.py
│   └── charts.py
├── services/                  # Lógica de negócio e clientes de API
│   ├── __init__.py
│   └── api_client.py          # Cliente HTTP (httpx) para o Backend
├── utils/                     # Funções utilitárias (formatadores, validadores)
│   ├── __init__.py
│   ├── formatters.py
│   └── validators.py
├── .streamlit/
│   └── config.toml            # Configurações de tema e servidor
├── requirements.txt           # Dependências Python
└── README.md


Como Executar

Instale as dependências:

pip install -r requirements.txt


(Opcional) Crie um arquivo .env:
Se o seu backend estiver rodando em uma URL diferente de http://localhost:8000, crie um arquivo .env na pasta frontend/ para configurar:

BACKEND_URL="[https://sua-api.com/api](https://sua-api.com/api)"


Se o backend não estiver disponível, o api_client.py usará dados mockados automaticamente.

Rode o aplicativo Streamlit:
Na pasta frontend/, execute:

streamlit run app.py


Acesse no navegador:
Abra http://localhost:8501.