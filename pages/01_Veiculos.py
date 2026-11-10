import logging
from pathlib import Path
import streamlit as st
from database import supabase

# Importações dos Componentes Visuais
from components.veiculos.cabecalho import render_cabecalho
from components.veiculos.aba_consulta import render_aba_consulta
from components.veiculos.aba_cadastro import render_aba_cadastro
from components.veiculos.aba_fipe import render_aba_fipe
from components.veiculos.aba_historico import render_aba_historico

# ==========================================
# CONFIGURAÇÕES GERAIS
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

st.set_page_config(
    page_title="GiroCar | Gestão de Veículos",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "",
    layout="wide",
)

# ==========================================
# MAESTRO - EXECUÇÃO PRINCIPAL
# ==========================================
render_cabecalho()

if not supabase:
    st.error("Não foi possível estabelecer conexão com o banco de dados. Verifique sua conexão de rede ou tente novamente mais tarde.")
    st.stop()

aba_consulta, aba_cadastro, aba_fipe, aba_historico = st.tabs([
    "Consultar e Gerenciar",
    "Cadastrar Veículo",
    "Consulta Tabela FIPE",
    "Histórico de Avaliações",
])

with aba_consulta:
    render_aba_consulta()

with aba_cadastro:
    render_aba_cadastro()

with aba_fipe:
    render_aba_fipe()

with aba_historico:
    render_aba_historico()