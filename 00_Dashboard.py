import logging
from pathlib import Path
import pandas as pd
import streamlit as st
from database import supabase

# Importações de Regras de Negócio
from components.regras_negocio.carregar_dados_dashboard import carregar_dados
from components.regras_negocio.calcular_estoque import calcular_estoque
from components.regras_negocio.preparar_vendas import preparar_vendas
from components.regras_negocio.montar_dados_grafico import montar_dados_grafico


# Importações de Componentes Visuais
from components.dashboard.cabecalho import render_cabecalho
from components.dashboard.kpis_estoque import render_estoque
from components.dashboard.filtro_periodo import render_filtro_periodo
from components.dashboard.kpis_vendas import render_kpis_vendas
from components.dashboard.grafico_lucratividade import render_grafico_lucratividade
from components.dashboard.monitoramento_oficina import render_monitoramento_oficina

# ==========================================
# CONFIGURAÇÕES GERAIS
# ==========================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

st.set_page_config(
    page_title="GiroCar | Dashboard de Veículos",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🚙",
    layout="wide",
)

# ==========================================
# MAESTRO - EXECUÇÃO PRINCIPAL
# ==========================================

render_cabecalho()

if not supabase:
    st.error("⚠️ Não foi possível estabelecer conexão com o banco de dados.")
    st.stop()

try:
    # 1. Carregamento e Preparação de Dados Globais
    df_veiculos, df_transacoes = carregar_dados()

    # 2. Renderização: Posição do Estoque
    qtd_disponivel, qtd_preparacao, capital_investido, df_preparacao = calcular_estoque(df_veiculos)
    render_estoque(qtd_disponivel, qtd_preparacao, capital_investido)

    st.divider()

    # 3. Processamento e Renderização: Análise de Vendas
    st.markdown("### Análise de Vendas e Lucratividade")
    
    df_lucro = pd.DataFrame()
    lucro_periodo = 0.0
    qtd_vendida = 0
    rotulo_periodo = "Período"

    if not df_transacoes.empty and not df_veiculos.empty:
        df_vendas = preparar_vendas(df_transacoes, df_veiculos)
        
        # Filtro Modifica os Dados em Tela
        df_vendas, rotulo_periodo = render_filtro_periodo(df_vendas)

        # Recálculo das variáveis pós-filtro para alimentar as renderizações
        lucro_periodo = df_vendas["Lucro Bruto (R$)"].sum()
        qtd_vendida = len(df_vendas)
        df_lucro = montar_dados_grafico(df_vendas)

    # Renderiza KPIs
    render_kpis_vendas(lucro_periodo, qtd_vendida, rotulo_periodo)

    # Renderiza Seção Inferior Dividida
    col_grafico, col_oficina = st.columns([2, 1])
    
    with col_grafico:
        render_grafico_lucratividade(df_lucro)
        
    with col_oficina:
        render_monitoramento_oficina(df_veiculos, qtd_preparacao, df_preparacao)

except Exception as e:
    logger.exception("Erro ao calcular as métricas do painel")
    st.error("⚠️ Erro ao calcular as métricas do painel.")
    with st.expander("Detalhes Técnicos"):
        st.code(str(e))