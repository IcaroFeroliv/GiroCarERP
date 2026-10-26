import streamlit as st
import pandas as pd
from database import supabase
from pathlib import Path
import logging

# Configuração dos logs técnicos
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho da logo na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

# Configuração da página
st.set_page_config(
    page_title="GiroCar | Dashboard de Veículos",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🚙",
    layout="wide"
)

# CSS para alinhar a logo com o título
st.markdown(
    """
    <style>
    .logo-girocar {
        transform: translateY(18px);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Cabeçalho com a logo alinhada ao título
col_logo, col_titulo = st.columns(
    [1, 4],
    vertical_alignment="center"
)

with col_logo:
    if LOGO_PATH.is_file():
        st.markdown(
            '<div class="logo-girocar">',
            unsafe_allow_html=True
        )
        st.image(str(LOGO_PATH), width=180)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        logger.error("Logo não encontrada: %s", LOGO_PATH)

with col_titulo:
    st.title("Deshboard de Veículos  ")
    st.write("Visão geral em tempo real do pátio e análise de lucratividade histórica.")

if not supabase:
    st.error("⚠️ Não foi possível estabelecer conexão com o banco de dados.")
    st.stop()

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

try:
    # 1. Busca dos Dados
    res_veiculos = supabase.table("veiculo").select("placa, modelo, marca, valor_aquisicao, status_veiculo").execute()
    res_transacoes = supabase.table("transacao").select("placa_veiculo, valor_final_negociado, data").execute()
    
    df_veiculos = pd.DataFrame(res_veiculos.data)
    df_transacoes = pd.DataFrame(res_transacoes.data)
    
    # ==========================================
    # BLOCO 1: VISÃO DE ESTOQUE (Tempo Real)
    # ==========================================
    st.markdown("### Posição Atual do Pátio")
    
    qtd_disponivel = 0
    qtd_preparacao = 0
    capital_investido = 0.0
    
    if not df_veiculos.empty:
        df_disponivel = df_veiculos[df_veiculos["status_veiculo"] == "Disponivel"]
        df_preparacao = df_veiculos[df_veiculos["status_veiculo"] == "Em preparacao"]
        
        qtd_disponivel = len(df_disponivel)
        qtd_preparacao = len(df_preparacao)
        capital_investido = df_disponivel["valor_aquisicao"].sum() + df_preparacao["valor_aquisicao"].sum()
        
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="Veículos Disponíveis", value=f"{qtd_disponivel}")
    kpi2.metric(label="Fila da Oficina (Preparação)", value=f"{qtd_preparacao}")
    kpi3.metric(label="Capital Empenhado (Estoque)", value=f"R$ {formatar_moeda(capital_investido)}")
    
    st.divider()
    
    # ==========================================
    # BLOCO 2: DESEMPENHO E LUCROS (Com Filtro)
    # ==========================================
    st.markdown("### Análise de Vendas e Lucratividade")
    
    df_lucro = pd.DataFrame()
    lucro_periodo = 0.0
    qtd_vendida = 0
    
    if not df_transacoes.empty and not df_veiculos.empty:
        # Merge das tabelas para calcular o lucro
        df_vendas = pd.merge(df_transacoes, df_veiculos, left_on="placa_veiculo", right_on="placa")
        df_vendas["Lucro Bruto (R$)"] = df_vendas["valor_final_negociado"] - df_vendas["valor_aquisicao"]
        
        # Converte a data para extrair o Mês/Ano e facilitar o filtro
        df_vendas["data"] = pd.to_datetime(df_vendas["data"])
        df_vendas["mes_ano"] = df_vendas["data"].dt.strftime("%m/%Y")
        
        # UI do Filtro de Período
        col_filtro, _ = st.columns([1, 3])
        with col_filtro:
            meses_disponiveis = sorted(df_vendas["mes_ano"].unique(), reverse=True)
            mes_selecionado = st.selectbox("Filtrar por Período:", ["Todo o Histórico"] + meses_disponiveis)
            
        # Aplica o filtro
        if mes_selecionado != "Todo o Histórico":
            df_vendas = df_vendas[df_vendas["mes_ano"] == mes_selecionado]
            
        lucro_periodo = df_vendas["Lucro Bruto (R$)"].sum()
        qtd_vendida = len(df_vendas)
        
        # Prepara dados finais pro gráfico
        df_lucro = df_vendas[["data", "placa_veiculo", "Lucro Bruto (R$)"]].sort_values("data")
        df_lucro["Veículo"] = df_vendas["marca"] + " " + df_vendas["modelo"] + " (" + df_vendas["placa_veiculo"] + ")"
    
    # Exibe KPIs das vendas filtradas
    kpi_v1, kpi_v2 = st.columns(2)
    kpi_v1.metric(label=f"Lucro Bruto ({mes_selecionado if 'mes_selecionado' in locals() else 'Período'})", value=f"R$ {formatar_moeda(lucro_periodo)}")
    kpi_v2.metric(label="Quantidade Vendida", value=f"{qtd_vendida} veículos")
    
    # Layout Inferior: Gráfico e Oficina
    col_grafico, col_oficina = st.columns([2, 1])
    
    with col_grafico:
        if not df_lucro.empty:
            st.bar_chart(df_lucro, x="Veículo", y="Lucro Bruto (R$)", color="#2ca02c", use_container_width=True)
        else:
            st.info("Nenhuma venda registrada no período selecionado.")
            
    with col_oficina:
        st.write("**Monitoramento da Oficina**")
        if not df_veiculos.empty and qtd_preparacao > 0:
            df_fila = df_preparacao[["placa", "marca", "modelo"]].rename(columns={"placa": "Placa", "marca": "Marca", "modelo": "Modelo"})
            st.dataframe(df_fila, hide_index=True, use_container_width=True)
        else:
            st.success("Nenhum veículo em preparação. Pátio livre!")

except Exception as e:
    st.error("⚠️ Erro ao calcular as métricas do painel.")
    with st.expander("Detalhes Técnicos"):
        st.code(str(e))