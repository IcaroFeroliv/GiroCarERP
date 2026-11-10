import streamlit as st
import logging
from database import supabase
from components.regras_negocio.validar_documento import limpar_e_validar_documento

logger = logging.getLogger(__name__)

def render_form_fornecedor():
    with st.form("form_fornecedor", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            cnpj_cpf_forn = st.text_input("CNPJ ou CPF do Fornecedor", max_chars=18)
            nome_forn = st.text_input("Nome / Razão Social")
        with col2:
            telefone_forn = st.text_input("Telefone de Contato")
            tipo_origem = st.selectbox("Tipo de Origem", ["Repasse", "Leilão", "Particular"])

        submit_forn = st.form_submit_button("Salvar Fornecedor", type="primary")

        if submit_forn:
            if not cnpj_cpf_forn.strip() or not nome_forn.strip():
                st.warning("Preencha os campos obrigatórios (CNPJ/CPF e Nome).")
            elif not limpar_e_validar_documento(cnpj_cpf_forn):
                st.error("CPF/CNPJ inválido. Verifique a digitação.")
            else:
                try:
                    novo_forn = {
                        "cnpj_cpf": cnpj_cpf_forn.strip(),
                        "nome_razao_social": nome_forn.strip(),
                        "telefone": telefone_forn.strip(),
                        "tipo_origem": tipo_origem
                    }
                    supabase.table("fornecedor").insert(novo_forn).execute()
                    st.success("Fornecedor cadastrado com sucesso!")
                except Exception:
                    logger.exception("Erro ao cadastrar fornecedor")
                    st.error("Erro ao cadastrar fornecedor. Verifique os dados e tente novamente.")