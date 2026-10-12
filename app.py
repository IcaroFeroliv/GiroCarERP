import streamlit as st
from database import supabase

st.set_page_config(page_title="GiroCar ERP", layout="wide")
st.title("🚗 GiroCar ERP - Dashboard")

if supabase:
    st.success("Conexão com o banco de dados estabelecida com sucesso!")
else:
    st.warning("Verifique suas credenciais de acesso.")