import streamlit as st

def mostrar_detalhes_tecnicos(erro, titulo="Detalhes Técnicos (Para Suporte)"):
    with st.expander(titulo):
        st.code(str(erro))