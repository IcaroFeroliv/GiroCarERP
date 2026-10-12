import streamlit as st
import pandas as pd
from database import supabase

# Configuração da página principal (deve ser o primeiro comando)
st.set_page_config(page_title="GiroCar ERP", page_icon="🚗", layout="wide")

st.title("GiroCar ERP - Dashboard Gerencial")
st.write("Bem-vindo ao sistema central de gestão de concessionárias.")

# Verifica a conexão com o banco (Critério de Tratamento de Erros)
if not supabase:
    st.error("⚠️ Erro crítico: Sem conexão com o banco de dados. Verifique o arquivo secrets.toml.")
    st.stop()

st.divider()

# RN07 - Inventário Dinâmico: O estoque é calculado através de um SELECT COUNT dinâmico
try:
    response = supabase.table("veiculo").select("valor_aquisicao").eq("status_veiculo", "Disponivel").execute()
    veiculos_estoque = response.data
    
    quantidade_estoque = len(veiculos_estoque)
    capital_investido = sum([v["valor_aquisicao"] for v in veiculos_estoque])
    
    valor_br = f"{capital_investido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    st.subheader("Visão Geral do Pátio (Em Tempo Real)")
    col1, col2, col3 = st.columns(3)
    
    col1.metric(label="Veículos Disponíveis", value=f"{quantidade_estoque}")
    col2.metric(label="Capital Investido", value=f"R$ {valor_br}")
    col3.metric(label="Status do Sistema", value="Online")

except Exception as e:
    st.error(f"Erro ao carregar os indicadores do dashboard. Detalhe técnico: {e}")


st.write("---")
st.info("Utilize o menu lateral para navegar entre os módulos do ERP (Veículos, Transações, etc).")