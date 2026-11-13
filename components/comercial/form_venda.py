import streamlit as st
from datetime import date
import logging
from database import supabase
from components.regras_negocio.mostrar_erro import mostrar_erro
from components.regras_negocio.formatadores_display import nome_veiculo, nome_cliente, nome_funcionario

logger = logging.getLogger(__name__)

def render_form_venda():
    if st.button(" Atualizar opções de cadastro", key="atualizar_opcoes_venda"):
        st.rerun()

    try:
        resposta_veiculos = supabase.table("veiculo").select("placa, modelo").eq("status_veiculo", "Disponivel").execute()
        veiculos = resposta_veiculos.data or []

        resposta_clientes = supabase.table("cliente").select("cpf_cnpj, nome_completo").execute()
        clientes = resposta_clientes.data or []

        resposta_funcionarios = supabase.table("funcionario").select("matricula, nome").execute()
        funcionarios = resposta_funcionarios.data or []

        erro_opcoes = False
    except Exception as erro:
        logger.exception("Erro ao carregar opções para venda: %s", erro)
        veiculos, clientes, funcionarios = [], [], []
        erro_opcoes = True

    if erro_opcoes:
        st.error("Não foi possível carregar os dados necessários para a venda. Verifique a conexão com o banco.")
    elif not veiculos:
        st.warning("Não há veículos disponíveis para venda no momento.")
    elif not clientes:
        st.warning("Cadastre um cliente antes de registrar uma venda.")
    elif not funcionarios:
        st.warning("Cadastre um funcionário antes de registrar uma venda.")
    else:
        with st.form("form_nova_venda", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                veiculo_selecionado = st.selectbox("Veículo disponível", options=veiculos, format_func=nome_veiculo)
                cliente_selecionado = st.selectbox("Cliente", options=clientes, format_func=nome_cliente)

            with col2:
                funcionario_selecionado = st.selectbox("Funcionário responsável", options=funcionarios, format_func=nome_funcionario)
                data_venda = st.date_input("Data da venda", value=date.today(), format="DD/MM/YYYY")

            valor_negociado = st.number_input("Valor final negociado (R$)", min_value=0.1, step=1000.0, format="%.2f")
            confirmar_venda = st.form_submit_button("Registrar venda", type="primary", width="stretch")

        if confirmar_venda:
            dados_venda = {
                "data": data_venda.isoformat(),
                "placa_veiculo": veiculo_selecionado["placa"],
                "cpf_cnpj_cliente": cliente_selecionado["cpf_cnpj"],
                "matricula_funcionario": funcionario_selecionado["matricula"],
                "valor_final_negociado": valor_negociado,
            }

            try:
                resposta = supabase.table("transacao").insert(dados_venda).execute()

                if not resposta.data:
                    st.error("O banco não confirmou o cadastro da venda. Verifique os dados antes de tentar novamente.")
                else:
                    resposta_status = (
                        supabase.table("veiculo")
                        .update({"status_veiculo": "Vendido"})
                        .eq("placa", veiculo_selecionado["placa"])
                        .eq("status_veiculo", "Disponivel")
                        .execute()
                    )

                    if resposta_status.data:
                        st.success("Venda registrada e veículo atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error(
                            "A venda foi registrada, mas o status do veículo não foi confirmado como atualizado. "
                            "Verifique o cadastro no banco antes de realizar outra tentativa."
                        )

            except Exception as erro:
                mostrar_erro("registrar a venda ou atualizar o veículo", erro)