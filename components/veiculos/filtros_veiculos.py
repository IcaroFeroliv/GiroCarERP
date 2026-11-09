import streamlit as st
from components.regras_negocio.filtrar_texto_contem import filtrar_texto_contem
from components.regras_negocio.filtrar_em_lista import filtrar_em_lista

def render_filtros_veiculos(df):
    with st.expander("Filtros de Busca", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_placa = st.text_input("Buscar por Placa").upper()
        with col_f2:
            filtro_status = st.multiselect("Filtrar por Status", options=df["status_veiculo"].unique())
        with col_f3:
            filtro_marca = st.multiselect("Filtrar por Marca", options=df["marca"].unique())

    df_filtrado = df.copy()
    df_filtrado = filtrar_texto_contem(df_filtrado, "placa", filtro_placa)
    df_filtrado = filtrar_em_lista(df_filtrado, "status_veiculo", filtro_status)
    df_filtrado = filtrar_em_lista(df_filtrado, "marca", filtro_marca)
    return df_filtrado