import pandas as pd
import streamlit as st
from database import supabase
from components.regras_negocio.formatar_reais import formatar_reais
from components.regras_negocio.filtrar_texto_contem import filtrar_texto_contem
from components.regras_negocio.filtrar_em_lista import filtrar_em_lista
from components.regras_negocio.mostrar_detalhes_tecnicos import mostrar_detalhes_tecnicos

COLUNAS_RENOMEADAS_HISTORICO = {
    "placa_veiculo": "Placa", "mes_ano_referencia": "Mês de Referência",
    "valor_api": "Valor de Mercado", "data_consulta": "Data da Consulta",
}

def render_aba_historico():
    st.subheader("Histórico de Avaliações (FIPE)")
    st.write("Acompanhe a variação de preço de mercado dos veículos da frota.")

    try:
        res_historico = supabase.table("historico").select("*").order("data_consulta", desc=True).execute()
        df_historico = pd.DataFrame(res_historico.data)

        if df_historico.empty:
            st.info("Nenhuma avaliação foi salva no histórico até o momento.")
            return

        with st.expander("Filtros de Busca do Histórico", expanded=False):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                filtro_placa_hist = st.text_input("Filtrar por Placa", key="filtro_hist_placa").upper()
            with col_f2:
                filtro_mes = st.multiselect("Mês de Referência", options=df_historico["mes_ano_referencia"].unique())
            with col_f3:
                filtro_data = st.multiselect("Data da Consulta", options=df_historico["data_consulta"].unique())

        df_filtrado = df_historico.copy()
        df_filtrado = filtrar_texto_contem(df_filtrado, "placa_veiculo", filtro_placa_hist)
        df_filtrado = filtrar_em_lista(df_filtrado, "mes_ano_referencia", filtro_mes)
        df_filtrado = filtrar_em_lista(df_filtrado, "data_consulta", filtro_data)

        if df_filtrado.empty:
            st.warning("Nenhum registro encontrado com os filtros aplicados.")
            return

        df_filtrado["valor_api"] = df_filtrado["valor_api"].apply(formatar_reais)
        df_exibicao = df_filtrado.rename(columns=COLUNAS_RENOMEADAS_HISTORICO)
        st.dataframe(df_exibicao[list(COLUNAS_RENOMEADAS_HISTORICO.values())], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Erro ao carregar o histórico de avaliações.")
        mostrar_detalhes_tecnicos(e, titulo="Detalhes Técnicos")