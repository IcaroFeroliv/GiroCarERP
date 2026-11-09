import streamlit as st
from components.regras_negocio.fipe_core import _fipe_get

@st.cache_data(ttl=86400)
def get_marcas():
    return _fipe_get("marcas") or []