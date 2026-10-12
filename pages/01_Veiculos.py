import streamlit as st
import pandas as pd
from database import supabase

# Apenas o ícone da aba no navegador foi mantido
st.set_page_config(page_title="Gestão de Veículos", page_icon="🚙", layout="wide")
st.title("Gestão de Frota e Veículos")

if not supabase:
    st.error("Erro de conexão com o banco.")
    st.stop()

# Abas sem emojis
aba_consulta, aba_cadastro = st.tabs(["Consultar e Gerenciar", "Cadastrar Veículo"])

# ==========================================
# ABA 1: READ, UPDATE e DELETE (Consulta)
# ==========================================
with aba_consulta:
    st.subheader("Veículos no Sistema")
    try:
        res = supabase.table("veiculo").select("*").execute()
        df = pd.DataFrame(res.data)
        
        if not df.empty:
            
            # --- NOVA SEÇÃO DE FILTROS ---
            with st.expander("Filtros de Busca", expanded=False):
                col_f1, col_f2, col_f3 = st.columns(3)
                
                with col_f1:
                    filtro_placa = st.text_input("Buscar por Placa").upper()
                with col_f2:
                    filtro_status = st.multiselect("Filtrar por Status", options=df["status_veiculo"].unique())
                with col_f3:
                    filtro_marca = st.multiselect("Filtrar por Marca", options=df["marca"].unique())
            
            # --- APLICANDO OS FILTROS NO DATAFRAME ---
            df_filtrado = df.copy()
            
            if filtro_placa:
                df_filtrado = df_filtrado[df_filtrado["placa"].str.contains(filtro_placa)]
            if filtro_status:
                df_filtrado = df_filtrado[df_filtrado["status_veiculo"].isin(filtro_status)]
            if filtro_marca:
                df_filtrado = df_filtrado[df_filtrado["marca"].isin(filtro_marca)]
            
            # Exibe a tabela filtrada
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # --- AÇÕES RÁPIDAS COM BASE NO FILTRO ---
            if not df_filtrado.empty:
                st.subheader("Ações Rápidas")
                col1, col2 = st.columns(2)
                
                # UPDATE
                with col1:
                    st.write("**Atualizar Status do Veículo**")
                    placa_edit = st.selectbox("Selecione a Placa", df_filtrado["placa"], key="edit_placa")
                    # Ajustado para refletir os status do seu banco de dados
                    novo_status = st.selectbox("Novo Status", ["Disponivel", "Em preparacao", "Vendido", "Reservado"])
                    
                    if st.button("Atualizar Status", use_container_width=True):
                        supabase.table("veiculo").update({"status_veiculo": novo_status}).eq("placa", placa_edit).execute()
                        st.success(f"Status da placa {placa_edit} atualizado para {novo_status}!")
                        st.rerun()
                
                # DELETE
                with col2:
                    st.write("**Excluir Registro**")
                    placa_del = st.selectbox("Selecione a Placa", df_filtrado["placa"], key="del_placa")
                    
                    if st.button("Excluir Veículo", type="primary", use_container_width=True):
                        try:
                            supabase.table("veiculo").delete().eq("placa", placa_del).execute()
                            st.success(f"Veículo {placa_del} excluído com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error("Não é possível excluir este veículo pois ele já possui vínculo com Manutenções ou Histórico.")
            else:
                st.warning("Nenhum veículo encontrado com os filtros aplicados.")
                
        else:
            st.info("Nenhum veículo cadastrado no sistema.")
            
    except Exception as e:
        st.error(f"Erro ao carregar base de veículos: {e}")

# ==========================================
# ABA 2: CREATE (Cadastro)
# ==========================================
with aba_cadastro:
    st.subheader("Formulário de Entrada de Veículo")
    
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
            status = st.selectbox("Status Inicial", ["Disponivel", "Em preparacao"])
            
        with col3:
            st.write("Indicadores de Risco (RN04)")
            leilao = st.checkbox("Passagem por Leilão?")
            sinistro = st.checkbox("Indicador de Sinistro?")
            st.write("Vínculos")
            cnpj_loja = st.text_input("CNPJ da Loja (Destino)")
            cnpj_forn = st.text_input("CNPJ/CPF do Fornecedor (Origem)")
        
        submit = st.form_submit_button("Salvar Registro de Veículo", type="primary")
        
        if submit:
            if not placa or not chassi or not cnpj_loja or not cnpj_forn:
                st.warning("Preencha todos os campos obrigatórios (Placa, Chassi e CNPJs)!")
            else:
                try:
                    novo_veiculo = {
                        "placa": placa,
                        "chassi": chassi,
                        "marca": marca,
                        "modelo": modelo,
                        "ano_fabricacao": ano_fab,
                        "ano_modelo": ano_mod,
                        "cor": cor,
                        "quilometragem": km,
                        "valor_aquisicao": valor,
                        "indicador_leilao": leilao,
                        "indicador_sinistro": sinistro,
                        "status_veiculo": status,
                        "cnpj_loja": cnpj_loja,
                        "cnpj_cpf_fornecedor": cnpj_forn
                    }
                    supabase.table("veiculo").insert(novo_veiculo).execute()
                    st.success(f"O veículo {marca} {modelo} ({placa}) foi salvo com sucesso!")
                except Exception as e:
                    st.error("Erro ao salvar! Verifique se a Placa/Chassi já existem e se a Loja/Fornecedor estão cadastrados.")
                    st.error(f"Detalhe: {e}")