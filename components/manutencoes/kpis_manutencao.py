import streamlit as st
from components.regras_negocio.formatar_reais import formatar_reais

def render_kpis_manutencao(df_manutencao):
    qtd_servicos = len(df_manutencao)
    custo_total = df_manutencao["custo_total"].sum() if not df_manutencao.empty else 0.0
    custo_medio = df_manutencao["custo_total"].mean() if not df_manutencao.empty else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Serviços registrados", qtd_servicos)
    col2.metric("Custo total", formatar_reais(custo_total) or "R$ 0,00")
    col3.metric("Custo médio por serviço", formatar_reais(custo_medio) or "R$ 0,00")