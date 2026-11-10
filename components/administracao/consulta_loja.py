import streamlit as st
import pandas as pd
import logging
from database import supabase
from components.regras_negocio.filtrar_multiplas_colunas import filtrar_multiplas_colunas

logger = logging.getLogger(__name__)

NOMES_COLUNAS_LOJA = {
    "cnpj": "CNPJ",
    "nome_unidade": "Nome da unidade",
    "endereco": "Endereço"
}

def render_consulta_loja():
    with st.expander("Consultar lojas cadastradas", expanded=False):
        st.subheader("Lojas cadastradas")
        try:
            res_loja = supabase.table("loja").select("*").execute()
            df_loja = pd.DataFrame(res_loja.data or [])

            if not df_loja.empty:
                busca_loja = st.text_input(
                    "Buscar loja",
                    placeholder="Digite CNPJ, nome da unidade ou endereço...",
                    key="busca_loja"
                )

                df_loja_filtrado = filtrar_multiplas_colunas(
                    df_loja.copy(), 
                    ["cnpj", "nome_unidade", "endereco"], 
                    busca_loja.strip()
                )

                colunas_loja = [col for col in NOMES_COLUNAS_LOJA if col in df_loja_filtrado.columns]
                df_exibicao_loja = df_loja_filtrado[colunas_loja].rename(columns=NOMES_COLUNAS_LOJA)

                st.caption(f"{len(df_loja_filtrado)} unidade(s) encontrada(s)")

                if not df_exibicao_loja.empty:
                    st.dataframe(df_exibicao_loja, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma loja corresponde à sua pesquisa.")
            else:
                st.info("Nenhuma loja cadastrada.")

        except Exception:
            logger.exception("Falha ao carregar lojas")
            st.error("Não foi possível carregar a lista de lojas. Tente novamente mais tarde.")