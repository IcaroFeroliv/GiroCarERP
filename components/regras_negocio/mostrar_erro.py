import logging
import streamlit as st

logger = logging.getLogger(__name__)

def mostrar_erro(acao, erro):
    """Registra o erro técnico e mostra uma mensagem amigável."""
    logger.exception("%s: %s", acao, erro)
    st.error(
        f"Não foi possível {acao.lower()}. "
        "Verifique a conexão e tente novamente."
    )