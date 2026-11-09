import streamlit as st
from database import supabase

STATUS_ATUALIZAR = ["Disponivel", "Em preparacao", "Vendido", "Reservado"]

def render_acoes_rapidas(df_filtrado):
    st.subheader("Ações Rápidas")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Atualizar Status do Veículo**")
        placa_edit = st.selectbox("Selecione a Placa", df_filtrado["placa"], key="edit_placa")
        novo_status = st.selectbox("Novo Status", STATUS_ATUALIZAR)

        if st.button("Atualizar Status", use_container_width=True):
            supabase.table("veiculo").update({"status_veiculo": novo_status}).eq("placa", placa_edit).execute()
            st.success(f"Status da placa {placa_edit} atualizado para {novo_status}!")
            st.rerun()

    with col2:
        st.write("**Excluir Registro**")
        placa_del = st.selectbox("Selecione a Placa", df_filtrado["placa"], key="del_placa")

        if st.button("Excluir Veículo", type="primary", use_container_width=True):
            try:
                supabase.table("veiculo").delete().eq("placa", placa_del).execute()
                st.success(f"Veículo {placa_del} excluído com sucesso!")
                st.rerun()
            except Exception:
                st.error("Não é possível excluir este veículo pois ele já possui vínculo com Manutenções ou Histórico.")