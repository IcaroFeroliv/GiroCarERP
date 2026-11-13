import streamlit as st
from components.comercial.form_venda import render_form_venda

def render_aba_venda():
    st.subheader("Registrar nova venda")
    st.caption("Preencha os dados da negociação para cadastrar a venda.")
    render_form_venda()