import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from database import supabase

# ==========================================
# CONFIGURAÇÕES
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

STATUS_DISPONIVEL = "Disponivel"
STATUS_PREPARACAO = "Em preparacao"
FILTRO_TODO_HISTORICO = "Todo o Histórico"

st.set_page_config(
    page_title="GiroCar | Dashboard de Veículos",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🚙",
    layout="wide",
)


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_dados():
    """Busca veículos e transações no Supabase e retorna dois DataFrames."""
    res_veiculos = (
        supabase.table("veiculo")
        .select("placa, modelo, marca, valor_aquisicao, status_veiculo")
        .execute()
    )
    res_transacoes = (
        supabase.table("transacao")
        .select("placa_veiculo, valor_final_negociado, data")
        .execute()
    )
    return pd.DataFrame(res_veiculos.data), pd.DataFrame(res_transacoes.data)


def calcular_estoque(df_veiculos):
    """Retorna (qtd_disponivel, qtd_preparacao, capital_investido, df_preparacao)."""
    df_preparacao = pd.DataFrame()
    if df_veiculos.empty:
        return 0, 0, 0.0, df_preparacao

    df_disponivel = df_veiculos[df_veiculos["status_veiculo"] == STATUS_DISPONIVEL]
    df_preparacao = df_veiculos[df_veiculos["status_veiculo"] == STATUS_PREPARACAO]
    capital = (
        df_disponivel["valor_aquisicao"].sum()
        + df_preparacao["valor_aquisicao"].sum()
    )
    return len(df_disponivel), len(df_preparacao), capital, df_preparacao


def preparar_vendas(df_transacoes, df_veiculos):
    """Cruza transações com veículos e calcula o lucro bruto por venda."""
    df_vendas = pd.merge(
        df_transacoes, df_veiculos, left_on="placa_veiculo", right_on="placa"
    )
    df_vendas["Lucro Bruto (R$)"] = (
        df_vendas["valor_final_negociado"] - df_vendas["valor_aquisicao"]
    )
    df_vendas["data"] = pd.to_datetime(df_vendas["data"])
    df_vendas["mes_ano"] = df_vendas["data"].dt.strftime("%m/%Y")
    return df_vendas


def montar_dados_grafico(df_vendas):
    df_lucro = df_vendas[["data", "placa_veiculo", "Lucro Bruto (R$)"]].sort_values("data")
    df_lucro["Veículo"] = (
        df_vendas["marca"]
        + " "
        + df_vendas["modelo"]
        + " ("
        + df_vendas["placa_veiculo"]
        + ")"
    )
    return df_lucro


# ==========================================
# COMPONENTES DE INTERFACE
# ==========================================
def render_cabecalho():
    # CSS para alinhar a logo com o título
    st.markdown(
        """
        <style>
        .logo-girocar {
            transform: translateY(18px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_logo, col_titulo = st.columns([1, 4], vertical_alignment="center")

    with col_logo:
        if LOGO_PATH.is_file():
            st.markdown('<div class="logo-girocar">', unsafe_allow_html=True)
            st.image(str(LOGO_PATH), width=180)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            logger.error("Logo não encontrada: %s", LOGO_PATH)

    with col_titulo:
        st.title("Dashboard de Veículos")
        st.write("Visão geral em tempo real do pátio e análise de lucratividade histórica.")


def render_estoque(qtd_disponivel, qtd_preparacao, capital_investido):
    st.markdown("### Posição Atual do Pátio")

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="Veículos Disponíveis", value=f"{qtd_disponivel}")
    kpi2.metric(label="Fila da Oficina (Preparação)", value=f"{qtd_preparacao}")
    kpi3.metric(
        label="Capital Empenhado (Estoque)",
        value=f"R$ {formatar_moeda(capital_investido)}",
    )


def render_filtro_periodo(df_vendas):
    """Exibe o seletor de período e retorna (df_filtrado, rotulo_selecionado)."""
    col_filtro, _ = st.columns([1, 3])
    with col_filtro:
        meses_disponiveis = sorted(df_vendas["mes_ano"].unique(), reverse=True)
        mes_selecionado = st.selectbox(
            "Filtrar por Período:", [FILTRO_TODO_HISTORICO] + meses_disponiveis
        )

    if mes_selecionado != FILTRO_TODO_HISTORICO:
        df_vendas = df_vendas[df_vendas["mes_ano"] == mes_selecionado]
    return df_vendas, mes_selecionado


def render_vendas(df_transacoes, df_veiculos, qtd_preparacao, df_preparacao):
    st.markdown("### Análise de Vendas e Lucratividade")

    df_lucro = pd.DataFrame()
    lucro_periodo = 0.0
    qtd_vendida = 0
    rotulo_periodo = "Período"

    if not df_transacoes.empty and not df_veiculos.empty:
        df_vendas = preparar_vendas(df_transacoes, df_veiculos)
        df_vendas, rotulo_periodo = render_filtro_periodo(df_vendas)

        lucro_periodo = df_vendas["Lucro Bruto (R$)"].sum()
        qtd_vendida = len(df_vendas)
        df_lucro = montar_dados_grafico(df_vendas)

    # KPIs das vendas filtradas
    kpi_v1, kpi_v2 = st.columns(2)
    kpi_v1.metric(
        label=f"Lucro Bruto ({rotulo_periodo})",
        value=f"R$ {formatar_moeda(lucro_periodo)}",
    )
    kpi_v2.metric(label="Quantidade Vendida", value=f"{qtd_vendida} veículos")

    # Layout inferior: gráfico e oficina
    col_grafico, col_oficina = st.columns([2, 1])

    with col_grafico:
        if not df_lucro.empty:
            st.bar_chart(
                df_lucro,
                x="Veículo",
                y="Lucro Bruto (R$)",
                color="#2ca02c",
                use_container_width=True,
            )
        else:
            st.info("Nenhuma venda registrada no período selecionado.")

    with col_oficina:
        st.write("**Monitoramento da Oficina**")
        if not df_veiculos.empty and qtd_preparacao > 0:
            df_fila = df_preparacao[["placa", "marca", "modelo"]].rename(
                columns={"placa": "Placa", "marca": "Marca", "modelo": "Modelo"}
            )
            st.dataframe(df_fila, hide_index=True, use_container_width=True)
        else:
            st.success("Nenhum veículo em preparação. Pátio livre!")


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
render_cabecalho()

if not supabase:
    st.error("⚠️ Não foi possível estabelecer conexão com o banco de dados.")
    st.stop()

try:
    df_veiculos, df_transacoes = carregar_dados()

    qtd_disponivel, qtd_preparacao, capital_investido, df_preparacao = calcular_estoque(df_veiculos)

    render_estoque(qtd_disponivel, qtd_preparacao, capital_investido)
    st.divider()
    render_vendas(df_transacoes, df_veiculos, qtd_preparacao, df_preparacao)

except Exception as e:
    logger.exception("Erro ao calcular as métricas do painel")
    st.error("⚠️ Erro ao calcular as métricas do painel.")
    with st.expander("Detalhes Técnicos"):
        st.code(str(e))