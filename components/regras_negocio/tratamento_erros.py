import streamlit as st
import logging

logger = logging.getLogger(__name__)

def mostrar_erro(acao, erro):
    """Registra o erro técnico e mostra uma mensagem amigável na interface."""
    logger.exception("%s: %s", acao, erro)
    st.error(
        f"Não foi possível {acao.lower()}. "
        "Verifique a conexão e tente novamente."
    )