import streamlit as st
from components.regras_negocio.fipe_core import _fipe_get

@st.cache_data(ttl=86400)
def get_modelos(cod_marca):
    dados = _fipe_get(f"marcas/{cod_marca}/modelos")
    return dados["modelos"] if dados else []