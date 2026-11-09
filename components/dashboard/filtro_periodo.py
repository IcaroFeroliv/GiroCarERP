import streamlit as st

# Importação corrigida apontando para o novo arquivo de constantes
from components.regras_negocio.constantes import FILTRO_TODO_HISTORICO

def render_filtro_periodo(df_vendas):
    col_filtro, _ = st.columns([1, 3])

    with col_filtro:
        meses_disponiveis = sorted(df_vendas["mes_ano"].unique(), reverse=True)
        mes_selecionado = st.selectbox(
            "Filtrar por Período:", [FILTRO_TODO_HISTORICO] + meses_disponiveis
        )

    if mes_selecionado != FILTRO_TODO_HISTORICO:
        df_vendas = df_vendas[df_vendas["mes_ano"] == mes_selecionado]

    return df_vendas, mes_selecionado