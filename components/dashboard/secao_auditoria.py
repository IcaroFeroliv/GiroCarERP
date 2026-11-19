import streamlit as st
from components.regras_negocio.auditoria_vendas import obter_dados_auditoria


def render_secao_auditoria() -> None:
    """Renderiza a tabela de auditoria de transações para o perfil Gerente."""
    st.divider()
    st.markdown("### Auditoria de Transações da Rede")

    try:
        df_final = obter_dados_auditoria()
        if not df_final.empty:
            st.dataframe(df_final, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma transação registrada para auditoria.")
    except Exception as err_auditoria:
        st.error(f"Erro ao carregar auditoria de vendas: {err_auditoria}")