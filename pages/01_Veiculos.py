import datetime
import logging
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from database import supabase

# ==========================================
# CONFIGURAÇÕES
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho da logo na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

FIPE_BASE_URL = "https://parallelum.com.br/fipe/api/v1/carros"
FIPE_HEADERS = {"User-Agent": "GiroCarERP/1.0"}
FIPE_SELECIONE = "-- Selecione --"
FIPE_NAO_VINCULAR = "-- Não vincular (Consulta Externa) --"

STATUS_ATUALIZAR = ["Disponivel", "Em preparacao", "Vendido", "Reservado"]
STATUS_CADASTRO = ["Disponivel", "Em preparacao", "Vendido"]

MSG_ERRO_CONEXAO = (
    "⚠️ Não foi possível estabelecer conexão com o banco de dados. "
    "Verifique sua conexão de rede ou tente novamente mais tarde."
)

st.set_page_config(
    page_title="GiroCar | Gestão de Veículos",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🚙",
    layout="wide",
)


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def formatar_reais(valor):
    """Formata número no padrão brasileiro (R$ 1.234,56). Valores nulos viram texto vazio."""
    if pd.isnull(valor):
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mostrar_detalhes_tecnicos(erro, titulo="Detalhes Técnicos (Para Suporte)"):
    with st.expander(titulo):
        st.code(str(erro))


def filtrar_texto_contem(df, coluna, texto):
    return df[df[coluna].str.contains(texto)] if texto else df


def filtrar_em_lista(df, coluna, valores):
    return df[df[coluna].isin(valores)] if valores else df


# ---------- FIPE (com cache para não sobrecarregar a API) ----------
def _fipe_get(caminho):
    """Faz GET na API FIPE e devolve o JSON (ou None se falhar)."""
    try:
        req = requests.get(f"{FIPE_BASE_URL}/{caminho}", headers=FIPE_HEADERS)
        return req.json() if req.status_code == 200 else None
    except Exception:
        return None


@st.cache_data(ttl=86400)
def get_marcas():
    return _fipe_get("marcas") or []


@st.cache_data(ttl=86400)
def get_modelos(cod_marca):
    dados = _fipe_get(f"marcas/{cod_marca}/modelos")
    return dados["modelos"] if dados else []


@st.cache_data(ttl=86400)
def get_anos(cod_marca, cod_modelo):
    return _fipe_get(f"marcas/{cod_marca}/modelos/{cod_modelo}/anos") or []


def valor_fipe_para_float(texto):
    """Converte 'R$ 45.000,00' em 45000.0."""
    return float(texto.replace("R$ ", "").replace(".", "").replace(",", "."))


# ==========================================
# CABEÇALHO
# ==========================================
def render_cabecalho():
    # CSS para alinhar a logo com o título
    st.markdown(
        """
        <style>
        .logo-girocar {
            transform: translateY(18px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_logo, col_titulo = st.columns([1, 4], vertical_alignment="center")

    with col_logo:
        if LOGO_PATH.is_file():
            st.markdown('<div class="logo-girocar">', unsafe_allow_html=True)
            st.image(str(LOGO_PATH), width=180)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            logger.error("Logo não encontrada: %s", LOGO_PATH)

    with col_titulo:
        st.title("Gestão de Veículos")


# ==========================================
# ABA 1: CONSULTAR E GERENCIAR (READ, UPDATE, DELETE)
# ==========================================
COLUNAS_RENOMEADAS_VEICULO = {
    "placa": "Placa",
    "chassi": "Chassi",
    "marca": "Marca",
    "modelo": "Modelo",
    "ano_fabricacao": "Ano Fab.",
    "ano_modelo": "Ano Mod.",
    "cor": "Cor",
    "quilometragem": "KM",
    "valor_aquisicao": "Valor de Aquisição",
    "status_veiculo": "Status",
    "indicador_leilao": "Leilão?",
    "indicador_sinistro": "Sinistro?",
    "cnpj_loja": "CNPJ Loja",
    "cnpj_cpf_fornecedor": "Doc. Fornecedor",
}

COLUNAS_MOSTRAR_VEICULO = [
    "Placa", "Marca", "Modelo", "Cor", "Ano Fab.", "Ano Mod.",
    "KM", "Valor de Aquisição", "Status", "Leilão?", "Sinistro?",
]


def render_filtros_veiculos(df):
    with st.expander("Filtros de Busca", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_placa = st.text_input("Buscar por Placa").upper()
        with col_f2:
            filtro_status = st.multiselect("Filtrar por Status", options=df["status_veiculo"].unique())
        with col_f3:
            filtro_marca = st.multiselect("Filtrar por Marca", options=df["marca"].unique())

    df_filtrado = df.copy()
    df_filtrado = filtrar_texto_contem(df_filtrado, "placa", filtro_placa)
    df_filtrado = filtrar_em_lista(df_filtrado, "status_veiculo", filtro_status)
    df_filtrado = filtrar_em_lista(df_filtrado, "marca", filtro_marca)
    return df_filtrado


def render_tabela_veiculos(df_filtrado):
    # Cópia só para exibição: df_filtrado segue intacto para UPDATE/DELETE
    df_formatado = df_filtrado.copy()
    df_formatado["valor_aquisicao"] = df_formatado["valor_aquisicao"].apply(formatar_reais)
    df_exibicao = df_formatado.rename(columns=COLUNAS_RENOMEADAS_VEICULO)
    st.dataframe(df_exibicao[COLUNAS_MOSTRAR_VEICULO], use_container_width=True, hide_index=True)


def render_acoes_rapidas(df_filtrado):
    st.subheader("Ações Rápidas")
    col1, col2 = st.columns(2)

    # UPDATE
    with col1:
        st.write("**Atualizar Status do Veículo**")
        placa_edit = st.selectbox("Selecione a Placa", df_filtrado["placa"], key="edit_placa")
        novo_status = st.selectbox("Novo Status", STATUS_ATUALIZAR)

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
            except Exception:
                st.error("Não é possível excluir este veículo pois ele já possui vínculo com Manutenções ou Histórico.")


def render_aba_consulta():
    st.subheader("Veículos no Sistema")
    try:
        res = supabase.table("veiculo").select("*").execute()
        df = pd.DataFrame(res.data)

        if df.empty:
            st.info("Nenhum veículo cadastrado no sistema.")
            return

        df_filtrado = render_filtros_veiculos(df)
        render_tabela_veiculos(df_filtrado)
        st.divider()

        if not df_filtrado.empty:
            render_acoes_rapidas(df_filtrado)
        else:
            st.warning("Nenhum veículo encontrado com os filtros aplicados.")

    except Exception as e:
        st.error(MSG_ERRO_CONEXAO)
        mostrar_detalhes_tecnicos(e)


# ==========================================
# ABA 2: CADASTRAR VEÍCULO
# ==========================================
def render_aba_cadastro():
    st.subheader("Formulário de Entrada de Veículo")

    try:
        # Busca dinamicamente os parceiros cadastrados no banco
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
                loja_selecionada = st.selectbox(
                    "Loja (Destino)",
                    lista_lojas if lista_lojas else ["-- Cadastre uma Loja --"],
                )
                fornecedor_selecionado = st.selectbox(
                    "Fornecedor (Origem)",
                    lista_fornecedores if lista_fornecedores else ["-- Cadastre um Fornecedor --"],
                )

            submit_cadastro = st.form_submit_button("Salvar Registro de Veículo", type="primary")

            if submit_cadastro:
                if not lista_lojas or not lista_fornecedores:
                    st.error("Não é possível salvar. Cadastre primeiro as Lojas e Fornecedores na aba Parceiros.")
                elif not placa or not chassi or not marca or not modelo:
                    st.warning("Por favor, preencha os campos obrigatórios (Placa, Chassi, Marca, Modelo).")
                else:
                    novo_veiculo = {
                        "placa": placa,
                        "chassi": chassi,
                        "marca": marca,
                        "modelo": modelo,
                        "cor": cor,
                        "ano_fabricacao": ano_fab,
                        "ano_modelo": ano_mod,
                        "quilometragem": km,
                        "valor_aquisicao": valor_aquisicao,
                        "status_veiculo": status_inicial,
                        "indicador_leilao": indicador_leilao,
                        "indicador_sinistro": indicador_sinistro,
                        # Extrai apenas o CNPJ/CPF (tudo antes do hífen)
                        "cnpj_loja": loja_selecionada.split(" - ")[0].strip(),
                        "cnpj_cpf_fornecedor": fornecedor_selecionado.split(" - ")[0].strip(),
                    }

                    supabase.table("veiculo").insert(novo_veiculo).execute()

                    st.success(f"Sucesso! O veículo {marca} {modelo} (Placa: {placa}) foi cadastrado e já está disponível no pátio.")

    except Exception as e:
        st.error("Erro ao carregar o formulário de cadastro ou salvar os dados.")
        mostrar_detalhes_tecnicos(e)


# ==========================================
# ABA 3: CONSULTA FIPE (LIVRE E CASCATA)
# ==========================================
def render_resultado_fipe(cod_marca, cod_modelo, cod_ano):
    st.divider()

    try:
        req_final = requests.get(
            f"{FIPE_BASE_URL}/marcas/{cod_marca}/modelos/{cod_modelo}/anos/{cod_ano}",
            headers=FIPE_HEADERS,
        )

        if req_final.status_code != 200:
            st.error("Falha ao comunicar com o servidor da Tabela FIPE.")
            return

        dados = req_final.json()
        v_fipe = dados.get("Valor")
        m_ref = dados.get("MesReferencia")
        c_fipe = dados.get("CodigoFipe")

        st.subheader("📊 Resultado da Avaliação Oficial")
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Valor de Mercado", v_fipe)
        col_r2.metric("Mês de Referência", m_ref)
        col_r3.metric("Código FIPE Encontrado", c_fipe)

        st.write("---")
        render_vinculo_fipe(v_fipe)

    except Exception as e:
        st.error("Erro técnico ao realizar a consulta final.")
        mostrar_detalhes_tecnicos(e, titulo="Detalhes Técnicos")


def render_vinculo_fipe(v_fipe):
    """Permite gravar o valor FIPE consultado no histórico de um veículo da frota (opcional)."""
    st.write("**Vincular ao Histórico de um Veículo da Frota? (Opcional)**")
    st.write("Se você pesquisou um carro que já está no seu estoque, selecione a placa abaixo para gravar o histórico financeiro no sistema.")

    res_frota = supabase.table("veiculo").select("placa, marca, modelo").execute()
    lista_frota = [f"{v['placa']} - {v['marca']} {v['modelo']}" for v in res_frota.data]

    with st.form("form_vincular_fipe", clear_on_submit=True):
        col_v1, col_v2 = st.columns([3, 1])

        with col_v1:
            veiculo_frota = st.selectbox("Veículos do Pátio", [FIPE_NAO_VINCULAR] + lista_frota)
        with col_v2:
            st.write("")
            st.write("")
            submit_vincular = st.form_submit_button(
                "Salvar no Banco de Dados", type="primary", use_container_width=True
            )

        if submit_vincular:
            if veiculo_frota == FIPE_NAO_VINCULAR:
                st.warning("Nenhum veículo selecionado. O histórico não foi salvo.")
                return

            placa = veiculo_frota.split(" - ")[0].strip()
            hoje = datetime.date.today()

            novo_historico = {
                "placa_veiculo": placa,
                # Formato 'YYYY-MM' (ex: '2026-10') para respeitar o limite de 7 caracteres do banco
                "mes_ano_referencia": hoje.strftime("%Y-%m"),
                "valor_api": valor_fipe_para_float(v_fipe),
                "data_consulta": str(hoje),
            }

            supabase.table("historico").insert(novo_historico).execute()
            st.success(f"Sucesso! O valor de {v_fipe} foi gravado no histórico financeiro da placa {placa}.")


def render_aba_fipe():
    st.subheader("Consultar Avaliação de Veículos (Tabela FIPE)")
    st.write("Pesquise o valor de mercado de qualquer veículo para avaliação de troca ou para atualizar o estoque atual.")

    col_f1, col_f2, col_f3 = st.columns(3)

    marcas = get_marcas()
    opcoes_marcas = {m["nome"]: m["codigo"] for m in marcas} if marcas else {}

    with col_f1:
        marca_sel = st.selectbox("1. Selecione a Marca", [FIPE_SELECIONE] + list(opcoes_marcas.keys()))

    if marca_sel == FIPE_SELECIONE:
        return

    cod_marca = opcoes_marcas[marca_sel]
    opcoes_modelos = {m["nome"]: m["codigo"] for m in get_modelos(cod_marca)}

    with col_f2:
        modelo_sel = st.selectbox("2. Selecione o Modelo", [FIPE_SELECIONE] + list(opcoes_modelos.keys()))

    if modelo_sel == FIPE_SELECIONE:
        return

    cod_modelo = opcoes_modelos[modelo_sel]
    opcoes_anos = {a["nome"]: a["codigo"] for a in get_anos(cod_marca, cod_modelo)}

    with col_f3:
        ano_sel = st.selectbox("3. Selecione o Ano/Combustível", [FIPE_SELECIONE] + list(opcoes_anos.keys()))

    # Só busca o preço final quando os 3 campos estiverem preenchidos
    if ano_sel != FIPE_SELECIONE:
        render_resultado_fipe(cod_marca, cod_modelo, opcoes_anos[ano_sel])


# ==========================================
# ABA 4: HISTÓRICO FIPE
# ==========================================
COLUNAS_RENOMEADAS_HISTORICO = {
    "placa_veiculo": "Placa",
    "mes_ano_referencia": "Mês de Referência",
    "valor_api": "Valor de Mercado",
    "data_consulta": "Data da Consulta",
}


def render_aba_historico():
    st.subheader("Histórico de Avaliações (FIPE)")
    st.write("Acompanhe a variação de preço de mercado dos veículos da frota.")

    try:
        res_historico = (
            supabase.table("historico")
            .select("*")
            .order("data_consulta", desc=True)
            .execute()
        )
        df_historico = pd.DataFrame(res_historico.data)

        if df_historico.empty:
            st.info("Nenhuma avaliação foi salva no histórico até o momento.")
            return

        with st.expander("Filtros de Busca do Histórico", expanded=False):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                filtro_placa_hist = st.text_input("Filtrar por Placa", key="filtro_hist_placa").upper()
            with col_f2:
                filtro_mes = st.multiselect("Mês de Referência", options=df_historico["mes_ano_referencia"].unique())
            with col_f3:
                filtro_data = st.multiselect("Data da Consulta", options=df_historico["data_consulta"].unique())

        df_filtrado = df_historico.copy()
        df_filtrado = filtrar_texto_contem(df_filtrado, "placa_veiculo", filtro_placa_hist)
        df_filtrado = filtrar_em_lista(df_filtrado, "mes_ano_referencia", filtro_mes)
        df_filtrado = filtrar_em_lista(df_filtrado, "data_consulta", filtro_data)

        if df_filtrado.empty:
            st.warning("Nenhum registro encontrado com os filtros aplicados.")
            return

        df_filtrado["valor_api"] = df_filtrado["valor_api"].apply(formatar_reais)
        df_exibicao = df_filtrado.rename(columns=COLUNAS_RENOMEADAS_HISTORICO)
        colunas_mostrar = list(COLUNAS_RENOMEADAS_HISTORICO.values())

        st.dataframe(df_exibicao[colunas_mostrar], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Erro ao carregar o histórico de avaliações.")
        mostrar_detalhes_tecnicos(e, titulo="Detalhes Técnicos")


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
render_cabecalho()

if not supabase:
    st.error("Não foi possível estabelecer conexão com o banco de dados. Verifique sua conexão de rede ou tente novamente mais tarde.")
    st.stop()

aba_consulta, aba_cadastro, aba_fipe, aba_historico = st.tabs([
    "Consultar e Gerenciar",
    "Cadastrar Veículo",
    "Consulta Tabela FIPE",
    "Histórico de Avaliações",
])

with aba_consulta:
    render_aba_consulta()

with aba_cadastro:
    render_aba_cadastro()

with aba_fipe:
    render_aba_fipe()

with aba_historico:
    render_aba_historico()