import streamlit as st
import pandas as pd
from database import supabase
import datetime

st.set_page_config(page_title="Comercial e Vendas", page_icon="💰", layout="wide")
st.title("Comercial e Gestão de Vendas")

if not supabase:
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

aba_vendas, aba_nova_venda, aba_pagamentos = st.tabs(["Histórico de Vendas", "Registrar Nova Venda", "Lançar Pagamento"])

# ==========================================
# ABA 1: HISTÓRICO DE VENDAS
# ==========================================
with aba_vendas:
    st.subheader("Transações Realizadas")
    try:
        res_transacoes = supabase.table("transacao").select("*").execute()
        df_transacoes = pd.DataFrame(res_transacoes.data)
        
        if not df_transacoes.empty:
            st.dataframe(df_transacoes, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma transação registrada até o momento.")
    except Exception as e:
        st.error(f"Erro ao carregar transações: {e}")

# ==========================================
# ABA 2: REGISTRAR NOVA VENDA
# ==========================================
with aba_nova_venda:
    st.subheader("Formulário de Transação")
    try:
        # RN01: Busca apenas veículos disponíveis para venda
        res_veiculos = supabase.table("veiculo").select("placa, modelo").eq("status_veiculo", "Disponivel").execute()
        veiculos_disp = [f"{v['placa']} - {v['modelo']}" for v in res_veiculos.data]
        
        res_clientes = supabase.table("cliente").select("cpf_cnpj, nome_completo").execute()
        clientes_lista = [f"{c['cpf_cnpj']} - {c['nome_completo']}" for c in res_clientes.data]
        
        res_funcs = supabase.table("funcionario").select("matricula, nome").execute()
        funcs_lista = [f"{f['matricula']} - {f['nome']}" for f in res_funcs.data]
        
        with st.form("form_nova_venda", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                veiculo_selecionado = st.selectbox("Veículo (Apenas Disponíveis)", veiculos_disp)
                cliente_selecionado = st.selectbox("Cliente", clientes_lista)
            with col2:
                vendedor_selecionado = st.selectbox("Vendedor Responsável", funcs_lista)
                data_venda = st.date_input("Data da Transação", datetime.date.today())
                valor_negociado = st.number_input("Valor Final Negociado (R$)", min_value=0.0, step=1000.0)
            
            submit_venda = st.form_submit_button("Registrar Venda", type="primary")
            
            if submit_venda:
                if not veiculo_selecionado or not cliente_selecionado or not vendedor_selecionado:
                    st.warning("Selecione todos os campos obrigatórios (Veículo, Cliente e Vendedor).")
                else:
                    placa = veiculo_selecionado.split(" - ")[0]
                    cpf_cliente = cliente_selecionado.split(" - ")[0]
                    matricula = vendedor_selecionado.split(" - ")[0]
                    
                    nova_transacao = {
                        "data": str(data_venda),
                        "placa_veiculo": placa,
                        "cpf_cnpj_cliente": cpf_cliente,
                        "matricula_funcionario": matricula,
                        "valor_final_negociado": valor_negociado
                    }
                    
                    # Insere a transação
                    supabase.table("transacao").insert(nova_transacao).execute()
                    
                    # Atualiza o status do veículo para Vendido
                    supabase.table("veiculo").update({"status_veiculo": "Vendido"}).eq("placa", placa).execute()
                    
                    st.success(f"Venda do veículo {placa} registrada com sucesso no valor de R$ {formatar_moeda(valor_negociado)}!")
                    st.info("Acesse a aba 'Lançar Pagamento' para registrar a forma de recebimento.")
                    
    except Exception as e:
        st.error(f"Erro ao processar dados da venda: {e}")

# ==========================================
# ABA 3: LANÇAR PAGAMENTOS (RN06)
# ==========================================
with aba_pagamentos:
    st.subheader("Registrar Parcela / Pagamento")
    try:
        # Carrega transações para vincular o pagamento
        transacoes_ativas = supabase.table("transacao").select("id_transacao, placa_veiculo, valor_final_negociado").execute()
        lista_transacoes = [f"ID: {t['id_transacao']} | Placa: {t['placa_veiculo']} | Valor: R$ {formatar_moeda(t['valor_final_negociado'])}" for t in transacoes_ativas.data]
        
        with st.form("form_pagamento", clear_on_submit=True):
            transacao_selecionada = st.selectbox("Venda de Referência", lista_transacoes)
            
            col1, col2 = st.columns(2)
            with col1:
                modalidade = st.selectbox("Modalidade de Pagamento", ["PIX", "Financiamento", "Cartao de Credito", "Transferencia", "Dinheiro", "Consorcio"])
                instituicao = st.text_input("Instituição Processadora (Banco)")
            with col2:
                valor_pagamento = st.number_input("Valor da Parcela/Entrada (R$)", min_value=0.0, step=100.0)
                n_parcelas = st.number_input("Número de Parcelas", min_value=1, step=1, value=1)
                taxa = st.number_input("Taxa de Juros (%)", min_value=0.0, step=0.1, value=0.0)
                
            submit_pagamento = st.form_submit_button("Salvar Pagamento", type="primary")
            
            if submit_pagamento:
                if not transacao_selecionada or not instituicao:
                    st.warning("Preencha a Venda de Referência e a Instituição Processadora.")
                else:
                    id_t = int(transacao_selecionada.split("ID: ")[1].split(" |")[0])
                    
                    novo_pagamento = {
                        "id_transacao": id_t,
                        "modalidade_pagamento": modalidade,
                        "valor_transacao": valor_pagamento,
                        "numero_parcelas": n_parcelas,
                        "instituicao_processadora": instituicao,
                        "taxa_juros": taxa
                    }
                    
                    supabase.table("pagamento").insert(novo_pagamento).execute()
                    st.success("Pagamento vinculado à transação com sucesso!")
                    
    except Exception as e:
        st.error(f"Erro ao processar pagamentos: {e}")