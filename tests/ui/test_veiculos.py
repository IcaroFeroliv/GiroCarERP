from unittest.mock import MagicMock
import pandas as pd

from components.veiculos import (
    aba_cadastro,
    aba_consulta,
    aba_fipe,
    aba_historico,
    acoes_rapidas,
    cabecalho,
    filtros_veiculos,
    resultado_fipe,
    tabela_veiculos,
    vinculo_fipe,
)


# --- CABEÇALHO ---
def test_render_cabecalho_com_logo(monkeypatch, mock_st, tmp_path):
    logo_falsa = tmp_path / "girocar.png"
    logo_falsa.write_bytes(b"fake")

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_falsa)

    cabecalho.render_cabecalho()

    mock_st.image.assert_called_once_with(str(logo_falsa), width=180)
    mock_st.title.assert_called_once_with("Gestão de Veículos")


def test_render_cabecalho_sem_logo(monkeypatch, mock_st, tmp_path):
    logo_inexistente = tmp_path / "nao_existe.png"
    mock_logger = MagicMock()

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_inexistente)
    monkeypatch.setattr(cabecalho, "logger", mock_logger)

    cabecalho.render_cabecalho()

    mock_st.image.assert_not_called()
    mock_logger.error.assert_called_once()


# --- FILTROS VEÍCULOS ---
def test_render_filtros_veiculos(monkeypatch, mock_st):
    df = pd.DataFrame([
        {"placa": "ABC1D23", "status_veiculo": "Disponivel", "marca": "Honda"},
        {"placa": "XYZ9K88", "status_veiculo": "Vendido", "marca": "Toyota"},
    ])
    mock_st.text_input.return_value = "abc"
    mock_st.multiselect.side_effect = [["Disponivel"], ["Honda"]]

    monkeypatch.setattr(filtros_veiculos, "st", mock_st)

    df_res = filtros_veiculos.render_filtros_veiculos(df)

    assert len(df_res) == 1
    assert df_res.iloc[0]["placa"] == "ABC1D23"


# --- TABELA VEÍCULOS ---
def test_render_tabela_veiculos(monkeypatch, mock_st):
    df = pd.DataFrame([
        {
            "placa": "ABC1D23",
            "chassi": "9BWZZZ377VT004251",
            "marca": "Honda",
            "modelo": "Civic",
            "ano_fabricacao": 2023,
            "ano_modelo": 2024,
            "cor": "Preto",
            "quilometragem": 15000,
            "valor_aquisicao": 95000.0,
            "status_veiculo": "Disponivel",
            "indicador_leilao": False,
            "indicador_sinistro": False,
            "cnpj_loja": "12345678000199",
            "cnpj_cpf_fornecedor": "98765432000188",
        }
    ])

    monkeypatch.setattr(tabela_veiculos, "st", mock_st)

    tabela_veiculos.render_tabela_veiculos(df)

    mock_st.dataframe.assert_called_once()


# --- AÇÕES RÁPIDAS ---
def test_acoes_rapidas_sem_cliques(monkeypatch, mock_st):
    df = pd.DataFrame([{"placa": "ABC1D23"}])
    mock_st.selectbox.side_effect = ["ABC1D23", "Disponivel", "ABC1D23"]
    mock_st.button.side_effect = [False, False]

    monkeypatch.setattr(acoes_rapidas, "st", mock_st)

    acoes_rapidas.render_acoes_rapidas(df)

    mock_st.success.assert_not_called()
    mock_st.error.assert_not_called()


def test_acoes_rapidas_atualizar_status(monkeypatch, mock_st):
    df = pd.DataFrame([{"placa": "ABC1D23"}])
    mock_sb = MagicMock()
    mock_st.selectbox.side_effect = ["ABC1D23", "Vendido", "ABC1D23"]
    mock_st.button.side_effect = [True, False]

    monkeypatch.setattr(acoes_rapidas, "st", mock_st)
    monkeypatch.setattr(acoes_rapidas, "supabase", mock_sb)

    acoes_rapidas.render_acoes_rapidas(df)

    mock_sb.table.assert_called_once_with("veiculo")
    mock_st.success.assert_called_once_with("Status da placa ABC1D23 atualizado para Vendido!")
    mock_st.rerun.assert_called_once()


def test_acoes_rapidas_excluir_sucesso(monkeypatch, mock_st):
    df = pd.DataFrame([{"placa": "ABC1D23"}])
    mock_sb = MagicMock()
    mock_st.selectbox.side_effect = ["ABC1D23", "Disponivel", "ABC1D23"]
    mock_st.button.side_effect = [False, True]

    monkeypatch.setattr(acoes_rapidas, "st", mock_st)
    monkeypatch.setattr(acoes_rapidas, "supabase", mock_sb)

    acoes_rapidas.render_acoes_rapidas(df)

    mock_st.success.assert_called_once_with("Veículo ABC1D23 excluído com sucesso!")
    mock_st.rerun.assert_called_once()


def test_acoes_rapidas_excluir_erro(monkeypatch, mock_st):
    df = pd.DataFrame([{"placa": "ABC1D23"}])
    mock_sb = MagicMock()
    mock_sb.table.return_value.delete.return_value.eq.return_value.execute.side_effect = RuntimeError("FK")
    mock_st.selectbox.side_effect = ["ABC1D23", "Disponivel", "ABC1D23"]
    mock_st.button.side_effect = [False, True]

    monkeypatch.setattr(acoes_rapidas, "st", mock_st)
    monkeypatch.setattr(acoes_rapidas, "supabase", mock_sb)

    acoes_rapidas.render_acoes_rapidas(df)

    mock_st.error.assert_called_once()


# --- ABA CONSULTA ---
def test_aba_consulta_vazia(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = []

    monkeypatch.setattr(aba_consulta, "st", mock_st)
    monkeypatch.setattr(aba_consulta, "supabase", mock_sb)

    aba_consulta.render_aba_consulta()

    mock_st.info.assert_called_once_with("Nenhum veículo cadastrado no sistema.")


def test_aba_consulta_com_dados(monkeypatch, mock_st):
    df = pd.DataFrame([{"placa": "ABC1D23"}])
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [{"placa": "ABC1D23"}]
    mock_tabela = MagicMock()
    mock_acoes = MagicMock()

    monkeypatch.setattr(aba_consulta, "st", mock_st)
    monkeypatch.setattr(aba_consulta, "supabase", mock_sb)
    monkeypatch.setattr(aba_consulta, "render_filtros_veiculos", lambda _: df)
    monkeypatch.setattr(aba_consulta, "render_tabela_veiculos", mock_tabela)
    monkeypatch.setattr(aba_consulta, "render_acoes_rapidas", mock_acoes)

    aba_consulta.render_aba_consulta()

    mock_tabela.assert_called_once()
    mock_acoes.assert_called_once()


def test_aba_consulta_filtro_sem_resultado(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [{"placa": "ABC1D23"}]
    mock_tabela = MagicMock()
    mock_acoes = MagicMock()

    monkeypatch.setattr(aba_consulta, "st", mock_st)
    monkeypatch.setattr(aba_consulta, "supabase", mock_sb)
    monkeypatch.setattr(aba_consulta, "render_filtros_veiculos", lambda _: pd.DataFrame())
    monkeypatch.setattr(aba_consulta, "render_tabela_veiculos", mock_tabela)
    monkeypatch.setattr(aba_consulta, "render_acoes_rapidas", mock_acoes)

    aba_consulta.render_aba_consulta()

    mock_acoes.assert_not_called()
    mock_st.warning.assert_called_once_with("Nenhum veículo encontrado com os filtros aplicados.")


def test_aba_consulta_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.side_effect = RuntimeError("sem conexao")
    mock_detalhes = MagicMock()

    monkeypatch.setattr(aba_consulta, "st", mock_st)
    monkeypatch.setattr(aba_consulta, "supabase", mock_sb)
    monkeypatch.setattr(aba_consulta, "mostrar_detalhes_tecnicos", mock_detalhes)

    aba_consulta.render_aba_consulta()

    mock_st.error.assert_called_once_with(aba_consulta.MSG_ERRO_CONEXAO)
    mock_detalhes.assert_called_once()


# --- ABA CADASTRO ---
def _mock_supabase_cadastro(lojas, fornecedores, erro=False):
    mock_sb = MagicMock()

    def table_side_effect(nome):
        if erro:
            raise RuntimeError("falha banco")
        tbl = MagicMock()
        if nome == "loja":
            tbl.select.return_value.execute.return_value.data = lojas
        elif nome == "fornecedor":
            tbl.select.return_value.execute.return_value.data = fornecedores
        return tbl

    mock_sb.table.side_effect = table_side_effect
    return mock_sb


def test_aba_cadastro_sem_lojas_e_submit(monkeypatch, mock_st):
    mock_sb = _mock_supabase_cadastro([], [])
    mock_st.text_input.side_effect = ["ABC1D23", "12345678901234567", "Honda", "Civic", "Preto"]
    mock_st.number_input.side_effect = [2024, 2024, 0, 80000.0]
    mock_st.selectbox.side_effect = ["Disponivel", "-- Cadastre uma Loja --", "-- Cadastre um Fornecedor --"]
    mock_st.checkbox.side_effect = [False, False]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(aba_cadastro, "st", mock_st)
    monkeypatch.setattr(aba_cadastro, "supabase", mock_sb)

    aba_cadastro.render_aba_cadastro()

    mock_st.warning.assert_called_once()
    mock_st.error.assert_called_once()


def test_aba_cadastro_sem_submit(monkeypatch, mock_st):
    lojas = [{"cnpj": "123", "nome_unidade": "Matriz"}]
    fornecedores = [{"cnpj_cpf": "456", "nome_razao_social": "Forn A"}]
    mock_sb = _mock_supabase_cadastro(lojas, fornecedores)
    mock_st.text_input.side_effect = ["", "", "", "", ""]
    mock_st.number_input.side_effect = [2024, 2024, 0, 0.0]
    mock_st.selectbox.side_effect = ["Disponivel", "123 - Matriz", "456 - Forn A"]
    mock_st.checkbox.side_effect = [False, False]
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(aba_cadastro, "st", mock_st)
    monkeypatch.setattr(aba_cadastro, "supabase", mock_sb)

    aba_cadastro.render_aba_cadastro()

    mock_st.success.assert_not_called()
    mock_st.warning.assert_not_called()


def test_aba_cadastro_campos_obrigatorios(monkeypatch, mock_st):
    lojas = [{"cnpj": "123", "nome_unidade": "Matriz"}]
    fornecedores = [{"cnpj_cpf": "456", "nome_razao_social": "Forn A"}]
    mock_sb = _mock_supabase_cadastro(lojas, fornecedores)
    mock_st.text_input.side_effect = ["", "CHASSI", "Honda", "Civic", "Preto"]
    mock_st.number_input.side_effect = [2024, 2024, 0, 80000.0]
    mock_st.selectbox.side_effect = ["Disponivel", "123 - Matriz", "456 - Forn A"]
    mock_st.checkbox.side_effect = [False, False]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(aba_cadastro, "st", mock_st)
    monkeypatch.setattr(aba_cadastro, "supabase", mock_sb)

    aba_cadastro.render_aba_cadastro()

    mock_st.warning.assert_called_once()


def test_aba_cadastro_sucesso(monkeypatch, mock_st):
    lojas = [{"cnpj": "123", "nome_unidade": "Matriz"}]
    fornecedores = [{"cnpj_cpf": "456", "nome_razao_social": "Forn A"}]
    mock_sb = _mock_supabase_cadastro(lojas, fornecedores)
    mock_st.text_input.side_effect = ["abc1d23", "9bwzzz377vt004251", "Honda", "Civic", "Preto"]
    mock_st.number_input.side_effect = [2024, 2024, 10000, 95000.0]
    mock_st.selectbox.side_effect = ["Disponivel", "123 - Matriz", "456 - Forn A"]
    mock_st.checkbox.side_effect = [False, True]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(aba_cadastro, "st", mock_st)
    monkeypatch.setattr(aba_cadastro, "supabase", mock_sb)

    aba_cadastro.render_aba_cadastro()

    mock_st.success.assert_called_once()


def test_aba_cadastro_erro_banco(monkeypatch, mock_st):
    mock_sb = _mock_supabase_cadastro([], [], erro=True)
    mock_detalhes = MagicMock()

    monkeypatch.setattr(aba_cadastro, "st", mock_st)
    monkeypatch.setattr(aba_cadastro, "supabase", mock_sb)
    monkeypatch.setattr(aba_cadastro, "mostrar_detalhes_tecnicos", mock_detalhes)

    aba_cadastro.render_aba_cadastro()

    mock_st.error.assert_called_once()
    mock_detalhes.assert_called_once()


# --- ABA FIPE ---
def test_aba_fipe_marca_nao_selecionada(monkeypatch, mock_st):
    mock_st.selectbox.return_value = aba_fipe.FIPE_SELECIONE
    mock_resultado = MagicMock()

    monkeypatch.setattr(aba_fipe, "st", mock_st)
    monkeypatch.setattr(aba_fipe, "get_marcas", lambda: [])
    monkeypatch.setattr(aba_fipe, "render_resultado_fipe", mock_resultado)

    aba_fipe.render_aba_fipe()

    mock_resultado.assert_not_called()


def test_aba_fipe_modelo_nao_selecionado(monkeypatch, mock_st):
    mock_st.selectbox.side_effect = ["Honda", aba_fipe.FIPE_SELECIONE]
    mock_resultado = MagicMock()

    monkeypatch.setattr(aba_fipe, "st", mock_st)
    monkeypatch.setattr(aba_fipe, "get_marcas", lambda: [{"nome": "Honda", "codigo": "25"}])
    monkeypatch.setattr(aba_fipe, "get_modelos", lambda cod: [{"nome": "Civic", "codigo": "100"}])
    monkeypatch.setattr(aba_fipe, "render_resultado_fipe", mock_resultado)

    aba_fipe.render_aba_fipe()

    mock_resultado.assert_not_called()


def test_aba_fipe_ano_nao_selecionado(monkeypatch, mock_st):
    mock_st.selectbox.side_effect = ["Honda", "Civic", aba_fipe.FIPE_SELECIONE]
    mock_resultado = MagicMock()

    monkeypatch.setattr(aba_fipe, "st", mock_st)
    monkeypatch.setattr(aba_fipe, "get_marcas", lambda: [{"nome": "Honda", "codigo": "25"}])
    monkeypatch.setattr(aba_fipe, "get_modelos", lambda cod: [{"nome": "Civic", "codigo": "100"}])
    monkeypatch.setattr(aba_fipe, "get_anos", lambda m, mod: [{"nome": "2024 Gasolina", "codigo": "2024-1"}])
    monkeypatch.setattr(aba_fipe, "render_resultado_fipe", mock_resultado)

    aba_fipe.render_aba_fipe()

    mock_resultado.assert_not_called()


def test_aba_fipe_completo(monkeypatch, mock_st):
    mock_st.selectbox.side_effect = ["Honda", "Civic", "2024 Gasolina"]
    mock_resultado = MagicMock()

    monkeypatch.setattr(aba_fipe, "st", mock_st)
    monkeypatch.setattr(aba_fipe, "get_marcas", lambda: [{"nome": "Honda", "codigo": "25"}])
    monkeypatch.setattr(aba_fipe, "get_modelos", lambda cod: [{"nome": "Civic", "codigo": "100"}])
    monkeypatch.setattr(aba_fipe, "get_anos", lambda m, mod: [{"nome": "2024 Gasolina", "codigo": "2024-1"}])
    monkeypatch.setattr(aba_fipe, "render_resultado_fipe", mock_resultado)

    aba_fipe.render_aba_fipe()

    mock_resultado.assert_called_once_with("25", "100", "2024-1")


# --- RESULTADO FIPE ---
def test_resultado_fipe_sucesso(monkeypatch, mock_st):
    cols = [MagicMock(), MagicMock(), MagicMock()]
    mock_st.columns.side_effect = lambda spec, **kwargs: cols

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "Valor": "R$ 120.000,00",
        "MesReferencia": "novembro de 2026",
        "CodigoFipe": "014001-0",
    }
    mock_vinculo = MagicMock()

    monkeypatch.setattr(resultado_fipe, "st", mock_st)
    monkeypatch.setattr(resultado_fipe.requests, "get", lambda *args, **kwargs: mock_resp)
    monkeypatch.setattr(resultado_fipe, "render_vinculo_fipe", mock_vinculo)

    resultado_fipe.render_resultado_fipe("25", "100", "2024-1")

    cols[0].metric.assert_called_once_with("Valor de Mercado", "R$ 120.000,00")
    mock_vinculo.assert_called_once_with("R$ 120.000,00")


def test_resultado_fipe_status_diferente_200(monkeypatch, mock_st):
    mock_resp = MagicMock()
    mock_resp.status_code = 500

    monkeypatch.setattr(resultado_fipe, "st", mock_st)
    monkeypatch.setattr(resultado_fipe.requests, "get", lambda *args, **kwargs: mock_resp)

    resultado_fipe.render_resultado_fipe("25", "100", "2024-1")

    mock_st.error.assert_called_once_with("Falha ao comunicar com o servidor da Tabela FIPE.")


def test_resultado_fipe_excecao(monkeypatch, mock_st):
    mock_detalhes = MagicMock()

    def _erro(*args, **kwargs):
        raise RuntimeError("timeout")

    monkeypatch.setattr(resultado_fipe, "st", mock_st)
    monkeypatch.setattr(resultado_fipe.requests, "get", _erro)
    monkeypatch.setattr(resultado_fipe, "mostrar_detalhes_tecnicos", mock_detalhes)

    resultado_fipe.render_resultado_fipe("25", "100", "2024-1")

    mock_st.error.assert_called_once_with("Erro técnico ao realizar a consulta final.")
    mock_detalhes.assert_called_once()


# --- VÍNCULO FIPE ---
def test_vinculo_fipe_sem_submit(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"placa": "ABC1D23", "marca": "Honda", "modelo": "Civic"}
    ]
    mock_st.selectbox.return_value = vinculo_fipe.FIPE_NAO_VINCULAR
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(vinculo_fipe, "st", mock_st)
    monkeypatch.setattr(vinculo_fipe, "supabase", mock_sb)

    vinculo_fipe.render_vinculo_fipe("R$ 120.000,00")

    mock_st.warning.assert_not_called()
    mock_st.success.assert_not_called()


def test_vinculo_fipe_nao_vincular(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = []
    mock_st.selectbox.return_value = vinculo_fipe.FIPE_NAO_VINCULAR
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(vinculo_fipe, "st", mock_st)
    monkeypatch.setattr(vinculo_fipe, "supabase", mock_sb)

    vinculo_fipe.render_vinculo_fipe("R$ 120.000,00")

    mock_st.warning.assert_called_once_with("Nenhum veículo selecionado. O histórico não foi salvo.")


def test_vinculo_fipe_sucesso(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"placa": "ABC1D23", "marca": "Honda", "modelo": "Civic"}
    ]
    mock_st.selectbox.return_value = "ABC1D23 - Honda Civic"
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(vinculo_fipe, "st", mock_st)
    monkeypatch.setattr(vinculo_fipe, "supabase", mock_sb)

    vinculo_fipe.render_vinculo_fipe("R$ 120.000,00")

    mock_st.success.assert_called_once()


# --- ABA HISTÓRICO ---
def test_aba_historico_vazio(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.order.return_value.execute.return_value.data = []

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)

    aba_historico.render_aba_historico()

    mock_st.info.assert_called_once_with("Nenhuma avaliação foi salva no histórico até o momento.")


def test_aba_historico_com_dados(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.order.return_value.execute.return_value.data = [
        {
            "placa_veiculo": "ABC1D23",
            "mes_ano_referencia": "2026-11",
            "valor_api": 120000.0,
            "data_consulta": "2026-11-25",
        }
    ]
    mock_st.text_input.return_value = "abc"
    mock_st.multiselect.side_effect = [["2026-11"], ["2026-11-25"]]

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)

    aba_historico.render_aba_historico()

    mock_st.dataframe.assert_called_once()


def test_aba_historico_filtro_sem_resultado(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.order.return_value.execute.return_value.data = [
        {
            "placa_veiculo": "ABC1D23",
            "mes_ano_referencia": "2026-11",
            "valor_api": 120000.0,
            "data_consulta": "2026-11-25",
        }
    ]
    mock_st.text_input.return_value = "INEXISTENTE"
    mock_st.multiselect.side_effect = [[], []]

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)

    aba_historico.render_aba_historico()

    mock_st.warning.assert_called_once_with("Nenhum registro encontrado com os filtros aplicados.")


def test_aba_historico_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.side_effect = RuntimeError("falha")
    mock_detalhes = MagicMock()

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)
    monkeypatch.setattr(aba_historico, "mostrar_detalhes_tecnicos", mock_detalhes)

    aba_historico.render_aba_historico()

    mock_st.error.assert_called_once_with("Erro ao carregar o histórico de avaliações.")
    mock_detalhes.assert_called_once()