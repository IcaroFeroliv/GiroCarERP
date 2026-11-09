import streamlit as st
from components.regras_negocio.formatar_reais import formatar_reais

def render_estoque(qtd_disponivel, qtd_preparacao, capital_investido):
    st.markdown("### Posição Atual do Pátio")
    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(label="Veículos Disponíveis", value=f"{qtd_disponivel}")
    kpi2.metric(label="Fila da Oficina (Preparação)", value=f"{qtd_preparacao}")
    
    # Removido o R$ fixo daqui
    kpi3.metric(
        label="Capital Empenhado (Estoque)",
        value=formatar_reais(capital_investido),
    )