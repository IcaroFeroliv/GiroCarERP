from pathlib import Path
import streamlit as st
from components.regras_negocio.autenticacao import (
    CREDENCIAIS_GERENTES,
    autenticar_gerente,
    autenticar_vendedor,
)


def render_tela_login(logo_path: Path) -> None:
    """Renderiza o formulário de login e atualiza a sessão conforme o perfil."""
    if logo_path.is_file():
        _, col_centro, _ = st.columns([1, 2, 1])
        with col_centro:
            st.image(str(logo_path), width=220)

    st.title("Acesso ao Sistema — GiroCar")
    st.markdown("Identifique-se para acessar o painel de indicadores e operações.")

    with st.form("form_login"):
        usuario_input = st.text_input("Usuário", placeholder="ex: joaosilva ou seu@email.com")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar no Sistema", type="primary", use_container_width=True)

        if not submit:
            return

        usuario_limpo = (usuario_input or "").strip()
        senha_limpa = str(senha or "").strip()

        if not usuario_limpo or not senha_limpa:
            st.warning("Preencha todos os campos.")
            return

        email_digitado = usuario_limpo.lower()
        if email_digitado in CREDENCIAIS_GERENTES:
            ok, identificador, mensagem = autenticar_gerente(email_digitado, senha_limpa)
            if ok:
                st.session_state["autenticado"] = True
                st.session_state["perfil_usuario"] = "Gerente"
                st.session_state["email_usuario"] = identificador
                st.success(mensagem)
                st.rerun()
            else:
                st.error(mensagem)
            return

        try:
            ok, identificador, mensagem = autenticar_vendedor(usuario_limpo, senha_limpa)
            if ok:
                st.session_state["autenticado"] = True
                st.session_state["perfil_usuario"] = "Vendedor"
                st.session_state["email_usuario"] = identificador
                st.success(mensagem)
                st.rerun()
            else:
                st.error(mensagem)
        except Exception as err:
            st.error(f"Erro ao validar credenciais no banco de dados: {err}")