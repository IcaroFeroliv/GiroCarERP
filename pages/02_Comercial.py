
import logging
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

from database import supabase


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
# IDENTIDADE VISUAL
# =========================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
        }

        .girocar-subtitle {
            color: #8b95a5;
            font-size: 0.95rem;
            margin-top: -12px;
            margin-bottom: 22px;
        }

        .metric-card {
            padding: 18px;
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-radius: 12px;
            min-height: 110px;
        }

        .section-caption {
            color: #8b95a5;
            font-size: 0.9rem;
        }

        div[data-testid="stForm"] {
            border-radius: 12px;
            padding: 20px;
        }

        div[data-testid="stMetric"] {
            padding: 4px 0;
        }

        div.stButton > button,
        div.stFormSubmitButton > button {
            border-radius: 8px;
            font-weight: 600;
            min-height: 42px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def formatar_moeda(valor):
    """Formata um valor numérico para o padrão monetário brasileiro."""
    try:
        valor = float(valor or 0)
        valor_formatado = f"{valor:,.2f}"
        valor_formatado = (
            valor_formatado
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        return f"R$ {valor_formatado}"
    except (ValueError, TypeError):
        return "R$ 0,00"


def mostrar_erro(acao, erro):
    """Registra o erro técnico e mostra uma mensagem amigável."""
    logger.exception("%s: %s", acao, erro)
    st.error(
        f"Não foi possível {acao.lower()}. "
        "Verifique a conexão e tente novamente."
    )


def obter_dados(tabela, colunas="*"):
    """Consulta uma tabela sem interromper toda a página em caso de falha."""
    try:
        resposta = supabase.table(tabela).select(colunas).execute()
        return resposta.data or []
    except Exception as erro:
        logger.exception("Erro ao consultar a tabela %s: %s", tabela, erro)
        st.error(f"Não foi possível carregar os dados de {tabela}.")
        return []


def nome_cliente(cliente):
    return f"{cliente.get('nome_completo', 'Sem nome')} — {cliente.get('cpf_cnpj', '')}"


def nome_funcionario(funcionario):
    return f"{funcionario.get('nome', 'Sem nome')} — Matrícula {funcionario.get('matricula', '')}"


def nome_veiculo(veiculo):
    return f"{veiculo.get('placa', '')} — {veiculo.get('modelo', 'Modelo não informado')}"


def nome_transacao(transacao):
    return (
        f"Venda #{transacao.get('id_transacao')} — "
        f"{transacao.get('placa_veiculo', '')} — "
        f"{formatar_moeda(transacao.get('valor_final_negociado', 0))}"
    )


# =========================================================
# CABEÇALHO
# =========================================================

col_logo, col_titulo = st.columns([1, 6], vertical_alignment="center")

with col_logo:
    if LOGO_PATH.is_file():
        st.image(str(LOGO_PATH), width=110)
    else:
        st.markdown("# 🚗")

with col_titulo:
    st.title("Comercial e Gestão de Vendas")
    st.markdown(
        '<p class="girocar-subtitle">'
        "Central de acompanhamento de vendas e pagamentos do GiroCarERP."
        "</p>",
        unsafe_allow_html=True,
    )

st.divider()


# =========================================================
# CARREGAMENTO DAS VENDAS
# =========================================================

with st.spinner("Carregando informações comerciais..."):
    try:
        resposta_vendas = (
            supabase.table("transacao")
            .select("*")
            .execute()
        )
        vendas = resposta_vendas.data or []
        erro_carregamento_vendas = False
    except Exception as erro:
        logger.exception("Erro ao carregar vendas: %s", erro)
        vendas = []
        erro_carregamento_vendas = True

if erro_carregamento_vendas:
    st.warning(
        "Não foi possível carregar o histórico de vendas. "
        "Confira a conexão com o banco de dados."
    )

df_vendas = pd.DataFrame(vendas)

if not df_vendas.empty and "valor_final_negociado" in df_vendas.columns:
    valores = pd.to_numeric(
        df_vendas["valor_final_negociado"],
        errors="coerce",
    ).fillna(0)
else:
    valores = pd.Series(dtype="float64")


# =========================================================
# INDICADORES
# =========================================================

total_vendas = len(vendas)
faturamento_negociado = float(valores.sum()) if not valores.empty else 0.0
ticket_medio = (
    faturamento_negociado / total_vendas
    if total_vendas > 0
    else 0.0
)

m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        label="Vendas registradas",
        value=f"{total_vendas}",
        help="Quantidade de registros encontrados na tabela transacao.",
    )

with m2:
    st.metric(
        label="Total negociado",
        value=formatar_moeda(faturamento_negociado),
        help="Soma dos valores registrados nas vendas.",
    )

with m3:
    st.metric(
        label="Ticket médio",
        value=formatar_moeda(ticket_medio),
        help="Valor médio das vendas registradas.",
    )

st.divider()


# =========================================================
# ABAS COMERCIAIS
# =========================================================

aba_historico, aba_venda, aba_pagamento = st.tabs(
    [
        " Histórico de vendas",
        " Registrar venda",
        " Lançar pagamento",
    ]
)


# =========================================================
# ABA 1 — HISTÓRICO DE VENDAS
# =========================================================

with aba_historico:
    st.subheader("Histórico de vendas")
    st.caption("Consulte os registros comerciais existentes no sistema.")

    if df_vendas.empty:
        st.info("Nenhuma venda foi encontrada para exibição.")
    else:
        df_exibicao = df_vendas.copy()

        if "valor_final_negociado" in df_exibicao.columns:
            df_exibicao["valor_final_negociado"] = pd.to_numeric(
                df_exibicao["valor_final_negociado"],
                errors="coerce",
            ).map(formatar_moeda)

        # Mantém todos os campos retornados pelo banco.
        # Não altera nem exclui dados da tabela original.
        st.dataframe(
    df_exibicao,
    width="stretch",
    hide_index=True,
    column_config={
        "valor_final_negociado": st.column_config.TextColumn(
            "Valor negociado"
        ),
        "data": st.column_config.TextColumn("Data da venda"),
        "placa_veiculo": st.column_config.TextColumn("Placa"),
    },
)

        st.caption(f"Total de registros exibidos: {len(df_exibicao)}")


# =========================================================
# ABA 2 — REGISTRAR VENDA
# =========================================================

with aba_venda:
    st.subheader("Registrar nova venda")
    st.caption("Preencha os dados da negociação para cadastrar a venda.")

    if st.button(
        " Atualizar opções de cadastro",
        key="atualizar_opcoes_venda",
    ):
        st.rerun()

    veiculos = obter_dados("veiculo", "placa, modelo").copy() if False else None

    try:
        resposta_veiculos = (
            supabase.table("veiculo")
            .select("placa, modelo")
            .eq("status_veiculo", "Disponivel")
            .execute()
        )
        veiculos = resposta_veiculos.data or []

        resposta_clientes = (
            supabase.table("cliente")
            .select("cpf_cnpj, nome_completo")
            .execute()
        )
        clientes = resposta_clientes.data or []

        resposta_funcionarios = (
            supabase.table("funcionario")
            .select("matricula, nome")
            .execute()
        )
        funcionarios = resposta_funcionarios.data or []

        erro_opcoes = False

    except Exception as erro:
        logger.exception("Erro ao carregar opções para venda: %s", erro)
        veiculos = []
        clientes = []
        funcionarios = []
        erro_opcoes = True

    if erro_opcoes:
        st.error(
            "Não foi possível carregar os dados necessários para a venda. "
            "Verifique a conexão com o banco."
        )

    elif not veiculos:
        st.warning("Não há veículos disponíveis para venda no momento.")

    elif not clientes:
        st.warning("Cadastre um cliente antes de registrar uma venda.")

    elif not funcionarios:
        st.warning("Cadastre um funcionário antes de registrar uma venda.")

    else:
        with st.form("form_nova_venda", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                veiculo_selecionado = st.selectbox(
                    "Veículo disponível",
                    options=veiculos,
                    format_func=nome_veiculo,
                )

                cliente_selecionado = st.selectbox(
                    "Cliente",
                    options=clientes,
                    format_func=nome_cliente,
                )

            with col2:
                funcionario_selecionado = st.selectbox(
                    "Funcionário responsável",
                    options=funcionarios,
                    format_func=nome_funcionario,
                )

                data_venda = st.date_input(
                    "Data da venda",
                    value=date.today(),
                    format="DD/MM/YYYY",
                )

            valor_negociado = st.number_input(
                "Valor final negociado (R$)",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
            )

            confirmar_venda = st.form_submit_button(
                "Registrar venda",
                type="primary",
                width="stretch",
            )

        if confirmar_venda:
            dados_venda = {
                "data": data_venda.isoformat(),
                "placa_veiculo": veiculo_selecionado["placa"],
                "cpf_cnpj_cliente": cliente_selecionado["cpf_cnpj"],
                "matricula_funcionario": funcionario_selecionado["matricula"],
                "valor_final_negociado": valor_negociado,
            }

            try:
                # Mantém os campos da tabela transacao.
                resposta = (
                    supabase.table("transacao")
                    .insert(dados_venda)
                    .execute()
                )

                if not resposta.data:
                    st.error(
                        "O banco não confirmou o cadastro da venda. "
                        "Verifique os dados antes de tentar novamente."
                    )
                else:
                    try:
                        # Mantém a regra atual: veículo vendido após a venda.
                        supabase.table("veiculo").update(
                            {"status_veiculo": "Vendido"}
                        ).eq(
                            "placa", veiculo_selecionado["placa"]
                        ).execute()

                        st.success("Venda registrada com sucesso!")
                        st.rerun()

                    except Exception as erro_atualizacao:
                        logger.exception(
                            "Venda registrada, mas houve erro ao atualizar "
                            "o veículo: %s",
                            erro_atualizacao,
                        )
                        st.warning(
                            "A venda foi registrada, mas não foi possível "
                            "atualizar o status do veículo. Confira o cadastro "
                            "antes de realizar outra tentativa."
                        )

            except Exception as erro:
                mostrar_erro("registrar a venda", erro)


# =========================================================
# ABA 3 — LANÇAR PAGAMENTO
# =========================================================

with aba_pagamento:
    st.subheader("Lançar pagamento")
    st.caption("Registre os dados do pagamento de uma venda existente.")

    transacoes_pagamento = obter_dados(
        "transacao",
        "id_transacao, placa_veiculo, valor_final_negociado",
    )

    if not transacoes_pagamento:
        st.info("Registre uma venda antes de lançar um pagamento.")

    else:
        modalidades = [
            "PIX",
            "Financiamento",
            "Cart?o de Credito",
            "Transfer?ncia",
            "Dinheiro",
            "Cons?rcio",
        ]

        with st.form("form_lancar_pagamento", clear_on_submit=True):
            transacao_selecionada = st.selectbox(
                "Venda relacionada",
                options=transacoes_pagamento,
                format_func=nome_transacao,
            )

            modalidade = st.selectbox(
                "Modalidade de pagamento",
                options=modalidades,
            )

            col1, col2 = st.columns(2)

            with col1:
                valor_pagamento = st.number_input(
                    "Valor da transação (R$)",
                    min_value=0.0,
                    step=500.0,
                    format="%.2f",
                )

                numero_parcelas = st.number_input(
                    "Número de parcelas",
                    min_value=1,
                    step=1,
                    value=1,
                )

            with col2:
                instituicao = st.text_input(
                    "Instituição processadora",
                    placeholder="Ex.: nome do banco ou operadora",
                )

                taxa_juros = st.number_input(
                    "Taxa de juros",
                    min_value=0.0,
                    step=0.5,
                    format="%.2f",
                    help="Informe a taxa no formato numérico utilizado pelo sistema.",
                )

            confirmar_pagamento = st.form_submit_button(
                "Registrar pagamento",
                type="primary",
                width="stretch",
            )

        if confirmar_pagamento:
            dados_pagamento = {
                "id_transacao": transacao_selecionada["id_transacao"],
                "modalidade_pagamento": modalidade,
                "valor_transacao": valor_pagamento,
                "numero_parcelas": int(numero_parcelas),
                "instituicao_processadora": instituicao.strip(),
                "taxa_juros": taxa_juros,
            }

            try:
                resposta = (
                    supabase.table("pagamento")
                    .insert(dados_pagamento)
                    .execute()
                )

                if resposta.data:
                    st.success("Pagamento registrado com sucesso!")
                    st.rerun()
                else:
                    st.warning(
                        "O banco não retornou a confirmação do pagamento. "
                        "Verifique os registros antes de tentar novamente."
                    )

            except Exception as erro:
                mostrar_erro("registrar o pagamento", erro)
