import streamlit as st
import pandas as pd
import logging
from database import supabase
from components.regras_negocio.filtrar_multiplas_colunas import filtrar_multiplas_colunas

logger = logging.getLogger(__name__)

NOMES_COLUNAS_FORN = {
    "cnpj_cpf": "CPF/CNPJ",
    "nome_razao_social": "Nome / Razão Social",
    "telefone": "Telefone",
    "tipo_origem": "Origem"
}

def render_consulta_fornecedor():
    with st.expander("Consultar fornecedores", expanded=False):
        st.subheader("Fornecedores cadastrados")
        try:
            res_forn = supabase.table("fornecedor").select("*").execute()
            df_forn = pd.DataFrame(res_forn.data or [])

            if not df_forn.empty:
                busca_forn = st.text_input(
                    "Buscar fornecedor",
                    placeholder="Digite nome, CPF/CNPJ ou telefone...",
                    key="busca_fornecedor"
                )

                df_forn_filtrado = filtrar_multiplas_colunas(
                    df_forn.copy(), 
                    ["cnpj_cpf", "nome_razao_social", "telefone"], 
                    busca_forn.strip()
                )

                colunas_forn = [col for col in NOMES_COLUNAS_FORN if col in df_forn_filtrado.columns]
                df_exibicao_forn = df_forn_filtrado[colunas_forn].rename(columns=NOMES_COLUNAS_FORN)

                st.caption(f"{len(df_forn_filtrado)} fornecedor(es) encontrado(s)")

                if not df_exibicao_forn.empty:
                    st.dataframe(df_exibicao_forn, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum fornecedor corresponde à sua pesquisa.")
            else:
                st.info("Nenhum fornecedor cadastrado.")

        except Exception:
            logger.exception("Erro ao carregar fornecedores")
            st.error("Erro ao carregar a lista de fornecedores.")