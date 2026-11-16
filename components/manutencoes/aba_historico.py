import streamlit as st
import pandas as pd
import datetime
from database import supabase
from components.regras_negocio.formatar_reais import formatar_reais
from components.regras_negocio.tratamento_erros import mostrar_erro
from components.regras_negocio.filtros_data import filtrar_por_periodo
from components.manutencoes.kpis_manutencao import render_kpis_manutencao

def render_aba_historico():
    st.subheader("Histórico de manutenções")

    try:
        resposta = supabase.table("manutencao").select("*").order("data", desc=True).execute()
        df = pd.DataFrame(resposta.data)

        if df.empty:
            st.info("Nenhuma manutenção foi registrada até o momento.")
            return
            
        if "custo_total" not in df.columns:
            st.error("A coluna custo_total não foi retornada pelo banco.")
            return

        df["custo_total"] = pd.to_numeric(df["custo_total"], errors="coerce").fillna(0)

        if "data" in df.columns:
            df["_data_filtro"] = pd.to_datetime(df["data"], errors="coerce").dt.date
        else:
            df["_data_filtro"] = pd.NaT

        render_kpis_manutencao(df)

        st.divider()
        st.markdown("#### Filtrar histórico")

        filtro1, filtro2, filtro3 = st.columns([1, 1, 1])

        with filtro1:
            placa = st.text_input("Placa do veículo", placeholder="Ex.: ABC1D23").strip().upper()

        datas_validas = df["_data_filtro"].dropna()
        data_min = min(datas_validas) if not datas_validas.empty else datetime.date.today()
        data_max = max(datas_validas) if not datas_validas.empty else datetime.date.today()

        with filtro2:
            data_inicial = st.date_input("Data inicial", value=data_min, key="manut_data_inicial", format="DD/MM/YYYY")

        with filtro3:
            data_final = st.date_input("Data final", value=data_max, key="manut_data_final", format="DD/MM/YYYY")

        filtrado = df.copy()

        if placa and "placa_veiculo" in filtrado.columns:
            filtrado = filtrado[filtrado["placa_veiculo"].fillna("").astype(str).str.upper().str.contains(placa, regex=False)]

        if data_inicial > data_final:
            st.warning("A data inicial não pode ser posterior à data final.")
        else:
            filtrado = filtrar_por_periodo(filtrado, "_data_filtro", data_inicial, data_final)

        st.caption(f"{len(filtrado)} registro(s) encontrado(s).")

        colunas = [c for c in ["placa_veiculo", "descricao_servico", "data", "custo_total"] if c in filtrado.columns]
        exibicao = filtrado[colunas].copy()

        if "data" in exibicao.columns:
            exibicao["data"] = pd.to_datetime(exibicao["data"], errors="coerce").dt.strftime("%d/%m/%Y").fillna("—")

        if "custo_total" in exibicao.columns:
            exibicao["custo_total"] = exibicao["custo_total"].map(lambda x: formatar_reais(x) or "R$ 0,00")

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
            st.dataframe(exibicao, width="stretch", hide_index=True)
            st.metric("Custo dos serviços exibidos", formatar_reais(filtrado["custo_total"].sum()) or "R$ 0,00")

    except Exception as erro:
        mostrar_erro("carregar o histórico", erro)  