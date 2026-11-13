import streamlit as st
from components.regras_negocio.formatar_reais import formatar_reais

def render_kpis_comercial(total_vendas, faturamento_negociado, ticket_medio):
    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            label="Vendas registradas",
            value=f"{total_vendas}",
            help="Quantidade de registros encontrados na tabela transacao.",
        )
    with m2:
        st.metric(
            label="Total negociado",
            value=formatar_reais(faturamento_negociado),
            help="Soma dos valores registrados nas vendas.",
        )
    with m3:
        st.metric(
            label="Ticket médio",
            value=formatar_reais(ticket_medio),
            help="Valor médio das vendas registradas.",
        )

    st.divider()