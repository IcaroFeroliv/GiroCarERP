import requests
import streamlit as st
from components.regras_negocio.fipe_core import FIPE_BASE_URL, FIPE_HEADERS
from components.regras_negocio.mostrar_detalhes_tecnicos import mostrar_detalhes_tecnicos
from components.veiculos.vinculo_fipe import render_vinculo_fipe

def render_resultado_fipe(cod_marca, cod_modelo, cod_ano):
    st.divider()
    try:
        req_final = requests.get(
            f"{FIPE_BASE_URL}/marcas/{cod_marca}/modelos/{cod_modelo}/anos/{cod_ano}",
            headers=FIPE_HEADERS,
        )

        if req_final.status_code != 200:
            st.error("Falha ao comunicar com o servidor da Tabela FIPE.")
            return

        dados = req_final.json()
        v_fipe = dados.get("Valor")
        m_ref = dados.get("MesReferencia")
        c_fipe = dados.get("CodigoFipe")

        st.subheader("📊 Resultado da Avaliação Oficial")
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Valor de Mercado", v_fipe)
        col_r2.metric("Mês de Referência", m_ref)
        col_r3.metric("Código FIPE Encontrado", c_fipe)

        st.write("---")
        render_vinculo_fipe(v_fipe)

    except Exception as e:
        st.error("Erro técnico ao realizar a consulta final.")
        mostrar_detalhes_tecnicos(e, titulo="Detalhes Técnicos")