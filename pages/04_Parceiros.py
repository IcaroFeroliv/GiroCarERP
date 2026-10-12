import streamlit as st
import pandas as pd
from database import supabase

st.set_page_config(page_title="Parceiros Comerciais", page_icon="🤝", layout="wide")
st.title("🤝 Gestão de Parceiros Comerciais")

if not supabase:
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

# Abas para separar Clientes e Fornecedores
aba_clientes, aba_fornecedores = st.tabs(["🎯 Clientes (CRM)", "🏭 Fornecedores"])

# ==========================================
# ABA 1: CLIENTES
# ==========================================
with aba_clientes:
    st.subheader("Cadastro de Clientes")
    
    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cpf_cnpj_cliente = st.text_input("CPF ou CNPJ", max_chars=18)
            nome_cliente = st.text_input("Nome Completo / Razão Social")
            telefone_cliente = st.text_input("Telefone")
        with col2:
            email_cliente = st.text_input("E-mail")
            status_funil = st.selectbox("Status no Funil de Vendas", ["Contato Inicial", "Em Negociação", "Venda Fechada"])
            
        submit_cliente = st.form_submit_button("Salvar Cliente", type="primary")
        
        if submit_cliente:
            if not cpf_cnpj_cliente or not nome_cliente:
                st.warning("Preencha os campos obrigatórios (CPF/CNPJ e Nome).")
            else:
                try:
                    novo_cliente = {
                        "cpf_cnpj": cpf_cnpj_cliente,
                        "nome_completo": nome_cliente,
                        "telefone": telefone_cliente,
                        "email": email_cliente,
                        "status_funil_vendas": status_funil
                    }
                    supabase.table("cliente").insert(novo_cliente).execute()
                    st.success("Cliente cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar cliente (verifique se o CPF já existe): {e}")

    st.divider()
    st.subheader("Lista de Clientes")
    try:
        res_cli = supabase.table("cliente").select("*").execute()
        df_cli = pd.DataFrame(res_cli.data)
        if not df_cli.empty:
            st.dataframe(df_cli, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum cliente cadastrado.")
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")

# ==========================================
# ABA 2: FORNECEDORES
# ==========================================
with aba_fornecedores:
    st.subheader("Cadastro de Fornecedores")
    
    with st.form("form_fornecedor", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cnpj_cpf_forn = st.text_input("CNPJ ou CPF do Fornecedor", max_chars=18)
            nome_forn = st.text_input("Nome / Razão Social")
        with col2:
            telefone_forn = st.text_input("Telefone de Contato")
            tipo_origem = st.selectbox("Tipo de Origem", ["Repasse", "Leilão", "Particular"])
            
        submit_forn = st.form_submit_button("Salvar Fornecedor", type="primary")
        
        if submit_forn:
            if not cnpj_cpf_forn or not nome_forn:
                st.warning("Preencha os campos obrigatórios (CNPJ/CPF e Nome).")
            else:
                try:
                    novo_forn = {
                        "cnpj_cpf": cnpj_cpf_forn,
                        "nome_razao_social": nome_forn,
                        "telefone": telefone_forn,
                        "tipo_origem": tipo_origem
                    }
                    supabase.table("fornecedor").insert(novo_forn).execute()
                    st.success("Fornecedor cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar fornecedor: {e}")

    st.divider()
    st.subheader("Lista de Fornecedores")
    try:
        res_forn = supabase.table("fornecedor").select("*").execute()
        df_forn = pd.DataFrame(res_forn.data)
        if not df_forn.empty:
            st.dataframe(df_forn, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum fornecedor cadastrado.")
    except Exception as e:
        st.error(f"Erro ao carregar fornecedores: {e}")