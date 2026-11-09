import streamlit as st
from components.regras_negocio.fipe_core import _fipe_get

@st.cache_data(ttl=86400)
def get_anos(cod_marca, cod_modelo):
    return _fipe_get(f"marcas/{cod_marca}/modelos/{cod_modelo}/anos") or []