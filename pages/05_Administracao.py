import logging
from pathlib import Path
import streamlit as st
from database import supabase

# Importações dos Componentes Visuais
from components.administracao.cabecalho import render_cabecalho
from components.administracao.aba_lojas import render_aba_lojas
from components.administracao.aba_funcionarios import render_aba_funcionarios

# ==========================================
# CONFIGURAÇÕES GERAIS
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

st.set_page_config(
    page_title="GiroCar | Administração",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🚗",
    layout="wide"
)

# ==========================================
# MAESTRO - EXECUÇÃO PRINCIPAL
# ==========================================
render_cabecalho()

if supabase is None:
    st.error(
        "Não foi possível conectar ao sistema. "
        "Tente novamente mais tarde ou entre em contato com o suporte."
    )
    st.stop()

aba_lojas, aba_funcionarios = st.tabs(["Lojas (Filiais)", "Funcionários"])

with aba_lojas:
    render_aba_lojas()

with aba_funcionarios:
    render_aba_funcionarios()