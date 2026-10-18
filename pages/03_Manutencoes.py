import streamlit as st
import pandas as pd
from database import supabase
import datetime

st.set_page_config(page_title="Oficina e Manutenções", page_icon="🔧", layout="wide")
st.title("Oficina e Registro de Manutenções")

if not supabase:
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

aba_historico, aba_nova_manutencao = st.tabs(["Histórico de Serviços", "Registrar Nova Manutenção"])

# ==========================================
# ABA 1: HISTÓRICO (READ)
# ==========================================
with aba_historico:
    st.subheader("Serviços Realizados")
    try:
        res_manutencao = supabase.table("manutencao").select("*").order('data', desc=True).execute()
        df_manutencao = pd.DataFrame(res_manutencao.data)
        
        if not df_manutencao.empty:
            # Filtro simples por placa
            filtro_placa = st.text_input("Filtrar Histórico por Placa").upper()
            if filtro_placa:
                df_manutencao = df_manutencao[df_manutencao["placa_veiculo"].str.contains(filtro_placa)]
                
            st.dataframe(df_manutencao, use_container_width=True, hide_index=True)
            
            custo_total = df_manutencao["custo_total"].sum()
            st.write(f"**Custo Acumulado dos Serviços Exibidos:** R$ {formatar_moeda(custo_total)}")
        else:
            st.info("Nenhuma manutenção registrada até o momento.")
    except Exception as e:
        st.error(f"Erro ao carregar o histórico da oficina: {e}")

# ==========================================
# ABA 2: CRIAR MANUTENÇÃO (CREATE)
# ==========================================
with aba_nova_manutencao:
    st.subheader("Ordem de Serviço (OS)")
    try:
        # Busca veículos da frota (exceto os que já foram vendidos)
        res_frota = supabase.table("veiculo").select("placa, modelo").neq("status_veiculo", "Vendido").execute()
        frota_lista = [f"{v['placa']} - {v['modelo']}" for v in res_frota.data]
        
        with st.form("form_manutencao", clear_on_submit=True):
            veiculo_os = st.selectbox("Selecionar Veículo", frota_lista)
            data_servico = st.date_input("Data do Serviço", datetime.date.today())
            
            descricao = st.text_area("Descrição do Serviço Realizado", max_chars=300)
            custo = st.number_input("Custo Total (R$)", min_value=0.0, step=50.0)
            
            submit_os = st.form_submit_button("Salvar Ordem de Serviço", type="primary")
            
            if submit_os:
                if not veiculo_os or not descricao or custo <= 0:
                    st.warning("Preencha a Placa, a Descrição e um Custo maior que zero.")
                else:
                    placa = veiculo_os.split(" - ")[0]
                    
                    nova_os = {
                        "placa_veiculo": placa,
                        "descricao_servico": descricao,
                        "data": str(data_servico),
                        "custo_total": custo
                    }
                    
                    # Insere a manutenção no banco
                    supabase.table("manutencao").insert(nova_os).execute()
                    
                    # Altera o status do veículo para Em Preparação (caso estivesse Disponível)
                    supabase.table("veiculo").update({"status_veiculo": "Em preparacao"}).eq("placa", placa).execute()
                    
                    st.success(f"Serviço registrado com sucesso para o veículo {placa}!")
                    
    except Exception as e:
        st.error(f"Erro ao registrar a manutenção: {e}")