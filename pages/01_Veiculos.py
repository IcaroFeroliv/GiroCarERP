import streamlit as st
import pandas as pd
from database import supabase

st.set_page_config(page_title="Gestão de Veículos", page_icon="🚙", layout="wide")
st.title("🚙 Gestão de Frota e Veículos")

if not supabase:
    st.error("Erro de conexão com o banco.")
    st.stop()

# Organização limpa da interface em Abas
aba_consulta, aba_cadastro = st.tabs(["📋 Consultar e Gerenciar", "➕ Cadastrar Veículo"])

# ==========================================
# ABA 1: READ, UPDATE e DELETE (Consulta)
# ==========================================
with aba_consulta:
    st.subheader("Veículos no Sistema")
    try:
        # READ: Busca todos os veículos
        res = supabase.table("veiculo").select("*").execute()
        df = pd.DataFrame(res.data)
        
        if not df.empty:
            # Exibe a tabela na tela
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("⚙️ Ações Rápidas")
            col1, col2 = st.columns(2)
            
            # UPDATE: Atualizar Status
            with col1:
                st.write("**Atualizar Status do Veículo**")
                placa_edit = st.selectbox("Selecione a Placa", df["Placa"], key="edit_placa")
                novo_status = st.selectbox("Novo Status", ["Estoque", "Em Preparação", "Reservado", "Vendido"])
                
                if st.button("Atualizar Status", use_container_width=True):
                    supabase.table("veiculo").update({"Status_Veiculo": novo_status}).eq("Placa", placa_edit).execute()
                    st.success(f"Status da placa {placa_edit} atualizado para {novo_status}!")
                    st.rerun() # Recarrega a página para atualizar a tabela
            
            # DELETE: Excluir Veículo
            with col2:
                st.write("**Excluir Registro**")
                placa_del = st.selectbox("Selecione a Placa", df["Placa"], key="del_placa")
                
                if st.button("Excluir Veículo", type="primary", use_container_width=True):
                    # O bloco Try captura o erro ON DELETE RESTRICT (RN05) do banco
                    try:
                        supabase.table("veiculo").delete().eq("Placa", placa_del).execute()
                        st.success(f"Veículo {placa_del} excluído com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error("Não é possível excluir este veículo pois ele já possui vínculo com Manutenções ou Histórico.")
        else:
            st.info("Nenhum veículo cadastrado no momento.")
            
    except Exception as e:
        st.error(f"Erro ao carregar base de veículos: {e}")

# ==========================================
# ABA 2: CREATE (Cadastro)
# ==========================================
with aba_cadastro:
    st.subheader("Formulário de Entrada de Veículo")
    
    # st.form cria um formulário que só é enviado ao clicar no botão final
    with st.form("form_cadastro_veiculo", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            placa = st.text_input("Placa", max_chars=10).upper()
            chassi = st.text_input("Chassi", max_chars=17).upper()
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            cor = st.text_input("Cor")
            
        with col2:
            ano_fab = st.number_input("Ano Fabricação", min_value=1900, max_value=2100, step=1, value=2024)
            ano_mod = st.number_input("Ano Modelo", min_value=1900, max_value=2100, step=1, value=2024)
            km = st.number_input("Quilometragem (KM)", min_value=0.0, step=100.0)
            valor = st.number_input("Valor de Aquisição (R$)", min_value=0.0, step=1000.0)
            status = st.selectbox("Status Inicial", ["Estoque", "Em Preparação"])
            
        with col3:
            st.write("Indicadores de Risco (RN04)")
            leilao = st.checkbox("Passagem por Leilão?")
            sinistro = st.checkbox("Indicador de Sinistro?")
            st.write("Vínculos")
            # Obs: Para o CRUD funcionar, as Lojas e Fornecedores já devem existir no banco
            cnpj_loja = st.text_input("CNPJ da Loja (Destino)")
            cnpj_forn = st.text_input("CNPJ/CPF do Fornecedor (Origem)")
        
        submit = st.form_submit_button("Salvar Registro de Veículo", type="primary")
        
        if submit:
            if not placa or not chassi or not cnpj_loja or not cnpj_forn:
                st.warning("Preencha todos os campos obrigatórios (Placa, Chassi e CNPJs)!")
            else:
                try:
                    # Monta o dicionário com os nomes idênticos às colunas do SQL
                    novo_veiculo = {
                        "Placa": placa,
                        "Chassi": chassi,
                        "Marca": marca,
                        "Modelo": modelo,
                        "Ano_Fabricacao": ano_fab,
                        "Ano_Modelo": ano_mod,
                        "Cor": cor,
                        "Quilometragem": km,
                        "Valor_Aquisicao": valor,
                        "Indicador_Leilao": leilao,
                        "Indicador_Sinistro": sinistro,
                        "Status_Veiculo": status,
                        "CNPJ_Loja": cnpj_loja,
                        "CNPJ_CPF_Fornecedor": cnpj_forn
                    }
                    # Executa a inserção no Supabase
                    supabase.table("veiculo").insert(novo_veiculo).execute()
                    st.success(f"O veículo {marca} {modelo} ({placa}) foi salvo com sucesso!")
                    
                except Exception as e:
                    st.error("Erro ao salvar! Verifique se a Placa/Chassi já existem e se a Loja/Fornecedor já foram cadastrados no sistema.")
                    st.error(f"Detalhe do Banco de Dados: {e}")