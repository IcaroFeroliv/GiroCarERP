import logging
from pathlib import Path
import streamlit as st

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

def render_cabecalho():
    st.markdown(
        """
        <style>
        .logo-girocar { transform: translateY(18px); }
        </style>
        """,
        unsafe_allow_html=True
    )

    col_logo, col_titulo = st.columns([1, 4], vertical_alignment="center")

    with col_logo:
        if LOGO_PATH.is_file():
            st.markdown('<div class="logo-girocar">', unsafe_allow_html=True)
            st.image(str(LOGO_PATH), width=180)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            logger.error("Logo não encontrada: %s", LOGO_PATH)

    with col_titulo:
        st.title("Administração (RH e Filiais)")