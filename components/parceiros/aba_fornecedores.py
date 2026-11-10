import streamlit as st
from components.parceiros.form_fornecedor import render_form_fornecedor
from components.parceiros.consulta_fornecedor import render_consulta_fornecedor

def render_aba_fornecedores():
    st.subheader("Cadastro de Fornecedores")
    render_form_fornecedor()
    st.divider()
    render_consulta_fornecedor()