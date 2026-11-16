import streamlit as st
import datetime
from database import supabase
from components.regras_negocio.tratamento_erros import mostrar_erro
from components.regras_negocio.supabase_utils import obter_dados

def render_aba_nova():
    st.subheader("Nova ordem de serviço")
    st.write("Preencha os dados do veículo e do serviço realizado.")

    try:
        frota = obter_dados("veiculo", "placa, modelo")
        
        # Filtra na memória para evitar complexidades de string com o utilitário
        frota = [v for v in frota if v.get("status_veiculo") != "Vendido"]

        if not frota:
            st.warning("Não há veículos disponíveis para registrar uma manutenção.")
        else:
            opcoes = {f"{v['placa']} - {v.get('modelo') or 'Modelo não informado'}": v["placa"] for v in frota if v.get("placa")}

            if not opcoes:
                st.warning("Não foi possível identificar as placas dos veículos.")
            else:
                with st.form("form_manutencao", clear_on_submit=True):
                    veiculo = st.selectbox("Veículo", options=list(opcoes.keys()))
                    data_servico = st.date_input("Data do serviço", value=datetime.date.today(), max_value=datetime.date.today(), format="DD/MM/YYYY")
                    descricao = st.text_area("Descrição do serviço realizado", placeholder="Informe os serviços executados...", max_chars=300)
                    custo = st.number_input("Custo total (R$)", min_value=0.0, step=50.0, format="%.2f")
                    
                    salvar = st.form_submit_button("Salvar ordem de serviço", type="primary", width="stretch")

                if salvar:
                    if not descricao.strip():
                        st.warning("Informe a descrição do serviço.")
                    elif custo <= 0:
                        st.warning("O custo total deve ser maior que zero.")
                    else:
                        placa_selecionada = opcoes[veiculo]
                        nova_os = {
                            "placa_veiculo": placa_selecionada,
                            "descricao_servico": descricao.strip(),
                            "data": str(data_servico),
                            "custo_total": custo,
                        }

                        try:
                            supabase.table("manutencao").insert(nova_os).execute()
                            supabase.table("veiculo").update({"status_veiculo": "Em preparacao"}).eq("placa", placa_selecionada).execute()
                            st.success(f"Manutenção registrada para {placa_selecionada}.")
                            st.rerun()
                        except Exception as erro:
                            mostrar_erro("registrar a ordem de serviço", erro)

    except Exception as erro:
        mostrar_erro("carregar os veículos", erro)