import streamlit as st
from components.regras_negocio.formatar_reais import formatar_reais

COLUNAS_RENOMEADAS_VEICULO = {
    "placa": "Placa", "chassi": "Chassi", "marca": "Marca", "modelo": "Modelo",
    "ano_fabricacao": "Ano Fab.", "ano_modelo": "Ano Mod.", "cor": "Cor",
    "quilometragem": "KM", "valor_aquisicao": "Valor de Aquisição",
    "status_veiculo": "Status", "indicador_leilao": "Leilão?",
    "indicador_sinistro": "Sinistro?", "cnpj_loja": "CNPJ Loja",
    "cnpj_cpf_fornecedor": "Doc. Fornecedor",
}

COLUNAS_MOSTRAR_VEICULO = [
    "Placa", "Marca", "Modelo", "Cor", "Ano Fab.", "Ano Mod.",
    "KM", "Valor de Aquisição", "Status", "Leilão?", "Sinistro?",
]

def render_tabela_veiculos(df_filtrado):
    df_formatado = df_filtrado.copy()
    df_formatado["valor_aquisicao"] = df_formatado["valor_aquisicao"].apply(formatar_reais)
    df_exibicao = df_formatado.rename(columns=COLUNAS_RENOMEADAS_VEICULO)
    st.dataframe(df_exibicao[COLUNAS_MOSTRAR_VEICULO], use_container_width=True, hide_index=True)