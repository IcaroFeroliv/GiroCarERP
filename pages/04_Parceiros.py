import logging
from pathlib import Path
import streamlit as st
from database import supabase

# Importações dos Componentes Visuais
from components.parceiros.cabecalho import render_cabecalho
from components.parceiros.aba_clientes import render_aba_clientes
from components.parceiros.aba_fornecedores import render_aba_fornecedores

# ==========================================
# CONFIGURAÇÕES GERAIS
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

st.set_page_config(
    page_title="Parceiros Comerciais",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🤝",
    layout="wide"
)

# ==========================================
# MAESTRO - EXECUÇÃO PRINCIPAL
# ==========================================
render_cabecalho()

if supabase is None:
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

aba_clientes, aba_fornecedores = st.tabs(["Clientes (CRM)", "Fornecedores"])

with aba_clientes:
    render_aba_clientes()

with aba_fornecedores:
    render_aba_fornecedores()