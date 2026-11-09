import streamlit as st
from components.regras_negocio.fipe_marcas import get_marcas
from components.regras_negocio.fipe_modelos import get_modelos
from components.regras_negocio.fipe_anos import get_anos
from components.veiculos.resultado_fipe import render_resultado_fipe

FIPE_SELECIONE = "-- Selecione --"

def render_aba_fipe():
    st.subheader("Consultar Avaliação de Veículos (Tabela FIPE)")
    st.write("Pesquise o valor de mercado de qualquer veículo para avaliação de troca ou para atualizar o estoque atual.")

    col_f1, col_f2, col_f3 = st.columns(3)
    marcas = get_marcas()
    opcoes_marcas = {m["nome"]: m["codigo"] for m in marcas} if marcas else {}

    with col_f1:
        marca_sel = st.selectbox("1. Selecione a Marca", [FIPE_SELECIONE] + list(opcoes_marcas.keys()))

    if marca_sel == FIPE_SELECIONE:
        return

    cod_marca = opcoes_marcas[marca_sel]
    opcoes_modelos = {m["nome"]: m["codigo"] for m in get_modelos(cod_marca)}

    with col_f2:
        modelo_sel = st.selectbox("2. Selecione o Modelo", [FIPE_SELECIONE] + list(opcoes_modelos.keys()))

    if modelo_sel == FIPE_SELECIONE:
        return

    cod_modelo = opcoes_modelos[modelo_sel]
    opcoes_anos = {a["nome"]: a["codigo"] for a in get_anos(cod_marca, cod_modelo)}

    with col_f3:
        ano_sel = st.selectbox("3. Selecione o Ano/Combustível", [FIPE_SELECIONE] + list(opcoes_anos.keys()))

    if ano_sel != FIPE_SELECIONE:
        render_resultado_fipe(cod_marca, cod_modelo, opcoes_anos[ano_sel])