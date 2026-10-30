import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from database import supabase


# Base do projeto e localização da logo usada no cabeçalho da página.
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

# Configuração global da página do Streamlit para manter a identidade visual.
st.set_page_config(
    page_title="Oficina e Manutenções | GiroCar",
    page_icon=str(LOGO_PATH),
    layout="wide",
)
# Cabeçalho com a identidade visual da GiroCar.
# Aqui a marca e o título da área de oficina são exibidos para manter a
# consistência visual com as demais páginas do sistema.
col_logo, col_titulo = st.columns([1, 5], vertical_alignment="center")

with col_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=180)

with col_titulo:
    st.title("Oficina e Manutenções")
    st.caption("Controle de ordens de serviço, histórico e custos da frota.")

if not supabase:
    st.error("Não foi possível conectar ao banco de dados.")
    st.stop()

# Função auxiliar para padronizar a exibição de valores monetários no formato
# brasileiro, facilitando a leitura dos custos de manutenção.
def formatar_moeda(valor):
    valor = float(valor or 0)
    numero = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {numero}"


# A página é dividida em duas abas principais: uma para consultar o histórico
# de serviços já registrados e outra para incluir novas ordens de serviço.
aba_historico, aba_nova = st.tabs(
    [" Histórico de serviços", " Registrar manutenção"]
)


# Aba de consulta do histórico de manutenção, com filtros por placa e período.
with aba_historico:
    st.subheader("Histórico de manutenções")

    try:
        resposta = (
            supabase.table("manutencao")
            .select("*")
            .order("data", desc=True)
            .execute()
        )

        df = pd.DataFrame(resposta.data)

        if df.empty:
            st.info("Nenhuma manutenção foi registrada até o momento.")
        else:
            if "custo_total" not in df.columns:
                st.error("A coluna custo_total não foi retornada pelo banco.")
                st.stop()

            df["custo_total"] = pd.to_numeric(
                df["custo_total"], errors="coerce"
            ).fillna(0)

            if "data" in df.columns:
                df["_data_filtro"] = pd.to_datetime(
                    df["data"], errors="coerce"
                ).dt.date
            else:
                df["_data_filtro"] = pd.NaT

            col1, col2, col3 = st.columns(3)
            col1.metric("Serviços registrados", len(df))
            col2.metric("Custo total", formatar_moeda(df["custo_total"].sum()))
            col3.metric(
                "Custo médio por serviço",
                formatar_moeda(df["custo_total"].mean()),
            )

            st.divider()
            st.markdown("#### Filtrar histórico")

            filtro1, filtro2, filtro3 = st.columns([1, 1, 1])

            with filtro1:
                placa = st.text_input(
                    "Placa do veículo",
                    placeholder="Ex.: ABC1D23",
                ).strip().upper()

            datas_validas = df["_data_filtro"].dropna()

            if not datas_validas.empty:
                data_min = min(datas_validas)
                data_max = max(datas_validas)
            else:
                data_min = datetime.date.today()
                data_max = datetime.date.today()

            with filtro2:
                data_inicial = st.date_input(
                    "Data inicial",
                    value=data_min,
                    key="manut_data_inicial",
                    format="DD/MM/YYYY",
                )

            with filtro3:
                data_final = st.date_input(
                    "Data final",
                    value=data_max,
                    key="manut_data_final",
                    format="DD/MM/YYYY",
                )

            filtrado = df.copy()

            if placa and "placa_veiculo" in filtrado.columns:
                filtrado = filtrado[
                    filtrado["placa_veiculo"]
                    .fillna("")
                    .astype(str)
                    .str.upper()
                    .str.contains(placa, regex=False)
                ]

            if data_inicial > data_final:
                st.warning(
                    "A data inicial não pode ser posterior à data final."
                )
            else:
                filtrado = filtrado[
                    filtrado["_data_filtro"].isna()
                    | (
                        (filtrado["_data_filtro"] >= data_inicial)
                        & (filtrado["_data_filtro"] <= data_final)
                    )
                ]

            st.caption(f"{len(filtrado)} registro(s) encontrado(s).")

            colunas = [
                coluna
                for coluna in [
                    "placa_veiculo",
                    "descricao_servico",
                    "data",
                    "custo_total",
                ]
                if coluna in filtrado.columns
            ]

            exibicao = filtrado[colunas].copy()

            if "data" in exibicao.columns:
                exibicao["data"] = (
                    pd.to_datetime(exibicao["data"], errors="coerce")
                    .dt.strftime("%d/%m/%Y")
                    .fillna("—")
                )

            if "custo_total" in exibicao.columns:
                exibicao["custo_total"] = exibicao["custo_total"].map(
                    formatar_moeda
                )

            exibicao = exibicao.rename(
                columns={
                    "placa_veiculo": "Placa",
                    "descricao_servico": "Descrição do serviço",
                    "data": "Data",
                    "custo_total": "Custo total",
                }
            )

            if exibicao.empty:
                st.info("Nenhum registro corresponde aos filtros selecionados.")
            else:
                st.dataframe(
                    exibicao,
                    width="stretch",
                    hide_index=True,
                )

            st.metric(
                "Custo dos serviços exibidos",
                formatar_moeda(filtrado["custo_total"].sum()),
            )

    except Exception as erro:
        st.error(f"Não foi possível carregar o histórico: {erro}")


# Aba para registrar uma nova ordem de serviço, incluindo veículo, data,
# descrição do serviço e custo total. Ao salvar, o status do veículo é
# atualizado para "Em preparacao".
with aba_nova:
    st.subheader("Nova ordem de serviço")
    st.write("Preencha os dados do veículo e do serviço realizado.")

    try:
        resposta_frota = (
            supabase.table("veiculo")
            .select("placa, modelo")
            .neq("status_veiculo", "Vendido")
            .execute()
        )

        frota = resposta_frota.data or []

        if not frota:
            st.warning(
                "Não há veículos disponíveis para registrar uma manutenção."
            )
        else:
            opcoes = {
                f"{v['placa']} - {v.get('modelo') or 'Modelo não informado'}": v["placa"]
                for v in frota
                if v.get("placa")
            }

            if not opcoes:
                st.warning("Não foi possível identificar as placas dos veículos.")
            else:
                with st.form("form_manutencao", clear_on_submit=True):
                    veiculo = st.selectbox(
                        "Veículo",
                        options=list(opcoes.keys()),
                    )

                    data_servico = st.date_input(
                        "Data do serviço",
                        value=datetime.date.today(),
                        max_value=datetime.date.today(),
                        format="DD/MM/YYYY",
                    )

                    descricao = st.text_area(
                        "Descrição do serviço realizado",
                        placeholder="Informe os serviços executados...",
                        max_chars=300,
                    )

                    custo = st.number_input(
                        "Custo total (R$)",
                        min_value=0.0,
                        step=50.0,
                        format="%.2f",
                    )

                    salvar = st.form_submit_button(
                        "Salvar ordem de serviço",
                        type="primary",
                        width="stretch",
                    )

                if salvar:
                    if not descricao.strip():
                        st.warning("Informe a descrição do serviço.")
                    elif custo <= 0:
                        st.warning("O custo total deve ser maior que zero.")
                    else:
                        placa_selecionada = opcoes[veiculo]

                        nova_os = {
                            "placa_veiculo": placa_selecionada,
                            "descricao_servico": descricao.strip(),
                            "data": str(data_servico),
                            "custo_total": custo,
                        }

                        try:
                            (
                                supabase.table("manutencao")
                                .insert(nova_os)
                                .execute()
                            )

                            (
                                supabase.table("veiculo")
                                .update({"status_veiculo": "Em preparacao"})
                                .eq("placa", placa_selecionada)
                                .execute()
                            )

                            st.success(
                                f"Manutenção registrada para {placa_selecionada}."
                            )
                            st.rerun()

                        except Exception as erro:
                            st.error(
                                f"Não foi possível concluir a operação: {erro}"
                            )

    except Exception as erro:
        st.error(f"Não foi possível carregar os veículos: {erro}")
