
import logging
from pathlib import Path

import streamlit as st
import pandas as pd
from database import supabase

# Configuração dos logs técnicos
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho da logo
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

# Configuração da página
st.set_page_config(
    page_title="Parceiros Comerciais",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🤝",
    layout="wide"
)

# Ajuste visual da logo
st.markdown(
    """
    <style>
    .logo-girocar {
        transform: translateY(12px);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Cabeçalho com logo e título
col_logo, col_titulo = st.columns(
    [1, 4],
    vertical_alignment="center"
)

with col_logo:
    if LOGO_PATH.is_file():
        st.markdown(
            '<div class="logo-girocar">',
            unsafe_allow_html=True
        )
        st.image(str(LOGO_PATH), width=180)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        logger.error("Logo não encontrada: %s", LOGO_PATH)

with col_titulo:
    st.title("Gestão de Parceiros Comerciais")

# Verificação da conexão com o banco
if not supabase:
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

# Abas para separar Clientes e Fornecedores
aba_clientes, aba_fornecedores = st.tabs(
    ["Clientes (CRM)", "Fornecedores"]
)

# ==========================================
# ABA 1: CLIENTES
# ==========================================
with aba_clientes:
    st.subheader("Cadastro de Clientes")

    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            cpf_cnpj_cliente = st.text_input(
                "CPF ou CNPJ",
                max_chars=18
            )
            nome_cliente = st.text_input(
                "Nome Completo / Razão Social"
            )
            telefone_cliente = st.text_input("Telefone")

        with col2:
            email_cliente = st.text_input("E-mail")
            status_funil = st.selectbox(
                "Status no Funil de Vendas",
                [
                    "Contato Inicial",
                    "Em Negociação",
                    "Venda Fechada"
                ]
            )

        submit_cliente = st.form_submit_button(
            "Salvar Cliente",
            type="primary"
        )

        if submit_cliente:
            if not cpf_cnpj_cliente.strip() or not nome_cliente.strip():
                st.warning(
                    "Preencha os campos obrigatórios (CPF/CNPJ e Nome)."
                )
            else:
                try:
                    novo_cliente = {
                        "cpf_cnpj": cpf_cnpj_cliente.strip(),
                        "nome_completo": nome_cliente.strip(),
                        "telefone": telefone_cliente.strip(),
                        "email": email_cliente.strip(),
                        "status_funil_vendas": status_funil
                    }

                    supabase.table("cliente").insert(
                        novo_cliente
                    ).execute()

                    st.success("Cliente cadastrado com sucesso!")

                except Exception:
                    logger.exception("Erro ao cadastrar cliente")
                    st.error(
                        "Erro ao cadastrar cliente. "
                        "Verifique os dados e se o CPF/CNPJ já existe."
                    )

    st.divider()
    st.subheader("Lista de Clientes")

    try:
        res_cli = supabase.table("cliente").select("*").execute()
        df_cli = pd.DataFrame(res_cli.data)

        if not df_cli.empty:
            st.dataframe(
                df_cli,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum cliente cadastrado.")

    except Exception:
        logger.exception("Erro ao carregar clientes")
        st.error("Erro ao carregar a lista de clientes.")

# ==========================================
# ABA 2: FORNECEDORES
# ==========================================
with aba_fornecedores:
    st.subheader("Cadastro de Fornecedores")

    with st.form("form_fornecedor", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            cnpj_cpf_forn = st.text_input(
                "CNPJ ou CPF do Fornecedor",
                max_chars=18
            )
            nome_forn = st.text_input("Nome / Razão Social")

        with col2:
            telefone_forn = st.text_input("Telefone de Contato")
            tipo_origem = st.selectbox(
                "Tipo de Origem",
                ["Repasse", "Leilão", "Particular"]
            )

        submit_forn = st.form_submit_button(
            "Salvar Fornecedor",
            type="primary"
        )

        if submit_forn:
            if not cnpj_cpf_forn.strip() or not nome_forn.strip():
                st.warning(
                    "Preencha os campos obrigatórios (CNPJ/CPF e Nome)."
                )
            else:
                try:
                    novo_forn = {
                        "cnpj_cpf": cnpj_cpf_forn.strip(),
                        "nome_razao_social": nome_forn.strip(),
                        "telefone": telefone_forn.strip(),
                        "tipo_origem": tipo_origem
                    }

                    supabase.table("fornecedor").insert(
                        novo_forn
                    ).execute()

                    st.success("Fornecedor cadastrado com sucesso!")

                except Exception:
                    logger.exception("Erro ao cadastrar fornecedor")
                    st.error(
                        "Erro ao cadastrar fornecedor. "
                        "Verifique os dados e tente novamente."
                    )

    st.divider()
    st.subheader("Lista de Fornecedores")

    try:
        res_forn = supabase.table("fornecedor").select("*").execute()
        df_forn = pd.DataFrame(res_forn.data)

        if not df_forn.empty:
            st.dataframe(
                df_forn,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum fornecedor cadastrado.")

    except Exception:
        logger.exception("Erro ao carregar fornecedores")
        st.error("Erro ao carregar a lista de fornecedores.")
