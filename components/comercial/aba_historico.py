import streamlit as st
from components.comercial.consulta_vendas import render_consulta_vendas

def render_aba_historico(df_vendas):
    st.subheader("Histórico de vendas")
    st.caption("Consulte e filtre os registros comerciais existentes no sistema.")
    render_consulta_vendas(df_vendas)