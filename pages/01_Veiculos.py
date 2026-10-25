import streamlit as st
import pandas as pd
import requests
import datetime
from database import supabase

st.set_page_config(page_title="Gestão de Veículos", page_icon="🚙", layout="wide")
st.title("Gestão de Frota e Veículos")

if not supabase:
    st.error("Não foi possível estabelecer conexão com o banco de dados. Verifique sua conexão de rede ou tente novamente mais tarde.")
    st.stop()

# Adicionamos a terceira aba para a FIPE
aba_consulta, aba_cadastro, aba_fipe, aba_historico = st.tabs([ "Consultar e Gerenciar", "Cadastrar Veículo", "Consulta Tabela FIPE", "Histórico de Avaliações"
])

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
        st.error("⚠️ Não foi possível estabelecer conexão com o banco de dados. Verifique sua conexão de rede ou tente novamente mais tarde.")
        with st.expander("Detalhes Técnicos (Para Suporte)"):
            st.code(str(e))

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
                    st.error("⚠️ Não foi possível estabelecer conexão com o banco de dados. Verifique sua conexão de rede ou tente novamente mais tarde.")
                    with st.expander("Detalhes Técnicos (Para Suporte)"):
                        st.code(str(e))

# ==========================================
# ABA 3: CONSULTA FIPE (LIVRE E CASCATA)
# ==========================================
with aba_fipe:
    st.subheader("Consultar Avaliação de Veículos (Tabela FIPE)")
    st.write("Pesquise o valor de mercado de qualquer veículo para avaliação de troca ou para atualizar o estoque atual.")

    # Funções com cache (st.cache_data) para não sobrecarregar a API e deixar o app rápido
    @st.cache_data(ttl=86400)
    def get_marcas():
        try:
            req = requests.get("https://parallelum.com.br/fipe/api/v1/carros/marcas", headers={'User-Agent': 'GiroCarERP/1.0'})
            return req.json() if req.status_code == 200 else []
        except: return []

    @st.cache_data(ttl=86400)
    def get_modelos(cod_marca):
        try:
            req = requests.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{cod_marca}/modelos", headers={'User-Agent': 'GiroCarERP/1.0'})
            return req.json()['modelos'] if req.status_code == 200 else []
        except: return []

    @st.cache_data(ttl=86400)
    def get_anos(cod_marca, cod_modelo):
        try:
            req = requests.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{cod_marca}/modelos/{cod_modelo}/anos", headers={'User-Agent': 'GiroCarERP/1.0'})
            return req.json() if req.status_code == 200 else []
        except: return []

    # Layout das 3 caixas de seleção em linha
    col_f1, col_f2, col_f3 = st.columns(3)

    marcas = get_marcas()
    opcoes_marcas = {m['nome']: m['codigo'] for m in marcas} if marcas else {}

    with col_f1:
        marca_sel = st.selectbox("1. Selecione a Marca", ["-- Selecione --"] + list(opcoes_marcas.keys()))

    if marca_sel != "-- Selecione --":
        cod_marca = opcoes_marcas[marca_sel]
        modelos = get_modelos(cod_marca)
        opcoes_modelos = {m['nome']: m['codigo'] for m in modelos}

        with col_f2:
            modelo_sel = st.selectbox("2. Selecione o Modelo", ["-- Selecione --"] + list(opcoes_modelos.keys()))

        if modelo_sel != "-- Selecione --":
            cod_modelo = opcoes_modelos[modelo_sel]
            anos = get_anos(cod_marca, cod_modelo)
            opcoes_anos = {a['nome']: a['codigo'] for a in anos}

            with col_f3:
                ano_sel = st.selectbox("3. Selecione o Ano/Combustível", ["-- Selecione --"] + list(opcoes_anos.keys()))

            # Só busca o preço final quando os 3 campos estiverem preenchidos
            if ano_sel != "-- Selecione --":
                cod_ano = opcoes_anos[ano_sel]

                st.divider()
                
                try:
                    req_final = requests.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{cod_marca}/modelos/{cod_modelo}/anos/{cod_ano}", headers={'User-Agent': 'GiroCarERP/1.0'})
                    
                    if req_final.status_code == 200:
                        dados = req_final.json()
                        v_fipe = dados.get('Valor')
                        m_ref = dados.get('MesReferencia')
                        c_fipe = dados.get('CodigoFipe')

                        # Exibe a consulta livre
                        st.subheader("📊 Resultado da Avaliação Oficial")
                        col_r1, col_r2, col_r3 = st.columns(3)
                        col_r1.metric("Valor de Mercado", v_fipe)
                        col_r2.metric("Mês de Referência", m_ref)
                        col_r3.metric("Código FIPE Encontrado", c_fipe)

                        st.write("---")
                        
                        # Opção de vincular ao banco de dados (Apenas se o lojista quiser)
                        st.write("**Vincular ao Histórico de um Veículo da Frota? (Opcional)**")
                        st.write("Se você pesquisou um carro que já está no seu estoque, selecione a placa abaixo para gravar o histórico financeiro no sistema.")

                        res_frota = supabase.table("veiculo").select("placa, marca, modelo").execute()
                        lista_frota = [f"{v['placa']} - {v['marca']} {v['modelo']}" for v in res_frota.data]

                        with st.form("form_vincular_fipe", clear_on_submit=True):
                            col_v1, col_v2 = st.columns([3, 1])
                            
                            with col_v1:
                                veiculo_frota = st.selectbox("Veículos do Pátio", ["-- Não vincular (Consulta Externa) --"] + lista_frota)
                            with col_v2:
                                st.write("") 
                                st.write("")
                                submit_vincular = st.form_submit_button("Salvar no Banco de Dados", type="primary", use_container_width=True)

                            if submit_vincular:
                                if veiculo_frota == "-- Não vincular (Consulta Externa) --":
                                    st.warning("Nenhum veículo selecionado. O histórico não foi salvo.")
                                else:
                                    placa = veiculo_frota.split(" - ")[0]
                                    # Limpa a string "R$ 45.000,00" para "45000.00" (FLOAT)
                                    valor_float = float(v_fipe.replace("R$ ", "").replace(".", "").replace(",", "."))

                                    # Cria o mês no formato 'YYYY-MM' (ex: '2026-10') para respeitar o limite de 7 caracteres do banco
                                    mes_formatado = datetime.date.today().strftime("%Y-%m")

                                    novo_historico = {
                                        "placa_veiculo": placa,
                                        "mes_ano_referencia": mes_formatado,
                                        "valor_api": valor_float,
                                        "data_consulta": str(datetime.date.today())
                                    }

                                    supabase.table("historico").insert(novo_historico).execute()
                                    st.success(f"Sucesso! O valor de {v_fipe} foi gravado no histórico financeiro da placa {placa}.")
                    else:
                        st.error("Falha ao comunicar com o servidor da Tabela FIPE.")
                except Exception as e:
                    st.error("Erro técnico ao realizar a consulta final.")
                    with st.expander("Detalhes Técnicos"):
                        st.code(str(e))

# ==========================================
# ABA 4: VISUALIZAR HISTÓRICO FIPE
# ==========================================
with aba_historico:
    st.subheader("Histórico de Avaliações (FIPE)")
    st.write("Acompanhe a variação de preço de mercado dos veículos da frota.")
    
    try:
        # Busca os dados ordenando dos mais recentes para os mais antigos
        res_historico = supabase.table("historico").select("*").order("data_consulta", desc=True).execute()
        df_historico = pd.DataFrame(res_historico.data)
        
        if not df_historico.empty:
            
            # --- SEÇÃO DE FILTROS AVANÇADOS ---
            with st.expander("Filtros de Busca do Histórico", expanded=False):
                col_f1, col_f2, col_f3 = st.columns(3)
                
                with col_f1:
                    filtro_placa_hist = st.text_input("Filtrar por Placa", key="filtro_hist_placa").upper()
                with col_f2:
                    # Busca dinamicamente os meses que existem no banco
                    meses_unicos = df_historico["mes_ano_referencia"].unique()
                    filtro_mes = st.multiselect("Mês de Referência", options=meses_unicos)
                with col_f3:
                    # Busca dinamicamente as datas de consulta
                    datas_unicas = df_historico["data_consulta"].unique()
                    filtro_data = st.multiselect("Data da Consulta", options=datas_unicas)
            
            # --- APLICANDO OS FILTROS ---
            df_filtrado = df_historico.copy()
            
            if filtro_placa_hist:
                df_filtrado = df_filtrado[df_filtrado["placa_veiculo"].str.contains(filtro_placa_hist)]
            if filtro_mes:
                df_filtrado = df_filtrado[df_filtrado["mes_ano_referencia"].isin(filtro_mes)]
            if filtro_data:
                df_filtrado = df_filtrado[df_filtrado["data_consulta"].isin(filtro_data)]
            
            # --- EXIBIÇÃO DA TABELA ---
            if not df_filtrado.empty:
                # 1. Formata a moeda para o padrão BR
                df_filtrado["valor_api"] = df_filtrado["valor_api"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
                # 2. Renomeia as colunas para uma interface mais amigável e limpa
                df_exibicao = df_filtrado.rename(columns={
                    "placa_veiculo": "Placa",
                    "mes_ano_referencia": "Mês de Referência",
                    "valor_api": "Valor de Mercado",
                    "data_consulta": "Data da Consulta"
                })
                
                # Seleciona apenas as colunas renomeadas (ocultando IDs internos se houver)
                colunas_mostrar = ["Placa", "Mês de Referência", "Valor de Mercado", "Data da Consulta"]
                
                st.dataframe(df_exibicao[colunas_mostrar], use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum registro encontrado com os filtros aplicados.")
                
        else:
            st.info("Nenhuma avaliação foi salva no histórico até o momento.")
            
    except Exception as e:
        st.error("Erro ao carregar o histórico de avaliações.")
        with st.expander("Detalhes Técnicos"):
            st.code(str(e))