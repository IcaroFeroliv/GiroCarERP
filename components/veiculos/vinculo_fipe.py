import datetime
import streamlit as st
from database import supabase
from components.regras_negocio.valor_fipe_para_float import valor_fipe_para_float

FIPE_NAO_VINCULAR = "-- Não vincular (Consulta Externa) --"

def render_vinculo_fipe(v_fipe):
    st.write("**Vincular ao Histórico de um Veículo da Frota? (Opcional)**")
    st.write("Se você pesquisou um carro que já está no seu estoque, selecione a placa abaixo para gravar o histórico financeiro no sistema.")

    res_frota = supabase.table("veiculo").select("placa, marca, modelo").execute()
    lista_frota = [f"{v['placa']} - {v['marca']} {v['modelo']}" for v in res_frota.data]

    with st.form("form_vincular_fipe", clear_on_submit=True):
        col_v1, col_v2 = st.columns([3, 1])
        with col_v1:
            veiculo_frota = st.selectbox("Veículos do Pátio", [FIPE_NAO_VINCULAR] + lista_frota)
        with col_v2:
            st.write("")
            st.write("")
            submit_vincular = st.form_submit_button("Salvar no Banco de Dados", type="primary", use_container_width=True)

        if submit_vincular:
            if veiculo_frota == FIPE_NAO_VINCULAR:
                st.warning("Nenhum veículo selecionado. O histórico não foi salvo.")
                return

            placa = veiculo_frota.split(" - ")[0].strip()
            hoje = datetime.date.today()
            novo_historico = {
                "placa_veiculo": placa,
                "mes_ano_referencia": hoje.strftime("%Y-%m"),
                "valor_api": valor_fipe_para_float(v_fipe),
                "data_consulta": str(hoje),
            }
            supabase.table("historico").insert(novo_historico).execute()
            st.success(f"Sucesso! O valor de {v_fipe} foi gravado no histórico financeiro da placa {placa}.")