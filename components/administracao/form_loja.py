import streamlit as st
import logging
from database import supabase
from components.regras_negocio.validar_documento import limpar_e_validar_documento

logger = logging.getLogger(__name__)

def render_form_loja():
    with st.form("form_loja", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            cnpj_loja = st.text_input("CNPJ da Loja", max_chars=18)
            nome_loja = st.text_input("Nome da Unidade")
        with col2:
            endereco_loja = st.text_input("Endereço Completo")

        submit_loja = st.form_submit_button("Salvar Loja", type="primary")

        if submit_loja:
            if not cnpj_loja.strip() or not nome_loja.strip():
                st.warning("Preencha os campos obrigatórios (CNPJ e Nome).")
            elif not limpar_e_validar_documento(cnpj_loja):
                st.error("CNPJ inválido. Verifique a digitação.")
            else:
                try:
                    nova_loja = {
                        "cnpj": cnpj_loja.strip(),
                        "nome_unidade": nome_loja.strip(),
                        "endereco": endereco_loja.strip()
                    }
                    supabase.table("loja").insert(nova_loja).execute()
                    st.success("Loja cadastrada com sucesso!")
                except Exception:
                    logger.exception("Falha ao cadastrar loja")
                    st.error("Não foi possível cadastrar a loja. Verifique os dados e tente novamente.")