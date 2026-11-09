import streamlit as st

def render_grafico_lucratividade(df_lucro):
    if not df_lucro.empty:
        st.bar_chart(
            df_lucro,
            x="Veículo",
            y="Lucro Bruto (R$)",
            color="#2ca02c",
            use_container_width=True,
        )
    else:
        st.info("Nenhuma venda registrada no período selecionado.")