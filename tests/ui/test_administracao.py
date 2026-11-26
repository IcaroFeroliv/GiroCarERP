from datetime import date
from unittest.mock import MagicMock
import pytest

from components.administracao import (
    aba_funcionarios,
    aba_lojas,
    cabecalho,
    consulta_funcionario,
    consulta_loja,
    form_funcionario,
    form_loja,
)


# --- ABAS ---
def test_render_aba_funcionarios(monkeypatch, mock_st):
    mock_form = MagicMock()
    mock_consulta = MagicMock()

    monkeypatch.setattr(aba_funcionarios, "st", mock_st)
    monkeypatch.setattr(aba_funcionarios, "render_form_funcionario", mock_form)
    monkeypatch.setattr(aba_funcionarios, "render_consulta_funcionario", mock_consulta)

    aba_funcionarios.render_aba_funcionarios()

    mock_st.subheader.assert_called_once_with("Cadastro de Funcionário")
    mock_form.assert_called_once()
    mock_st.divider.assert_called_once()
    mock_consulta.assert_called_once()


def test_render_aba_lojas(monkeypatch, mock_st):
    mock_form = MagicMock()
    mock_consulta = MagicMock()

    monkeypatch.setattr(aba_lojas, "st", mock_st)
    monkeypatch.setattr(aba_lojas, "render_form_loja", mock_form)
    monkeypatch.setattr(aba_lojas, "render_consulta_loja", mock_consulta)

    aba_lojas.render_aba_lojas()

    mock_st.subheader.assert_called_once_with("Cadastro de Loja")
    mock_form.assert_called_once()
    mock_st.divider.assert_called_once()
    mock_consulta.assert_called_once()


# --- CABEÇALHO ---
def test_render_cabecalho_com_logo(monkeypatch, mock_st, tmp_path):
    logo_falsa = tmp_path / "girocar.png"
    logo_falsa.write_bytes(b"fake")

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_falsa)

    cabecalho.render_cabecalho()

    mock_st.image.assert_called_once_with(str(logo_falsa), width=180)
    mock_st.title.assert_called_once_with("Administração (RH e Filiais)")


def test_render_cabecalho_sem_logo(monkeypatch, mock_st, tmp_path):
    logo_inexistente = tmp_path / "nao_existe.png"
    mock_logger = MagicMock()

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_inexistente)
    monkeypatch.setattr(cabecalho, "logger", mock_logger)

    cabecalho.render_cabecalho()

    mock_st.image.assert_not_called()
    mock_logger.error.assert_called_once()


# --- CONSULTA FUNCIONÁRIO ---
def test_consulta_funcionario_vazio(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = []

    monkeypatch.setattr(consulta_funcionario, "st", mock_st)
    monkeypatch.setattr(consulta_funcionario, "supabase", mock_sb)

    consulta_funcionario.render_consulta_funcionario()

    mock_st.info.assert_called_once_with("Nenhum funcionário cadastrado.")


def test_consulta_funcionario_com_dados_e_filtro_cargo(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {
            "matricula": "001",
            "nome": "Ana",
            "cargo_nivel_acesso": "Gerente",
            "cnpj_loja": "12345678000199",
            "data_admissao": "2026-01-10",
        },
        {
            "matricula": "002",
            "nome": "Bruno",
            "cargo_nivel_acesso": "Vendedor",
            "cnpj_loja": "12345678000199",
            "data_admissao": "2026-02-10",
        },
    ]
    mock_st.selectbox.return_value = "Gerente"
    mock_st.text_input.return_value = "Ana"

    monkeypatch.setattr(consulta_funcionario, "st", mock_st)
    monkeypatch.setattr(consulta_funcionario, "supabase", mock_sb)

    consulta_funcionario.render_consulta_funcionario()

    mock_st.dataframe.assert_called_once()
    mock_st.caption.assert_called_once_with("1 funcionário(s) encontrado(s)")


def test_consulta_funcionario_sem_coluna_cargo_e_sem_resultado(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"matricula": "001", "nome": "Ana", "cnpj_loja": "12345678000199", "data_admissao": "2026-01-10"}
    ]
    mock_st.text_input.return_value = "Inexistente"

    monkeypatch.setattr(consulta_funcionario, "st", mock_st)
    monkeypatch.setattr(consulta_funcionario, "supabase", mock_sb)

    consulta_funcionario.render_consulta_funcionario()

    mock_st.info.assert_called_once_with("Nenhum funcionário corresponde à sua pesquisa.")


def test_consulta_funcionario_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.side_effect = RuntimeError("erro banco")

    monkeypatch.setattr(consulta_funcionario, "st", mock_st)
    monkeypatch.setattr(consulta_funcionario, "supabase", mock_sb)

    consulta_funcionario.render_consulta_funcionario()

    mock_st.error.assert_called_once()


# --- CONSULTA LOJA ---
def test_consulta_loja_vazio(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = []

    monkeypatch.setattr(consulta_loja, "st", mock_st)
    monkeypatch.setattr(consulta_loja, "supabase", mock_sb)

    consulta_loja.render_consulta_loja()

    mock_st.info.assert_called_once_with("Nenhuma loja cadastrada.")


def test_consulta_loja_com_dados(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"cnpj": "12345678000199", "nome_unidade": "Matriz BH", "endereco": "Av. Afonso Pena"}
    ]
    mock_st.text_input.return_value = "Matriz"

    monkeypatch.setattr(consulta_loja, "st", mock_st)
    monkeypatch.setattr(consulta_loja, "supabase", mock_sb)

    consulta_loja.render_consulta_loja()

    mock_st.dataframe.assert_called_once()
    mock_st.caption.assert_called_once_with("1 unidade(s) encontrada(s)")


def test_consulta_loja_pesquisa_sem_resultado(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"cnpj": "12345678000199", "nome_unidade": "Matriz BH", "endereco": "Av. Afonso Pena"}
    ]
    mock_st.text_input.return_value = "Filial X"

    monkeypatch.setattr(consulta_loja, "st", mock_st)
    monkeypatch.setattr(consulta_loja, "supabase", mock_sb)

    consulta_loja.render_consulta_loja()

    mock_st.info.assert_called_once_with("Nenhuma loja corresponde à sua pesquisa.")


def test_consulta_loja_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.side_effect = RuntimeError("erro banco")

    monkeypatch.setattr(consulta_loja, "st", mock_st)
    monkeypatch.setattr(consulta_loja, "supabase", mock_sb)

    consulta_loja.render_consulta_loja()

    mock_st.error.assert_called_once()


# --- FORM FUNCIONÁRIO ---
def test_form_funcionario_sem_submit(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["", "", ""]
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(form_funcionario, "st", mock_st)

    form_funcionario.render_form_funcionario()

    mock_st.warning.assert_not_called()
    mock_st.success.assert_not_called()


def test_form_funcionario_campos_obrigatorios(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["", "João", "123"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_funcionario, "st", mock_st)

    form_funcionario.render_form_funcionario()

    mock_st.warning.assert_called_once()


def test_form_funcionario_cnpj_invalido(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["001", "João", "000"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_funcionario, "st", mock_st)
    monkeypatch.setattr(form_funcionario, "limpar_e_validar_documento", lambda _: False)

    form_funcionario.render_form_funcionario()

    mock_st.error.assert_called_once_with("O CNPJ da Loja vinculada é inválido.")


def test_form_funcionario_sucesso(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_st.text_input.side_effect = ["001", "João", "12345678000199"]
    mock_st.selectbox.return_value = "Vendedor"
    mock_st.date_input.return_value = date(2026, 5, 1)
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_funcionario, "st", mock_st)
    monkeypatch.setattr(form_funcionario, "supabase", mock_sb)
    monkeypatch.setattr(form_funcionario, "limpar_e_validar_documento", lambda _: True)

    form_funcionario.render_form_funcionario()

    mock_sb.table.assert_called_once_with("funcionario")
    mock_st.success.assert_called_once_with("Funcionário cadastrado com sucesso!")


def test_form_funcionario_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.side_effect = RuntimeError("falha")
    mock_st.text_input.side_effect = ["001", "João", "12345678000199"]
    mock_st.selectbox.return_value = "Vendedor"
    mock_st.date_input.return_value = date(2026, 5, 1)
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_funcionario, "st", mock_st)
    monkeypatch.setattr(form_funcionario, "supabase", mock_sb)
    monkeypatch.setattr(form_funcionario, "limpar_e_validar_documento", lambda _: True)

    form_funcionario.render_form_funcionario()

    mock_st.error.assert_called_once()


# --- FORM LOJA ---
def test_form_loja_sem_submit(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["", "", ""]
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(form_loja, "st", mock_st)

    form_loja.render_form_loja()

    mock_st.warning.assert_not_called()
    mock_st.success.assert_not_called()


def test_form_loja_campos_obrigatorios(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["", "Matriz", "Rua A"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_loja, "st", mock_st)

    form_loja.render_form_loja()

    mock_st.warning.assert_called_once()


def test_form_loja_cnpj_invalido(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["000", "Matriz", "Rua A"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_loja, "st", mock_st)
    monkeypatch.setattr(form_loja, "limpar_e_validar_documento", lambda _: False)

    form_loja.render_form_loja()

    mock_st.error.assert_called_once_with("CNPJ inválido. Verifique a digitação.")


def test_form_loja_sucesso(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_st.text_input.side_effect = ["12345678000199", "Matriz", "Rua A"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_loja, "st", mock_st)
    monkeypatch.setattr(form_loja, "supabase", mock_sb)
    monkeypatch.setattr(form_loja, "limpar_e_validar_documento", lambda _: True)

    form_loja.render_form_loja()

    mock_sb.table.assert_called_once_with("loja")
    mock_st.success.assert_called_once_with("Loja cadastrada com sucesso!")


def test_form_loja_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.side_effect = RuntimeError("falha")
    mock_st.text_input.side_effect = ["12345678000199", "Matriz", "Rua A"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_loja, "st", mock_st)
    monkeypatch.setattr(form_loja, "supabase", mock_sb)
    monkeypatch.setattr(form_loja, "limpar_e_validar_documento", lambda _: True)

    form_loja.render_form_loja()

    mock_st.error.assert_called_once()