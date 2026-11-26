from unittest.mock import MagicMock
import pandas as pd

from components.dashboard import (
    cabecalho,
    filtro_periodo,
    grafico_lucratividade,
    kpis_estoque,
    kpis_vendas,
    monitoramento_oficina,
    portal_vendedor,
    secao_auditoria,
    tela_login,
)
from components.regras_negocio.constantes import FILTRO_TODO_HISTORICO


# --- CABEÇALHO ---
def test_render_cabecalho_com_logo(monkeypatch, mock_st, tmp_path):
    logo_falsa = tmp_path / "girocar.png"
    logo_falsa.write_bytes(b"fake")

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_falsa)

    cabecalho.render_cabecalho()

    mock_st.image.assert_called_once_with(str(logo_falsa), width=180)
    mock_st.title.assert_called_once_with("Dashboard de Veículos")


def test_render_cabecalho_sem_logo(monkeypatch, mock_st, tmp_path):
    logo_inexistente = tmp_path / "nao_existe.png"
    mock_logger = MagicMock()

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_inexistente)
    monkeypatch.setattr(cabecalho, "logger", mock_logger)

    cabecalho.render_cabecalho()

    mock_st.image.assert_not_called()
    mock_logger.error.assert_called_once()


# --- FILTRO PERÍODO ---
def test_filtro_periodo_todo_historico(monkeypatch, mock_st):
    df = pd.DataFrame([{"mes_ano": "05/2026"}, {"mes_ano": "04/2026"}])
    mock_st.selectbox.return_value = FILTRO_TODO_HISTORICO

    monkeypatch.setattr(filtro_periodo, "st", mock_st)

    df_res, mes = filtro_periodo.render_filtro_periodo(df)

    assert len(df_res) == 2
    assert mes == FILTRO_TODO_HISTORICO


def test_filtro_periodo_mes_especifico(monkeypatch, mock_st):
    df = pd.DataFrame([{"mes_ano": "05/2026"}, {"mes_ano": "04/2026"}])
    mock_st.selectbox.return_value = "05/2026"

    monkeypatch.setattr(filtro_periodo, "st", mock_st)

    df_res, mes = filtro_periodo.render_filtro_periodo(df)

    assert len(df_res) == 1
    assert mes == "05/2026"


# --- GRÁFICO LUCRATIVIDADE ---
def test_grafico_lucratividade_com_dados(monkeypatch, mock_st):
    df = pd.DataFrame([{"Veículo": "Civic", "Lucro Bruto (R$)": 12000.0}])
    monkeypatch.setattr(grafico_lucratividade, "st", mock_st)

    grafico_lucratividade.render_grafico_lucratividade(df)

    mock_st.bar_chart.assert_called_once()


def test_grafico_lucratividade_vazio(monkeypatch, mock_st):
    monkeypatch.setattr(grafico_lucratividade, "st", mock_st)

    grafico_lucratividade.render_grafico_lucratividade(pd.DataFrame())

    mock_st.info.assert_called_once_with("Nenhuma venda registrada no período selecionado.")


# --- KPIS ESTOQUE E VENDAS ---
def test_render_estoque(monkeypatch, mock_st):
    cols = [MagicMock(), MagicMock(), MagicMock()]
    mock_st.columns.side_effect = lambda spec, **kwargs: cols

    monkeypatch.setattr(kpis_estoque, "st", mock_st)

    kpis_estoque.render_estoque(10, 2, 500000.0)

    cols[0].metric.assert_called_once()
    cols[1].metric.assert_called_once()
    cols[2].metric.assert_called_once()


def test_render_kpis_vendas(monkeypatch, mock_st):
    cols = [MagicMock(), MagicMock()]
    mock_st.columns.side_effect = lambda spec, **kwargs: cols

    monkeypatch.setattr(kpis_vendas, "st", mock_st)

    kpis_vendas.render_kpis_vendas(45000.0, 3, "05/2026")

    cols[0].metric.assert_called_once()
    cols[1].metric.assert_called_once()


# --- MONITORAMENTO OFICINA ---
def test_monitoramento_oficina_com_veiculos(monkeypatch, mock_st):
    df_veiculos = pd.DataFrame([{"placa": "ABC1D23"}])
    df_preparacao = pd.DataFrame([{"placa": "ABC1D23", "marca": "Honda", "modelo": "Civic"}])

    monkeypatch.setattr(monitoramento_oficina, "st", mock_st)

    monitoramento_oficina.render_monitoramento_oficina(df_veiculos, 1, df_preparacao)

    mock_st.dataframe.assert_called_once()


def test_monitoramento_oficina_vazio(monkeypatch, mock_st):
    monkeypatch.setattr(monitoramento_oficina, "st", mock_st)

    monitoramento_oficina.render_monitoramento_oficina(pd.DataFrame(), 0, pd.DataFrame())

    mock_st.success.assert_called_once_with("Nenhum veículo em preparação. Pátio livre!")


# --- PORTAL VENDEDOR ---
def test_portal_vendedor_sem_cliques(monkeypatch, mock_st):
    mock_st.button.return_value = False
    monkeypatch.setattr(portal_vendedor, "st", mock_st)

    portal_vendedor.render_portal_vendedor()

    mock_st.warning.assert_called_once()
    mock_st.switch_page.assert_not_called()


def test_portal_vendedor_com_cliques(monkeypatch, mock_st):
    mock_st.button.side_effect = [True, True, True]
    monkeypatch.setattr(portal_vendedor, "st", mock_st)

    portal_vendedor.render_portal_vendedor()

    assert mock_st.switch_page.call_count == 3


# --- SEÇÃO AUDITORIA ---
def test_secao_auditoria_com_dados(monkeypatch, mock_st):
    df = pd.DataFrame([{"id": 1, "placa": "ABC1D23"}])
    monkeypatch.setattr(secao_auditoria, "st", mock_st)
    monkeypatch.setattr(secao_auditoria, "obter_dados_auditoria", lambda: df)

    secao_auditoria.render_secao_auditoria()

    mock_st.dataframe.assert_called_once()


def test_secao_auditoria_vazia(monkeypatch, mock_st):
    monkeypatch.setattr(secao_auditoria, "st", mock_st)
    monkeypatch.setattr(secao_auditoria, "obter_dados_auditoria", lambda: pd.DataFrame())

    secao_auditoria.render_secao_auditoria()

    mock_st.info.assert_called_once_with("Nenhuma transação registrada para auditoria.")


def test_secao_auditoria_erro(monkeypatch, mock_st):
    def _erro():
        raise RuntimeError("falha auditoria")

    monkeypatch.setattr(secao_auditoria, "st", mock_st)
    monkeypatch.setattr(secao_auditoria, "obter_dados_auditoria", _erro)

    secao_auditoria.render_secao_auditoria()

    mock_st.error.assert_called_once()


# --- TELA LOGIN ---
def test_tela_login_com_logo_sem_submit(monkeypatch, mock_st, tmp_path):
    logo_falsa = tmp_path / "girocar.png"
    logo_falsa.write_bytes(b"fake")
    mock_st.text_input.side_effect = ["", ""]
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(tela_login, "st", mock_st)

    tela_login.render_tela_login(logo_falsa)

    mock_st.image.assert_called_once_with(str(logo_falsa), width=220)
    mock_st.warning.assert_not_called()


def test_tela_login_campos_vazios(monkeypatch, mock_st, tmp_path):
    logo_inexistente = tmp_path / "nao_existe.png"
    mock_st.text_input.side_effect = ["   ", ""]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(tela_login, "st", mock_st)

    tela_login.render_tela_login(logo_inexistente)

    mock_st.warning.assert_called_once_with("Preencha todos os campos.")


def test_tela_login_gerente_sucesso(monkeypatch, mock_st, tmp_path):
    mock_st.text_input.side_effect = ["gerente@girocar.com", "123"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(tela_login, "st", mock_st)
    monkeypatch.setattr(tela_login, "CREDENCIAIS_GERENTES", {"gerente@girocar.com": "123"})
    monkeypatch.setattr(tela_login, "autenticar_gerente", lambda u, s: (True, u, "Bem-vindo!"))

    tela_login.render_tela_login(tmp_path / "x.png")

    assert mock_st.session_state["autenticado"] is True
    assert mock_st.session_state["perfil_usuario"] == "Gerente"
    mock_st.success.assert_called_once_with("Bem-vindo!")
    mock_st.rerun.assert_called_once()


def test_tela_login_gerente_falha(monkeypatch, mock_st, tmp_path):
    mock_st.text_input.side_effect = ["gerente@girocar.com", "errada"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(tela_login, "st", mock_st)
    monkeypatch.setattr(tela_login, "CREDENCIAIS_GERENTES", {"gerente@girocar.com": "123"})
    monkeypatch.setattr(tela_login, "autenticar_gerente", lambda u, s: (False, None, "Senha inválida"))

    tela_login.render_tela_login(tmp_path / "x.png")

    mock_st.error.assert_called_once_with("Senha inválida")


def test_tela_login_vendedor_sucesso(monkeypatch, mock_st, tmp_path):
    mock_st.text_input.side_effect = ["joao", "123"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(tela_login, "st", mock_st)
    monkeypatch.setattr(tela_login, "CREDENCIAIS_GERENTES", {})
    monkeypatch.setattr(tela_login, "autenticar_vendedor", lambda u, s: (True, "joao", "Login OK"))

    tela_login.render_tela_login(tmp_path / "x.png")

    assert mock_st.session_state["autenticado"] is True
    assert mock_st.session_state["perfil_usuario"] == "Vendedor"
    mock_st.success.assert_called_once_with("Login OK")
    mock_st.rerun.assert_called_once()


def test_tela_login_vendedor_falha(monkeypatch, mock_st, tmp_path):
    mock_st.text_input.side_effect = ["joao", "errada"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(tela_login, "st", mock_st)
    monkeypatch.setattr(tela_login, "CREDENCIAIS_GERENTES", {})
    monkeypatch.setattr(tela_login, "autenticar_vendedor", lambda u, s: (False, None, "Credenciais inválidas"))

    tela_login.render_tela_login(tmp_path / "x.png")

    mock_st.error.assert_called_once_with("Credenciais inválidas")


def test_tela_login_vendedor_erro_banco(monkeypatch, mock_st, tmp_path):
    def _erro(u, s):
        raise RuntimeError("sem conexao")

    mock_st.text_input.side_effect = ["joao", "123"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(tela_login, "st", mock_st)
    monkeypatch.setattr(tela_login, "CREDENCIAIS_GERENTES", {})
    monkeypatch.setattr(tela_login, "autenticar_vendedor", _erro)

    tela_login.render_tela_login(tmp_path / "x.png")

    mock_st.error.assert_called_once()