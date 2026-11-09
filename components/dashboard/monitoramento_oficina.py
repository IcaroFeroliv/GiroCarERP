import streamlit as st

def render_monitoramento_oficina(df_veiculos, qtd_preparacao, df_preparacao):
    st.write("**Monitoramento da Oficina**")

    if not df_veiculos.empty and qtd_preparacao > 0:
        df_fila = df_preparacao[["placa", "marca", "modelo"]].rename(
            columns={"placa": "Placa", "marca": "Marca", "modelo": "Modelo"}
        )
        st.dataframe(df_fila, hide_index=True, use_container_width=True)
    else:
        st.success("Nenhum veículo em preparação. Pátio livre!")