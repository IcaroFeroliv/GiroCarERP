import streamlit as st
import pandas as pd
from database import supabase

st.set_page_config(page_title="Administração", page_icon="🏢", layout="wide")
st.title("🏢 Administração (RH e Filiais)")

if not supabase:
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

aba_lojas, aba_funcionarios = st.tabs(["🏪 Lojas (Filiais)", "🧑‍💼 Funcionários"])

# ==========================================
# ABA 1: LOJAS
# ==========================================
with aba_lojas:
    st.subheader("Cadastro de Loja")

    
    with st.form("form_loja", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cnpj_loja = st.text_input("CNPJ da Loja", max_chars=18)
            nome_loja = st.text_input("Nome da Unidade")
        with col2:
            endereco_loja = st.text_input("Endereço Completo")
            
        submit_loja = st.form_submit_button("Salvar Loja", type="primary")
        
        if submit_loja:
            if not cnpj_loja or not nome_loja:
                st.warning("Preencha os campos obrigatórios (CNPJ e Nome).")
            else:
                try:
                    nova_loja = {
                        "cnpj": cnpj_loja,
                        "nome_unidade": nome_loja,
                        "endereco": endereco_loja
                    }
                    supabase.table("loja").insert(nova_loja).execute()
                    st.success("Loja cadastrada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar loja: {e}")

    st.divider()
    st.subheader("Lista de Lojas")
    try:
        res_loja = supabase.table("loja").select("*").execute()
        df_loja = pd.DataFrame(res_loja.data)
        if not df_loja.empty:
            st.dataframe(df_loja, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma loja cadastrada.")
    except Exception as e:
        st.error(f"Erro ao carregar lojas: {e}")

# ==========================================
# ABA 2: FUNCIONÁRIOS
# ==========================================
with aba_funcionarios:
    st.subheader("Cadastro de Funcionário")
    
    with st.form("form_funcionario", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            matricula = st.text_input("Matrícula", max_chars=50)
            nome_func = st.text_input("Nome Completo")
        with col2:
            cargo = st.selectbox("Cargo / Nível de Acesso", ["Vendedor", "Gerente"])
            cnpj_vinculo = st.text_input("CNPJ da Loja (Vínculo)")
        with col3:
            # st.date_input retorna um objeto Data. Precisamos converter para string (YYYY-MM-DD) pro banco
            data_admissao = st.date_input("Data de Admissão")
            
        submit_func = st.form_submit_button("Salvar Funcionário", type="primary")
        
        if submit_func:
            if not matricula or not nome_func or not cnpj_vinculo:
                st.warning("Preencha Matrícula, Nome e o CNPJ da Loja vinculada.")
            else:
                try:
                    novo_func = {
                        "matricula": matricula,
                        "nome": nome_func,
                        "cargo_nivel_acesso": cargo,
                        "cnpj_loja": cnpj_vinculo,
                        "data_admissao": str(data_admissao) 
                    }
                    supabase.table("funcionario").insert(novo_func).execute()
                    st.success("Funcionário cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar funcionário (verifique se o CNPJ da loja existe): {e}")

    st.divider()
    st.subheader("Quadro de Funcionários")
    try:
        res_func = supabase.table("funcionario").select("*").execute()
        df_func = pd.DataFrame(res_func.data)
        if not df_func.empty:
            st.dataframe(df_func, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum funcionário cadastrado.")
    except Exception as e:
        st.error(f"Erro ao carregar funcionários: {e}")