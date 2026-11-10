import streamlit as st
from components.parceiros.form_cliente import render_form_cliente
from components.parceiros.consulta_cliente import render_consulta_cliente

def render_aba_clientes():
    st.subheader("Cadastro de Clientes")
    render_form_cliente()
    st.divider()
    render_consulta_cliente()