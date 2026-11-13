import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

def render_cabecalho():
    st.markdown(
        """
        <style>
            .block-container { padding-top: 1.8rem; padding-bottom: 2rem; }
            .girocar-subtitle { color: #8b95a5; font-size: 0.95rem; margin-top: -12px; margin-bottom: 22px; }
            .metric-card { padding: 18px; border: 1px solid rgba(128, 128, 128, 0.22); border-radius: 12px; min-height: 110px; }
            .section-caption { color: #8b95a5; font-size: 0.9rem; }
            div[data-testid="stForm"] { border-radius: 12px; padding: 20px; }
            div[data-testid="stMetric"] { padding: 4px 0; }
            div.stButton > button, div.stFormSubmitButton > button { border-radius: 8px; font-weight: 600; min-height: 42px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_logo, col_titulo = st.columns([1, 6], vertical_alignment="center")

    with col_logo:
        if LOGO_PATH.is_file():
            st.image(str(LOGO_PATH), width=110)
        else:
            st.markdown("# 🚗")

    with col_titulo:
        st.title("Comercial e Gestão de Vendas")
        st.markdown(
            '<p class="girocar-subtitle">Central de acompanhamento de vendas e pagamentos do GiroCarERP.</p>',
            unsafe_allow_html=True,
        )

    st.divider()