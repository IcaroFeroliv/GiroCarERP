import streamlit as st
import logging
from database import supabase
from components.regras_negocio.validar_documento import limpar_e_validar_documento

logger = logging.getLogger(__name__)

def render_form_cliente():
    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            cpf_cnpj_cliente = st.text_input("CPF ou CNPJ", max_chars=18)
            nome_cliente = st.text_input("Nome Completo / Razão Social")
            telefone_cliente = st.text_input("Telefone")
        with col2:
            email_cliente = st.text_input("E-mail")
            status_funil = st.selectbox(
                "Status no Funil de Vendas",
                ["Contato Inicial", "Em Negociação", "Venda Fechada"]
            )

        submit_cliente = st.form_submit_button("Salvar Cliente", type="primary")

        if submit_cliente:
            if not cpf_cnpj_cliente.strip() or not nome_cliente.strip():
                st.warning("Preencha os campos obrigatórios (CPF/CNPJ e Nome).")
            elif not limpar_e_validar_documento(cpf_cnpj_cliente):
                st.error("CPF/CNPJ inválido. Verifique a digitação.")
            else:
                try:
                    novo_cliente = {
                        "cpf_cnpj": cpf_cnpj_cliente.strip(),
                        "nome_completo": nome_cliente.strip(),
                        "telefone": telefone_cliente.strip(),
                        "email": email_cliente.strip(),
                        "status_funil_vendas": status_funil
                    }
                    supabase.table("cliente").insert(novo_cliente).execute()
                    st.success("Cliente cadastrado com sucesso!")
                except Exception:
                    logger.exception("Erro ao cadastrar cliente")
                    st.error("Erro ao cadastrar cliente. Verifique os dados e se o CPF/CNPJ já existe.")