import streamlit as st
import logging
from database import supabase
from components.regras_negocio.validar_documento import limpar_e_validar_documento

logger = logging.getLogger(__name__)

def render_form_funcionario():
    with st.form("form_funcionario", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            matricula = st.text_input("Matrícula", max_chars=50)
            nome_func = st.text_input("Nome Completo")
        with col2:
            cargo = st.selectbox("Cargo / Nível de Acesso", ["Vendedor", "Gerente"])
            cnpj_vinculo = st.text_input("CNPJ da Loja (Vínculo)")
        with col3:
            data_admissao = st.date_input("Data de Admissão")

        submit_func = st.form_submit_button("Salvar Funcionário", type="primary")

        if submit_func:
            if not matricula.strip() or not nome_func.strip() or not cnpj_vinculo.strip():
                st.warning("Preencha Matrícula, Nome e o CNPJ da Loja vinculada.")
            elif not limpar_e_validar_documento(cnpj_vinculo):
                st.error("O CNPJ da Loja vinculada é inválido.")
            else:
                try:
                    novo_func = {
                        "matricula": matricula.strip(),
                        "nome": nome_func.strip(),
                        "cargo_nivel_acesso": cargo,
                        "cnpj_loja": cnpj_vinculo.strip(),
                        "data_admissao": str(data_admissao)
                    }
                    supabase.table("funcionario").insert(novo_func).execute()
                    st.success("Funcionário cadastrado com sucesso!")
                except Exception:
                    logger.exception("Falha ao cadastrar funcionário")
                    st.error("Não foi possível cadastrar o funcionário. Confira os dados e se a loja vinculada existe.")