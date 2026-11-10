import streamlit as st
import pandas as pd
import logging
from database import supabase
from components.regras_negocio.filtrar_multiplas_colunas import filtrar_multiplas_colunas

logger = logging.getLogger(__name__)

NOMES_COLUNAS_FUNC = {
    "matricula": "Matrícula",
    "nome": "Nome do funcionário",
    "cargo_nivel_acesso": "Cargo",
    "cnpj_loja": "CNPJ da loja",
    "data_admissao": "Data de admissão"
}

def render_consulta_funcionario():
    with st.expander("Consultar funcionários", expanded=False):
        st.subheader("Quadro de Funcionários")
        try:
            res_func = supabase.table("funcionario").select("*").execute()
            df_func = pd.DataFrame(res_func.data or [])

            if not df_func.empty:
                col_filtro, col_busca = st.columns([1, 2])

                if "cargo_nivel_acesso" in df_func.columns:
                    cargos_disponiveis = df_func["cargo_nivel_acesso"].dropna().astype(str).unique().tolist()
                    cargos_disponiveis.sort()
                    with col_filtro:
                        cargo_selecionado = st.selectbox(
                            "Filtrar por cargo",
                            ["Todos"] + cargos_disponiveis,
                            key="filtro_cargo_funcionario"
                        )
                else:
                    cargo_selecionado = "Todos"

                with col_busca:
                    busca_func = st.text_input(
                        "Buscar funcionário",
                        placeholder="Digite matrícula, nome ou CNPJ da loja...",
                        key="busca_funcionario"
                    )

                df_func_filtrado = df_func.copy()

                if cargo_selecionado != "Todos":
                    df_func_filtrado = df_func_filtrado[df_func_filtrado["cargo_nivel_acesso"] == cargo_selecionado]

                df_func_filtrado = filtrar_multiplas_colunas(
                    df_func_filtrado, 
                    ["matricula", "nome", "cnpj_loja", "data_admissao"], 
                    busca_func.strip()
                )

                colunas_func = [col for col in NOMES_COLUNAS_FUNC if col in df_func_filtrado.columns]
                df_exibicao_func = df_func_filtrado[colunas_func].rename(columns=NOMES_COLUNAS_FUNC)

                st.caption(f"{len(df_func_filtrado)} funcionário(s) encontrado(s)")

                if not df_exibicao_func.empty:
                    st.dataframe(df_exibicao_func, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum funcionário corresponde à sua pesquisa.")
            else:
                st.info("Nenhum funcionário cadastrado.")

        except Exception:
            logger.exception("Falha ao carregar funcionários")
            st.error("Não foi possível carregar a lista de funcionários. Tente novamente mais tarde.")