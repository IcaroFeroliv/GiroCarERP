import pandas as pd
import streamlit as st
from database import supabase
from components.veiculos.filtros_veiculos import render_filtros_veiculos
from components.veiculos.tabela_veiculos import render_tabela_veiculos
from components.veiculos.acoes_rapidas import render_acoes_rapidas
from components.regras_negocio.mostrar_detalhes_tecnicos import mostrar_detalhes_tecnicos

MSG_ERRO_CONEXAO = (
    "⚠️ Não foi possível estabelecer conexão com o banco de dados. "
    "Verifique sua conexão de rede ou tente novamente mais tarde."
)

def render_aba_consulta():
    st.subheader("Veículos no Sistema")
    try:
        res = supabase.table("veiculo").select("*").execute()
        df = pd.DataFrame(res.data)

        if df.empty:
            st.info("Nenhum veículo cadastrado no sistema.")
            return

        df_filtrado = render_filtros_veiculos(df)
        render_tabela_veiculos(df_filtrado)
        st.divider()

        if not df_filtrado.empty:
            render_acoes_rapidas(df_filtrado)
        else:
            st.warning("Nenhum veículo encontrado com os filtros aplicados.")

    except Exception as e:
        st.error(MSG_ERRO_CONEXAO)
        mostrar_detalhes_tecnicos(e)