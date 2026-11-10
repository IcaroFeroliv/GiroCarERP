import streamlit as st
from components.administracao.form_funcionario import render_form_funcionario
from components.administracao.consulta_funcionario import render_consulta_funcionario

def render_aba_funcionarios():
    st.subheader("Cadastro de Funcionário")
    render_form_funcionario()
    st.divider()
    render_consulta_funcionario()