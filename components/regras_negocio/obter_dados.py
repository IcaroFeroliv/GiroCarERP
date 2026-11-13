import logging
import streamlit as st
from database import supabase

logger = logging.getLogger(__name__)

def obter_dados(tabela, colunas="*"):
    """Consulta uma tabela sem interromper toda a página em caso de falha."""
    try:
        resposta = supabase.table(tabela).select(colunas).execute()
        return resposta.data or []
    except Exception as erro:
        logger.exception("Erro ao consultar a tabela %s: %s", tabela, erro)
        st.error(f"Não foi possível carregar os dados de {tabela}.")
        return []