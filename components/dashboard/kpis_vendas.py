import streamlit as st
from components.regras_negocio.formatar_reais import formatar_reais

def render_kpis_vendas(lucro_periodo, qtd_vendida, rotulo_periodo):
    kpi_v1, kpi_v2 = st.columns(2)

    # Removido o R$ fixo daqui
    kpi_v1.metric(
        label=f"Lucro Bruto ({rotulo_periodo})",
        value=formatar_reais(lucro_periodo),
    )
    kpi_v2.metric(label="Quantidade Vendida", value=f"{qtd_vendida} veículos")