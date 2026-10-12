import streamlit as st
import pandas as pd
from database import supabase

# Configuração da página principal (deve ser o primeiro comando)
st.set_page_config(page_title="GiroCar ERP", page_icon="🚗", layout="wide")

st.title("🚗 GiroCar ERP - Dashboard Gerencial")
st.write("Bem-vindo ao sistema central de gestão de concessionárias.")

# Verifica a conexão com o banco (Critério de Tratamento de Erros)
if not supabase:
    st.error("⚠️ Erro crítico: Sem conexão com o banco de dados. Verifique o arquivo secrets.toml.")
    st.stop()

st.divider()

# RN07 - Inventário Dinâmico: O estoque é calculado através de um SELECT COUNT dinâmico
try:
    # Ajustado para minúsculo: valor_aquisicao e status_veiculo
    response = supabase.table("veiculo").select("valor_aquisicao").eq("status_veiculo", "Estoque").execute()
    veiculos_estoque = response.data
    
    # Processa os KPIs
    quantidade_estoque = len(veiculos_estoque)
    # Ajustado a chave do dicionário para minúsculo
    capital_investido = sum([v["valor_aquisicao"] for v in veiculos_estoque])
    
    # Exibe os indicadores na tela
    st.subheader("📊 Visão Geral do Pátio (Em Tempo Real)")
    col1, col2, col3 = st.columns(3)
    
    col1.metric(label="Veículos em Estoque (Unidades)", value=f"{quantidade_estoque}")
    col2.metric(label="Capital Investido no Estoque", value=f"R$ {capital_investido:,.2f}")
    col3.metric(label="Status do Sistema", value="Online 🟢")

except Exception as e:
    st.error(f"Erro ao carregar os indicadores do dashboard. Detalhe técnico: {e}")

st.write("---")
st.info("👈 Utilize o menu lateral para navegar entre os módulos do ERP (Veículos, Transações, etc).")