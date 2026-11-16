import logging
from pathlib import Path
import streamlit as st

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

def render_cabecalho():
    col_logo, col_titulo = st.columns([1, 5], vertical_alignment="center")

    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=180)
        else:
            logger.error("Logo não encontrada: %s", LOGO_PATH)

    with col_titulo:
        st.title("Oficina e Manutenções")
        st.caption("Controle de ordens de serviço, histórico e custos da frota.")