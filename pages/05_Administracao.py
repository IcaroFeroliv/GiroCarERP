
import logging
from pathlib import Path

import streamlit as st
import pandas as pd
from database import supabase

# Configuração dos logs técnicos
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho da logo na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

# Configuração da página
st.set_page_config(
    page_title="GiroCar | Administração",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🚗",
    layout="wide"
)

# CSS para alinhar a logo com o título
st.markdown(
    """
    <style>
    .logo-girocar {
        transform: translateY(18px);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Cabeçalho com a logo alinhada ao título
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
    st.title("Administração (RH e Filiais)")

# Verificação da conexão com o banco
if not supabase:
    st.error(
        "Não foi possível conectar ao sistema. "
        "Tente novamente mais tarde ou entre em contato com o suporte."
    )
    st.stop()

aba_lojas, aba_funcionarios = st.tabs(
    ["🏪 Lojas (Filiais)", "🧑‍💼 Funcionários"]
)

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

        submit_loja = st.form_submit_button(
            "Salvar Loja", type="primary"
        )

        if submit_loja:
            if not cnpj_loja.strip() or not nome_loja.strip():
                st.warning(
                    "Preencha os campos obrigatórios (CNPJ e Nome)."
                )
            else:
                try:
                    nova_loja = {
                        "cnpj": cnpj_loja.strip(),
                        "nome_unidade": nome_loja.strip(),
                        "endereco": endereco_loja.strip()
                    }

                    supabase.table("loja").insert(nova_loja).execute()
                    st.success("Loja cadastrada com sucesso!")

                except Exception:
                    logger.exception("Falha ao cadastrar loja")
                    st.error(
                        "Não foi possível cadastrar a loja. "
                        "Verifique os dados e tente novamente. "
                        "Se o problema persistir, entre em contato com o suporte."
                    )

    st.divider()
    st.subheader("Lista de Lojas")

    try:
        res_loja = supabase.table("loja").select("*").execute()
        df_loja = pd.DataFrame(res_loja.data)

        if not df_loja.empty:
            st.dataframe(
                df_loja,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhuma loja cadastrada.")

    except Exception:
        logger.exception("Falha ao carregar lojas")
        st.error(
            "Não foi possível carregar a lista de lojas. "
            "Tente novamente mais tarde."
        )

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
            cargo = st.selectbox(
                "Cargo / Nível de Acesso",
                ["Vendedor", "Gerente"]
            )
            cnpj_vinculo = st.text_input("CNPJ da Loja (Vínculo)")

        with col3:
            data_admissao = st.date_input("Data de Admissão")

        submit_func = st.form_submit_button(
            "Salvar Funcionário", type="primary"
        )

        if submit_func:
            if (
                not matricula.strip()
                or not nome_func.strip()
                or not cnpj_vinculo.strip()
            ):
                st.warning(
                    "Preencha Matrícula, Nome e o CNPJ da Loja vinculada."
                )
            else:
                try:
                    novo_func = {
                        "matricula": matricula.strip(),
                        "nome": nome_func.strip(),
                        "cargo_nivel_acesso": cargo,
                        "cnpj_loja": cnpj_vinculo.strip(),
                        "data_admissao": str(data_admissao)
                    }

                    supabase.table("funcionario").insert(
                        novo_func
                    ).execute()

                    st.success("Funcionário cadastrado com sucesso!")

                except Exception:
                    logger.exception("Falha ao cadastrar funcionário")
                    st.error(
                        "Não foi possível cadastrar o funcionário. "
                        "Confira os dados e se a loja vinculada existe. "
                        "Se o problema persistir, entre em contato com o suporte."
                    )

    st.divider()
    st.subheader("Quadro de Funcionários")

    try:
        res_func = supabase.table("funcionario").select("*").execute()
        df_func = pd.DataFrame(res_func.data)

        if not df_func.empty:
            st.dataframe(
                df_func,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum funcionário cadastrado.")

    except Exception:
        logger.exception("Falha ao carregar funcionários")
        st.error(
            "Não foi possível carregar a lista de funcionários. "
            "Tente novamente mais tarde."
        )
