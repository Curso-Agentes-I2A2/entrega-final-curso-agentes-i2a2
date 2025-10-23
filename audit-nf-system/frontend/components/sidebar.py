import streamlit as st
from datetime import datetime

# URL de um logo placeholder. Substitua pela URL do seu logo.
LOGO_URL = "https://placehold.co/200x80/1f77b4/FFFFFF?text=AuditorNF-e&font=sans-serif"

def build_sidebar():
    """
    Constrói a sidebar padrão que será usada em todas as páginas.
    Usa st.session_state para obter informações do usuário (mockadas em app.py).
    """
    
    with st.sidebar:
        # --- Logo ---
        st.image(LOGO_URL, use_container_width=True)
        
        # --- Informações do Usuário ---
        st.subheader("Perfil do Usuário", divider="blue")
        
        if 'user_info' in st.session_state:
            user = st.session_state['user_info']
            st.markdown(f"**Nome:** {user['name']}")
            st.markdown(f"**Cargo:** {user['role']}")
            st.caption(f"Último acesso: {user['last_login']}")
        else:
            st.info("Usuário não logado.")

        # --- Estatísticas Rápidas (Mock) ---
        st.subheader("Status Rápido", divider="blue")
        st.metric(label="NFs Pendentes", value="88", delta="5")
        st.metric(label="Valor em Risco", value="R$ 12.5k", delta="-R$ 1.2k")

        st.divider()
        
        # --- Botão de Logout (Apenas visual) ---
        if st.button("Logout", use_container_width=True):
            st.toast("Logout realizado com sucesso!", icon="👋")
            # Em um app real, aqui você limparia o session_state e redirecionaria
            # st.session_state.clear()
            # st.switch_page("Login.py") # Se houvesse uma página de login