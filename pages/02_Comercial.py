import logging
from pathlib import Path
import pandas as pd
import streamlit as st
from database import supabase

# Importações de Regras de Negócio e Componentes Visuais
from components.regras_negocio.calcular_kpis_comercial import calcular_kpis_comercial
from components.comercial.cabecalho import render_cabecalho
from components.comercial.kpis_comercial import render_kpis_comercial
from components.comercial.aba_historico import render_aba_historico
from components.comercial.aba_venda import render_aba_venda
from components.comercial.aba_pagamento import render_aba_pagamento

# =========================================================
# CONFIGURAÇÕES
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Comercial e Vendas | GiroCar",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🚗",
    layout="wide",
)

# =========================================================
# MAESTRO - EXECUÇÃO PRINCIPAL
# =========================================================
render_cabecalho()

with st.spinner("Carregando informações comerciais..."):
    try:
        resposta_vendas = supabase.table("transacao").select("*").execute()
        vendas = resposta_vendas.data or []
        erro_carregamento_vendas = False
    except Exception as erro:
        logger.exception("Erro ao carregar vendas: %s", erro)
        vendas = []
        erro_carregamento_vendas = True

if erro_carregamento_vendas:
    st.warning("Não foi possível carregar o histórico de vendas. Confira a conexão com o banco de dados.")

df_vendas = pd.DataFrame(vendas)

# 1. Processamento e Renderização de Indicadores
total_vendas, faturamento_negociado, ticket_medio = calcular_kpis_comercial(df_vendas)
render_kpis_comercial(total_vendas, faturamento_negociado, ticket_medio)

# 2. Renderização das Abas
aba_historico, aba_venda, aba_pagamento = st.tabs([
    " Histórico de vendas",
    " Registrar venda",
    " Lançar pagamento",
])

with aba_historico:
    render_aba_historico(df_vendas)

with aba_venda:
    render_aba_venda()

with aba_pagamento:
    render_aba_pagamento()