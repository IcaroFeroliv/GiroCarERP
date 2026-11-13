import streamlit as st
import pandas as pd
from components.regras_negocio.formatar_reais import formatar_reais

def render_consulta_vendas(df_vendas):
    if df_vendas.empty:
        st.info("Nenhuma venda foi encontrada para exibição.")
        return

    df_exibicao = df_vendas.copy()
    col_filtro1, col_filtro2 = st.columns(2)

    with col_filtro1:
        if "placa_veiculo" in df_exibicao.columns:
            filtro_placa = st.text_input(
                "Pesquisar por placa",
                placeholder="Ex.: ABC1D23",
                key="filtro_placa_vendas",
            ).strip().upper()

            df_exibicao = df_exibicao[
                df_exibicao["placa_veiculo"].fillna("").astype(str).str.upper().str.contains(filtro_placa, regex=False)
            ]

    with col_filtro2:
        if "valor_final_negociado" in df_exibicao.columns:
            valores_filtro = pd.to_numeric(df_exibicao["valor_final_negociado"], errors="coerce")
            valor_minimo = float(valores_filtro.min()) if valores_filtro.notna().any() else 0.0
            valor_maximo = float(valores_filtro.max()) if valores_filtro.notna().any() else 0.0

            faixa_valor = st.slider(
                "Faixa de valor negociado (R$)",
                min_value=valor_minimo,
                max_value=max(valor_maximo, valor_minimo + 1.0),
                value=(valor_minimo, max(valor_maximo, valor_minimo + 1.0)),
                key="faixa_valor_vendas",
            )

            df_exibicao = df_exibicao[
                valores_filtro.loc[df_exibicao.index].between(faixa_valor[0], faixa_valor[1])
            ]

    df_tabela = df_exibicao.copy()

    if "valor_final_negociado" in df_tabela.columns:
        df_tabela["valor_final_negociado"] = pd.to_numeric(
            df_tabela["valor_final_negociado"], errors="coerce"
        ).map(formatar_reais)

    st.dataframe(
        df_tabela,
        width="stretch",
        hide_index=True,
        column_config={
            "valor_final_negociado": st.column_config.TextColumn("Valor negociado"),
            "data": st.column_config.TextColumn("Data da venda"),
            "placa_veiculo": st.column_config.TextColumn("Placa"),
        },
    )

    st.caption(f"Exibindo {len(df_exibicao)} de {len(df_vendas)} venda(s).")