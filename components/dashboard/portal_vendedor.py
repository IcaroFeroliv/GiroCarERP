import streamlit as st


def render_portal_vendedor() -> None:
    """Exibe aviso de restrição do dashboard e atalhos operacionais para vendedor."""
    st.warning("🔒 **Acesso Restrito:** O perfil de Vendedor não possui permissão para visualizar o Dashboard Executivo.")
    st.markdown("Utilize o menu lateral para navegar entre as páginas operacionais liberadas para o seu perfil:")

    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        if st.button("🚗 Ir para Veículos", use_container_width=True):
            st.switch_page("pages/01_Veiculos.py")
    with col_v2:
        if st.button("📝 Ir para Comercial", use_container_width=True):
            st.switch_page("pages/02_Comercial.py")
    with col_v3:
        if st.button("🔧 Ir para Manutenções", use_container_width=True):
            st.switch_page("pages/03_Manutencoes.py")