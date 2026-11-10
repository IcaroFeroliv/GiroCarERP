import streamlit as st
from components.administracao.form_loja import render_form_loja
from components.administracao.consulta_loja import render_consulta_loja

def render_aba_lojas():
    st.subheader("Cadastro de Loja")
    render_form_loja()
    st.divider()
    render_consulta_loja()