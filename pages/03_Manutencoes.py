import logging
from pathlib import Path
import streamlit as st
from database import supabase

# Importações dos Componentes Visuais
from components.manutencoes.cabecalho import render_cabecalho
from components.manutencoes.aba_historico import render_aba_historico
from components.manutencoes.aba_nova import render_aba_nova

# ==========================================
# CONFIGURAÇÕES GERAIS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

st.set_page_config(
    page_title="Oficina e Manutenções | GiroCar",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🔧",
    layout="wide",
)

# ==========================================
# MAESTRO - EXECUÇÃO PRINCIPAL
# ==========================================
render_cabecalho()

if not supabase:
    st.error("Não foi possível conectar ao banco de dados.")
    st.stop()

aba_historico, aba_nova = st.tabs([
    " Histórico de serviços", 
    " Registrar manutenção"
])

with aba_historico:
    render_aba_historico()

with aba_nova:
    render_aba_nova()