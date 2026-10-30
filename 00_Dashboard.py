
import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from database import supabase


# ==========================================
# CONFIGURAÇÕES GERAIS
# ==========================================

# Configura o sistema de logs para registrar mensagens de nível INFO
# ou superior, permitindo acompanhar a execução e identificar erros.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define o diretório principal do projeto e o caminho da imagem da logo.
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "girocar.png"

# Constantes utilizadas para identificar os estados dos veículos
# e a opção de visualização de todo o histórico de vendas.
STATUS_DISPONIVEL = "Disponivel"
STATUS_PREPARACAO = "Em preparacao"
FILTRO_TODO_HISTORICO = "Todo o Histórico"

# Configura as propriedades iniciais da aplicação Streamlit.
st.set_page_config(
    page_title="GiroCar | Dashboard de Veículos",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🚙",
    layout="wide",
)


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def formatar_moeda(valor):
    """
    Formata um valor numérico para o padrão monetário brasileiro.

    Parâmetros:
        valor: Valor numérico que será formatado.

    Retorno:
        String contendo o valor com duas casas decimais,
        separador de milhar por ponto e separador decimal por vírgula.

    Exemplo:
        12500.50 -> "12.500,50"
    """
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_dados():
    """
    Consulta as informações de veículos e transações no Supabase.

    São realizadas duas consultas independentes:
        - Tabela 'veiculo': recupera informações cadastrais,
          valores de aquisição e situação atual dos veículos.
        - Tabela 'transacao': recupera informações das vendas,
          incluindo placa do veículo, valor negociado e data.

    Retorno:
        Tupla contendo dois DataFrames do Pandas:
        - DataFrame com os dados dos veículos.
        - DataFrame com os dados das transações.
    """
    res_veiculos = (
        supabase.table("veiculo")
        .select("placa, modelo, marca, valor_aquisicao, status_veiculo")
        .execute()
    )
    res_transacoes = (
        supabase.table("transacao")
        .select("placa_veiculo, valor_final_negociado, data")
        .execute()
    )
    return pd.DataFrame(res_veiculos.data), pd.DataFrame(res_transacoes.data)


def calcular_estoque(df_veiculos):
    """
    Calcula a posição atual do estoque de veículos.

    Separa os veículos conforme seus respectivos status,
    contabiliza as quantidades e calcula o capital investido
    nos veículos disponíveis e em preparação.

    Parâmetros:
        df_veiculos: DataFrame contendo os dados dos veículos.

    Retorno:
        Tupla contendo:
        - Quantidade de veículos disponíveis.
        - Quantidade de veículos em preparação.
        - Capital total investido no estoque.
        - DataFrame contendo somente os veículos em preparação.

    Observação:
        Caso o DataFrame esteja vazio, retorna valores zerados
        e um DataFrame vazio para os veículos em preparação.
    """
    df_preparacao = pd.DataFrame()
    if df_veiculos.empty:
        return 0, 0, 0.0, df_preparacao

    # Filtra os veículos conforme o status atual.
    df_disponivel = df_veiculos[df_veiculos["status_veiculo"] == STATUS_DISPONIVEL]
    df_preparacao = df_veiculos[df_veiculos["status_veiculo"] == STATUS_PREPARACAO]

    # Soma os valores de aquisição dos veículos disponíveis
    # e daqueles que ainda estão em preparação.
    capital = (
        df_disponivel["valor_aquisicao"].sum()
        + df_preparacao["valor_aquisicao"].sum()
    )

    return len(df_disponivel), len(df_preparacao), capital, df_preparacao


def preparar_vendas(df_transacoes, df_veiculos):
    """
    Prepara os dados das vendas para análise de lucratividade.

    Realiza o cruzamento entre as informações de transações
    e veículos utilizando a placa como chave de relacionamento.

    Após o cruzamento:
        - Calcula o lucro bruto de cada venda.
        - Converte a coluna de data para o formato datetime.
        - Cria uma coluna auxiliar com mês e ano da venda,
          utilizada posteriormente no filtro de período.

    Parâmetros:
        df_transacoes: DataFrame contendo os registros de transações.
        df_veiculos: DataFrame contendo os dados cadastrais dos veículos.

    Retorno:
        DataFrame contendo os dados das vendas associados
        às informações dos respectivos veículos.
    """
    df_vendas = pd.merge(
        df_transacoes, df_veiculos, left_on="placa_veiculo", right_on="placa"
    )

    # Calcula o lucro bruto considerando a diferença entre
    # o valor final negociado e o valor de aquisição do veículo.
    df_vendas["Lucro Bruto (R$)"] = (
        df_vendas["valor_final_negociado"] - df_vendas["valor_aquisicao"]
    )

    # Converte a data da transação e cria a identificação do mês/ano.
    df_vendas["data"] = pd.to_datetime(df_vendas["data"])
    df_vendas["mes_ano"] = df_vendas["data"].dt.strftime("%m/%Y")

    return df_vendas


def montar_dados_grafico(df_vendas):
    """
    Organiza os dados necessários para a construção do gráfico de lucratividade.

    Seleciona a data da venda, a placa do veículo e o lucro bruto.
    Em seguida, ordena os registros pela data e cria uma identificação
    textual do veículo, combinando marca, modelo e placa.

    Parâmetros:
        df_vendas: DataFrame contendo os dados das vendas processadas.

    Retorno:
        DataFrame preparado para alimentar o gráfico de barras,
        contendo a identificação de cada veículo e seu lucro bruto.
    """
    df_lucro = df_vendas[["data", "placa_veiculo", "Lucro Bruto (R$)"]].sort_values("data")

    # Monta uma identificação única para facilitar a leitura do gráfico.
    df_lucro["Veículo"] = (
        df_vendas["marca"]
        + " "
        + df_vendas["modelo"]
        + " ("
        + df_vendas["placa_veiculo"]
        + ")"
    )

    return df_lucro


# ==========================================
# COMPONENTES DE INTERFACE
# ==========================================

def render_cabecalho():
    """
    Renderiza o cabeçalho principal do dashboard.

    Apresenta a logo da GiroCar e o título da aplicação.
    Também aplica um pequeno ajuste visual via CSS para alinhar
    a imagem da logo com o título.

    Caso a imagem não seja encontrada no caminho configurado,
    registra uma mensagem de erro no sistema de logs.
    """

    # CSS responsável pelo alinhamento vertical da logo.
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

    # Divide o cabeçalho em duas colunas para posicionar
    # a logo à esquerda e as informações à direita.
    col_logo, col_titulo = st.columns([1, 4], vertical_alignment="center")

    with col_logo:
        if LOGO_PATH.is_file():
            st.markdown('<div class="logo-girocar">', unsafe_allow_html=True)
            st.image(str(LOGO_PATH), width=180)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            logger.error("Logo não encontrada: %s", LOGO_PATH)

    with col_titulo:
        st.title("Dashboard de Veículos")
        st.write("Visão geral em tempo real do pátio e análise de lucratividade histórica.")


def render_estoque(qtd_disponivel, qtd_preparacao, capital_investido):
    """
    Exibe os indicadores referentes à posição atual do estoque.

    Apresenta três indicadores principais (KPIs):
        - Quantidade de veículos disponíveis para venda.
        - Quantidade de veículos que estão na fila de preparação.
        - Capital financeiro empenhado nos veículos em estoque.

    Parâmetros:
        qtd_disponivel: Quantidade de veículos disponíveis.
        qtd_preparacao: Quantidade de veículos em preparação.
        capital_investido: Soma dos valores de aquisição dos veículos
        disponíveis e em preparação.
    """

    st.markdown("### Posição Atual do Pátio")

    # Organiza os indicadores em três colunas.
    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(label="Veículos Disponíveis", value=f"{qtd_disponivel}")
    kpi2.metric(label="Fila da Oficina (Preparação)", value=f"{qtd_preparacao}")
    kpi3.metric(
        label="Capital Empenhado (Estoque)",
        value=f"R$ {formatar_moeda(capital_investido)}",
    )


def render_filtro_periodo(df_vendas):
    """
    Exibe o filtro de período para a análise histórica das vendas.

    Obtém os meses/anos existentes nos registros de vendas,
    organiza as opções em ordem decrescente e disponibiliza
    um seletor para filtrar os dados.

    Também disponibiliza a opção de visualizar todo o histórico.

    Parâmetros:
        df_vendas: DataFrame contendo as vendas processadas.

    Retorno:
        Tupla contendo:
        - DataFrame filtrado conforme o período selecionado.
        - Rótulo correspondente ao período selecionado.
    """

    col_filtro, _ = st.columns([1, 3])

    with col_filtro:
        # Recupera os períodos existentes e ordena do mais recente
        # para o mais antigo.
        meses_disponiveis = sorted(df_vendas["mes_ano"].unique(), reverse=True)

        mes_selecionado = st.selectbox(
            "Filtrar por Período:", [FILTRO_TODO_HISTORICO] + meses_disponiveis
        )

    # Aplica o filtro somente quando um mês específico é selecionado.
    if mes_selecionado != FILTRO_TODO_HISTORICO:
        df_vendas = df_vendas[df_vendas["mes_ano"] == mes_selecionado]

    return df_vendas, mes_selecionado


def render_vendas(df_transacoes, df_veiculos, qtd_preparacao, df_preparacao):
    """
    Renderiza a seção de análise de vendas e lucratividade.

    Responsável por:
        - Preparar os dados das vendas.
        - Disponibilizar o filtro por período.
        - Calcular o lucro bruto total do período selecionado.
        - Contabilizar a quantidade de veículos vendidos.
        - Preparar os dados para o gráfico de lucratividade.
        - Exibir os indicadores financeiros e de vendas.
        - Apresentar o gráfico de lucro por veículo.
        - Monitorar os veículos que estão em preparação na oficina.

    Parâmetros:
        df_transacoes: DataFrame contendo os registros de transações.
        df_veiculos: DataFrame contendo os dados dos veículos.
        qtd_preparacao: Quantidade de veículos em preparação.
        df_preparacao: DataFrame contendo os veículos em preparação.
    """

    st.markdown("### Análise de Vendas e Lucratividade")

    # Inicializa os valores padrão para os casos em que
    # não existam registros de vendas ou veículos.
    df_lucro = pd.DataFrame()
    lucro_periodo = 0.0
    qtd_vendida = 0
    rotulo_periodo = "Período"

    # Processa os dados somente quando existem transações e veículos.
    if not df_transacoes.empty and not df_veiculos.empty:
        df_vendas = preparar_vendas(df_transacoes, df_veiculos)
        df_vendas, rotulo_periodo = render_filtro_periodo(df_vendas)

        # Calcula os indicadores considerando o período selecionado.
        lucro_periodo = df_vendas["Lucro Bruto (R$)"].sum()
        qtd_vendida = len(df_vendas)

        # Prepara os dados que serão utilizados no gráfico.
        df_lucro = montar_dados_grafico(df_vendas)

    # ------------------------------------------
    # INDICADORES DE VENDAS
    # ------------------------------------------

    # Apresenta o lucro bruto e a quantidade de veículos vendidos
    # considerando os filtros aplicados.
    kpi_v1, kpi_v2 = st.columns(2)

    kpi_v1.metric(
        label=f"Lucro Bruto ({rotulo_periodo})",
        value=f"R$ {formatar_moeda(lucro_periodo)}",
    )
    kpi_v2.metric(label="Quantidade Vendida", value=f"{qtd_vendida} veículos")

    # ------------------------------------------
    # GRÁFICO E MONITORAMENTO DA OFICINA
    # ------------------------------------------

    # Divide a parte inferior da interface em duas áreas:
    # uma maior para o gráfico e outra para o monitoramento da oficina.
    col_grafico, col_oficina = st.columns([2, 1])

    with col_grafico:
        if not df_lucro.empty:
            # Exibe o lucro bruto individual de cada veículo vendido.
            st.bar_chart(
                df_lucro,
                x="Veículo",
                y="Lucro Bruto (R$)",
                color="#2ca02c",
                use_container_width=True,
            )
        else:
            st.info("Nenhuma venda registrada no período selecionado.")

    with col_oficina:
        st.write("**Monitoramento da Oficina**")

        if not df_veiculos.empty and qtd_preparacao > 0:
            # Seleciona e renomeia as colunas para apresentação
            # dos veículos que aguardam preparação.
            df_fila = df_preparacao[["placa", "marca", "modelo"]].rename(
                columns={"placa": "Placa", "marca": "Marca", "modelo": "Modelo"}
            )

            st.dataframe(df_fila, hide_index=True, use_container_width=True)
        else:
            st.success("Nenhum veículo em preparação. Pátio livre!")


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================

# Renderiza o cabeçalho antes das demais seções do dashboard.
render_cabecalho()

# Verifica se a conexão com o Supabase está disponível.
# Caso contrário, apresenta uma mensagem de erro e interrompe
# a execução da aplicação.
if not supabase:
    st.error("⚠️ Não foi possível estabelecer conexão com o banco de dados.")
    st.stop()

try:
    # Recupera os dados das tabelas de veículos e transações.
    df_veiculos, df_transacoes = carregar_dados()

    # Calcula os indicadores relacionados ao estoque atual.
    qtd_disponivel, qtd_preparacao, capital_investido, df_preparacao = calcular_estoque(df_veiculos)

    # Renderiza os indicadores de estoque.
    render_estoque(qtd_disponivel, qtd_preparacao, capital_investido)

    # Insere um divisor visual entre a posição do estoque
    # e a seção de análise de vendas.
    st.divider()

    # Renderiza os indicadores de vendas, gráfico de lucratividade
    # e monitoramento dos veículos em preparação.
    render_vendas(df_transacoes, df_veiculos, qtd_preparacao, df_preparacao)

except Exception as e:
    # Registra o erro completo, incluindo informações técnicas,
    # no sistema de logs para facilitar a identificação do problema.
    logger.exception("Erro ao calcular as métricas do painel")

    # Apresenta uma mensagem amigável ao usuário.
    st.error("⚠️ Erro ao calcular as métricas do painel.")

    # Disponibiliza os detalhes técnicos em uma seção expansível,
    # evitando exibir informações técnicas diretamente na interface principal.
    with st.expander("Detalhes Técnicos"):
        st.code(str(e))
