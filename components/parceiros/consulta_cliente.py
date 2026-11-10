import streamlit as st
import pandas as pd
import logging
from database import supabase
from components.regras_negocio.filtrar_multiplas_colunas import filtrar_multiplas_colunas

logger = logging.getLogger(__name__)

NOMES_COLUNAS_CLIENTE = {
    "cpf_cnpj": "CPF/CNPJ",
    "nome_completo": "Nome do cliente",
    "telefone": "Telefone",
    "email": "E-mail",
    "status_funil_vendas": "Status comercial"
}

def render_consulta_cliente():
    with st.expander("Consultar clientes", expanded=False):
        st.subheader("Clientes cadastrados")
        try:
            res_cli = supabase.table("cliente").select("*").execute()
            df_cli = pd.DataFrame(res_cli.data or [])

            if not df_cli.empty:
                busca_cliente = st.text_input(
                    "Buscar cliente",
                    placeholder="Digite nome, CPF/CNPJ, telefone ou e-mail...",
                    key="busca_cliente"
                )

                if "status_funil_vendas" in df_cli.columns:
                    status_opcoes = df_cli["status_funil_vendas"].dropna().astype(str).unique().tolist()
                    status_opcoes.sort()
                    status_selecionado = st.selectbox(
                        "Filtrar por status comercial",
                        ["Todos"] + status_opcoes,
                        key="filtro_status_cliente"
                    )
                else:
                    status_selecionado = "Todos"

                df_filtrado = filtrar_multiplas_colunas(
                    df_cli.copy(), 
                    ["cpf_cnpj", "nome_completo", "telefone", "email"], 
                    busca_cliente.strip()
                )

                if status_selecionado != "Todos" and "status_funil_vendas" in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado["status_funil_vendas"] == status_selecionado]

                colunas_cliente = [col for col in NOMES_COLUNAS_CLIENTE if col in df_filtrado.columns]
                df_exibicao_cliente = df_filtrado[colunas_cliente].rename(columns=NOMES_COLUNAS_CLIENTE)

                st.caption(f"{len(df_filtrado)} cliente(s) encontrado(s)")

                if not df_exibicao_cliente.empty:
                    st.dataframe(df_exibicao_cliente, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum cliente corresponde à sua pesquisa.")
            else:
                st.info("Nenhum cliente cadastrado.")

        except Exception:
            logger.exception("Erro ao carregar clientes")
            st.error("Erro ao carregar a lista de clientes.")