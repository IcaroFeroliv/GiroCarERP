import streamlit as st
from database import supabase
from components.regras_negocio.mostrar_detalhes_tecnicos import mostrar_detalhes_tecnicos

STATUS_CADASTRO = ["Disponivel", "Em preparacao", "Vendido"]

def render_aba_cadastro():
    st.subheader("Formulário de Entrada de Veículo")
    try:
        res_lojas = supabase.table("loja").select("cnpj, nome_unidade").execute()
        lista_lojas = [f"{l['cnpj']} - {l['nome_unidade']}" for l in res_lojas.data]

        res_fornecedores = supabase.table("fornecedor").select("cnpj_cpf, nome_razao_social").execute()
        lista_fornecedores = [f"{f['cnpj_cpf']} - {f['nome_razao_social']}" for f in res_fornecedores.data]

        if not lista_lojas or not lista_fornecedores:
            st.warning("⚠️ Atenção: Nenhuma loja ou fornecedor cadastrado. Vá até a aba Parceiros e cadastre-os antes de dar entrada na frota.")

        with st.form("form_cadastro_veiculo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                placa = st.text_input("Placa", max_chars=7).upper()
                chassi = st.text_input("Chassi", max_chars=17).upper()
                marca = st.text_input("Marca")
                modelo = st.text_input("Modelo")
                cor = st.text_input("Cor")
            with col2:
                ano_fab = st.number_input("Ano Fabricação", min_value=1900, max_value=2100, step=1, value=2024)
                ano_mod = st.number_input("Ano Modelo", min_value=1900, max_value=2100, step=1, value=2024)
                km = st.number_input("Quilometragem (KM)", min_value=0, step=1000)
                valor_aquisicao = st.number_input("Valor de Aquisição (R$)", min_value=0.0, step=1000.0)
                status_inicial = st.selectbox("Status Inicial", STATUS_CADASTRO)

            st.write("---")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.write("### Indicadores de Risco")
                indicador_leilao = st.checkbox("Indicador de Leilão?")
                indicador_sinistro = st.checkbox("Indicador de Sinistro?")
            with col_r2:
                st.write("### Vínculos")
                loja_selecionada = st.selectbox("Loja (Destino)", lista_lojas if lista_lojas else ["-- Cadastre uma Loja --"])
                fornecedor_selecionado = st.selectbox("Fornecedor (Origem)", lista_fornecedores if lista_fornecedores else ["-- Cadastre um Fornecedor --"])

            submit_cadastro = st.form_submit_button("Salvar Registro de Veículo", type="primary")

            if submit_cadastro:
                if not lista_lojas or not lista_fornecedores:
                    st.error("Não é possível salvar. Cadastre primeiro as Lojas e Fornecedores na aba Parceiros.")
                elif not placa or not chassi or not marca or not modelo:
                    st.warning("Por favor, preencha os campos obrigatórios (Placa, Chassi, Marca, Modelo).")
                else:
                    novo_veiculo = {
                        "placa": placa, "chassi": chassi, "marca": marca, "modelo": modelo,
                        "cor": cor, "ano_fabricacao": ano_fab, "ano_modelo": ano_mod,
                        "quilometragem": km, "valor_aquisicao": valor_aquisicao,
                        "status_veiculo": status_inicial, "indicador_leilao": indicador_leilao,
                        "indicador_sinistro": indicador_sinistro,
                        "cnpj_loja": loja_selecionada.split(" - ")[0].strip(),
                        "cnpj_cpf_fornecedor": fornecedor_selecionado.split(" - ")[0].strip(),
                    }
                    supabase.table("veiculo").insert(novo_veiculo).execute()
                    st.success(f"Sucesso! O veículo {marca} {modelo} (Placa: {placa}) foi cadastrado e já está disponível no pátio.")

    except Exception as e:
        st.error("Erro ao carregar o formulário de cadastro ou salvar os dados.")
        mostrar_detalhes_tecnicos(e)