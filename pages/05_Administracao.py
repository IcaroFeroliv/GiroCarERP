import logging
from pathlib import Path

import streamlit as st
import pandas as pd
from database import supabase


# ==========================================
# CONFIGURAÇÕES
# ==========================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

st.set_page_config(
    page_title="GiroCar | Administração",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🚗",
    layout="wide"
)


# ==========================================
# ESTILO VISUAL
# ==========================================

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


# ==========================================
# CABEÇALHO
# ==========================================

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


# ==========================================
# CONEXÃO COM O BANCO
# ==========================================

if supabase is None:
    st.error(
        "Não foi possível conectar ao sistema. "
        "Tente novamente mais tarde ou entre em contato com o suporte."
    )
    st.stop()


# ==========================================
# ABAS
# ==========================================

aba_lojas, aba_funcionarios = st.tabs(
    ["Lojas (Filiais)", "Funcionários"]
)


# ==========================================
# ABA 1: LOJAS
# ==========================================

with aba_lojas:

    st.subheader("Cadastro de Loja")

    with st.form("form_loja", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            cnpj_loja = st.text_input(
                "CNPJ da Loja",
                max_chars=18
            )

            nome_loja = st.text_input(
                "Nome da Unidade"
            )

        with col2:
            endereco_loja = st.text_input(
                "Endereço Completo"
            )

        submit_loja = st.form_submit_button(
            "Salvar Loja",
            type="primary"
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

                    supabase.table("loja").insert(
                        nova_loja
                    ).execute()

                    st.success("Loja cadastrada com sucesso!")

                except Exception:
                    logger.exception("Falha ao cadastrar loja")

                    st.error(
                        "Não foi possível cadastrar a loja. "
                        "Verifique os dados e tente novamente."
                    )

    st.divider()

    # CONSULTA DE LOJAS
    with st.expander(
        "Consultar lojas cadastradas",
        expanded=False
    ):

        st.subheader("Lojas cadastradas")

        try:
            res_loja = (
                supabase.table("loja")
                .select("*")
                .execute()
            )

            df_loja = pd.DataFrame(res_loja.data or [])

            if not df_loja.empty:

                # PESQUISA DE LOJAS
                busca_loja = st.text_input(
                    "Buscar loja",
                    placeholder="Digite CNPJ, nome da unidade ou endereço...",
                    key="busca_loja"
                )

                df_loja_filtrado = df_loja.copy()

                if busca_loja.strip():

                    campos_busca_loja = [
                        coluna
                        for coluna in [
                            "cnpj",
                            "nome_unidade",
                            "endereco"
                        ]
                        if coluna in df_loja_filtrado.columns
                    ]

                    if campos_busca_loja:
                        termo = busca_loja.strip()

                        encontrados = (
                            df_loja_filtrado[campos_busca_loja]
                            .fillna("")
                            .astype(str)
                            .apply(
                                lambda coluna: coluna.str.contains(
                                    termo,
                                    case=False,
                                    regex=False
                                )
                            )
                            .any(axis=1)
                        )

                        df_loja_filtrado = (
                            df_loja_filtrado[encontrados]
                        )

                # NOMES AMIGÁVEIS
                nomes_colunas_loja = {
                    "cnpj": "CNPJ",
                    "nome_unidade": "Nome da unidade",
                    "endereco": "Endereço"
                }

                colunas_loja = [
                    coluna
                    for coluna in nomes_colunas_loja
                    if coluna in df_loja_filtrado.columns
                ]

                df_exibicao_loja = (
                    df_loja_filtrado[colunas_loja]
                    .rename(columns=nomes_colunas_loja)
                )

                st.caption(
                    f"{len(df_loja_filtrado)} unidade(s) encontrada(s)"
                )

                if not df_exibicao_loja.empty:

                    st.dataframe(
                        df_exibicao_loja,
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info(
                        "Nenhuma loja corresponde à sua pesquisa."
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
            matricula = st.text_input(
                "Matrícula",
                max_chars=50
            )

            nome_func = st.text_input(
                "Nome Completo"
            )

        with col2:
            cargo = st.selectbox(
                "Cargo / Nível de Acesso",
                ["Vendedor", "Gerente"]
            )

            cnpj_vinculo = st.text_input(
                "CNPJ da Loja (Vínculo)"
            )

        with col3:
            data_admissao = st.date_input(
                "Data de Admissão"
            )

        submit_func = st.form_submit_button(
            "Salvar Funcionário",
            type="primary"
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

                    st.success(
                        "Funcionário cadastrado com sucesso!"
                    )

                except Exception:
                    logger.exception(
                        "Falha ao cadastrar funcionário"
                    )

                    st.error(
                        "Não foi possível cadastrar o funcionário. "
                        "Confira os dados e se a loja vinculada existe."
                    )

    st.divider()

    # CONSULTA DE FUNCIONÁRIOS
    with st.expander(
        "Consultar funcionários",
        expanded=False
    ):

        st.subheader("Quadro de Funcionários")

        try:
            res_func = (
                supabase.table("funcionario")
                .select("*")
                .execute()
            )

            df_func = pd.DataFrame(res_func.data or [])

            if not df_func.empty:

                col_filtro, col_busca = st.columns([1, 2])

                # FILTRO POR CARGO
                if "cargo_nivel_acesso" in df_func.columns:

                    cargos_disponiveis = (
                        df_func["cargo_nivel_acesso"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )

                    cargos_disponiveis.sort()

                    with col_filtro:
                        cargo_selecionado = st.selectbox(
                            "Filtrar por cargo",
                            ["Todos"] + cargos_disponiveis,
                            key="filtro_cargo_funcionario"
                        )

                else:
                    cargo_selecionado = "Todos"

                # PESQUISA DE FUNCIONÁRIOS
                with col_busca:
                    busca_func = st.text_input(
                        "Buscar funcionário",
                        placeholder=(
                            "Digite matrícula, nome ou CNPJ da loja..."
                        ),
                        key="busca_funcionario"
                    )

                df_func_filtrado = df_func.copy()

                if cargo_selecionado != "Todos":
                    df_func_filtrado = df_func_filtrado[
                        df_func_filtrado["cargo_nivel_acesso"]
                        == cargo_selecionado
                    ]

                if busca_func.strip():

                    campos_busca_func = [
                        coluna
                        for coluna in [
                            "matricula",
                            "nome",
                            "cnpj_loja",
                            "data_admissao"
                        ]
                        if coluna in df_func_filtrado.columns
                    ]

                    if campos_busca_func:
                        termo = busca_func.strip()

                        encontrados = (
                            df_func_filtrado[campos_busca_func]
                            .fillna("")
                            .astype(str)
                            .apply(
                                lambda coluna: coluna.str.contains(
                                    termo,
                                    case=False,
                                    regex=False
                                )
                            )
                            .any(axis=1)
                        )

                        df_func_filtrado = (
                            df_func_filtrado[encontrados]
                        )

                # NOMES AMIGÁVEIS
                nomes_colunas_func = {
                    "matricula": "Matrícula",
                    "nome": "Nome do funcionário",
                    "cargo_nivel_acesso": "Cargo",
                    "cnpj_loja": "CNPJ da loja",
                    "data_admissao": "Data de admissão"
                }

                colunas_func = [
                    coluna
                    for coluna in nomes_colunas_func
                    if coluna in df_func_filtrado.columns
                ]

                df_exibicao_func = (
                    df_func_filtrado[colunas_func]
                    .rename(columns=nomes_colunas_func)
                )

                st.caption(
                    f"{len(df_func_filtrado)} funcionário(s) encontrado(s)"
                )

                if not df_exibicao_func.empty:

                    st.dataframe(
                        df_exibicao_func,
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info(
                        "Nenhum funcionário corresponde à sua pesquisa."
                    )

            else:
                st.info("Nenhum funcionário cadastrado.")

        except Exception:
            logger.exception(
                "Falha ao carregar funcionários"
            )

            st.error(
                "Não foi possível carregar a lista de funcionários. "
                "Tente novamente mais tarde."
            )
