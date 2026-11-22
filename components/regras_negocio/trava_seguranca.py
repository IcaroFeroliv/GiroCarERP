import streamlit as st

def verificar_acesso(pagina_atual):
    """
    Verifica se o usuário está logado e se possui permissão 
    para acessar a página atual com base no seu perfil.
    """
    # 1. Se não estiver logado, bloqueia e manda para o login
    if not st.session_state.get("autenticado"):
        st.error("Acesso negado. Por favor, faça o login na página principal (app.py).")
        if st.button("Ir para a Tela de Login"):
            st.switch_page("app.py")
        st.stop()
        
    perfil = st.session_state.get("perfil_usuario")
    
    # 2. Se for Vendedor, restringe apenas para as páginas permitidas (01, 02, 03)
    paginas_vendedor = ["01_Veiculos.py", "02_Comercial.py", "03_Manutencoes.py"]
    
    if perfil == "Vendedor" and pagina_atual not in paginas_vendedor:
        st.error("Acesso restrito! O perfil de Vendedor não possui permissão para acessar esta página.")
        if st.button("Voltar para o Início"):
            st.switch_page("app.py")
        st.stop()