from datetime import date
from unittest.mock import MagicMock
import pandas as pd

from components.comercial import (
    aba_historico,
    aba_pagamento,
    aba_venda,
    cabecalho,
    consulta_vendas,
    form_pagamento,
    form_venda,
    kpis_comercial,
)


# --- ABAS ---
def test_render_aba_historico(monkeypatch, mock_st):
    mock_consulta = MagicMock()
    df = pd.DataFrame()

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "render_consulta_vendas", mock_consulta)

    aba_historico.render_aba_historico(df)

    mock_st.subheader.assert_called_once_with("Histórico de vendas")
    mock_st.caption.assert_called_once()
    mock_consulta.assert_called_once_with(df)


def test_render_aba_pagamento(monkeypatch, mock_st):
    mock_form = MagicMock()

    monkeypatch.setattr(aba_pagamento, "st", mock_st)
    monkeypatch.setattr(aba_pagamento, "render_form_pagamento", mock_form)

    aba_pagamento.render_aba_pagamento()

    mock_st.subheader.assert_called_once_with("Lançar pagamento")
    mock_st.caption.assert_called_once()
    mock_form.assert_called_once()


def test_render_aba_venda(monkeypatch, mock_st):
    mock_form = MagicMock()

    monkeypatch.setattr(aba_venda, "st", mock_st)
    monkeypatch.setattr(aba_venda, "render_form_venda", mock_form)

    aba_venda.render_aba_venda()

    mock_st.subheader.assert_called_once_with("Registrar nova venda")
    mock_st.caption.assert_called_once()
    mock_form.assert_called_once()


# --- CABEÇALHO ---
def test_render_cabecalho_com_logo(monkeypatch, mock_st, tmp_path):
    logo_falsa = tmp_path / "girocar.png"
    logo_falsa.write_bytes(b"fake")

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_falsa)

    cabecalho.render_cabecalho()

    mock_st.image.assert_called_once_with(str(logo_falsa), width=110)
    mock_st.title.assert_called_once_with("Comercial e Gestão de Vendas")
    mock_st.divider.assert_called_once()


def test_render_cabecalho_sem_logo(monkeypatch, mock_st, tmp_path):
    logo_inexistente = tmp_path / "nao_existe.png"

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_inexistente)

    cabecalho.render_cabecalho()

    mock_st.image.assert_not_called()
    mock_st.markdown.assert_any_call("# 🚗")


# --- KPIS COMERCIAL ---
def test_render_kpis_comercial(monkeypatch, mock_st):
    monkeypatch.setattr(kpis_comercial, "st", mock_st)

    kpis_comercial.render_kpis_comercial(5, 250000.0, 50000.0)

    assert mock_st.metric.call_count == 3
    mock_st.divider.assert_called_once()


# --- CONSULTA VENDAS ---
def test_consulta_vendas_vazio(monkeypatch, mock_st):
    monkeypatch.setattr(consulta_vendas, "st", mock_st)

    consulta_vendas.render_consulta_vendas(pd.DataFrame())

    mock_st.info.assert_called_once_with("Nenhuma venda foi encontrada para exibição.")
    mock_st.dataframe.assert_not_called()


def test_consulta_vendas_com_colunas_completas(monkeypatch, mock_st):
    df = pd.DataFrame([
        {"placa_veiculo": "ABC1D23", "valor_final_negociado": 50000.0, "data": "2026-05-01"},
        {"placa_veiculo": "XYZ9K88", "valor_final_negociado": 80000.0, "data": "2026-05-02"},
    ])
    mock_st.text_input.return_value = "abc"
    mock_st.slider.return_value = (40000.0, 60000.0)

    monkeypatch.setattr(consulta_vendas, "st", mock_st)

    consulta_vendas.render_consulta_vendas(df)

    mock_st.dataframe.assert_called_once()
    mock_st.caption.assert_called_once_with("Exibindo 1 de 2 venda(s).")


def test_consulta_vendas_sem_colunas_de_filtro(monkeypatch, mock_st):
    df = pd.DataFrame([{"id_transacao": 1, "data": "2026-05-01"}])

    monkeypatch.setattr(consulta_vendas, "st", mock_st)

    consulta_vendas.render_consulta_vendas(df)

    mock_st.text_input.assert_not_called()
    mock_st.slider.assert_not_called()
    mock_st.dataframe.assert_called_once()
    mock_st.caption.assert_called_once_with("Exibindo 1 de 1 venda(s).")


# --- FORM PAGAMENTO ---
def test_form_pagamento_sem_transacoes(monkeypatch, mock_st):
    monkeypatch.setattr(form_pagamento, "st", mock_st)
    monkeypatch.setattr(form_pagamento, "obter_dados", lambda *args, **kwargs: [])

    form_pagamento.render_form_pagamento()

    mock_st.info.assert_called_once_with("Registre uma venda antes de lançar um pagamento.")


def test_form_pagamento_sem_submit(monkeypatch, mock_st):
    transacoes = [{"id_transacao": 1, "placa_veiculo": "ABC1D23", "valor_final_negociado": 50000.0}]
    mock_st.selectbox.side_effect = [transacoes[0], "PIX"]
    mock_st.number_input.side_effect = [50000.0, 1, 0.0]
    mock_st.text_input.return_value = "Banco X"
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(form_pagamento, "st", mock_st)
    monkeypatch.setattr(form_pagamento, "obter_dados", lambda *args, **kwargs: transacoes)

    form_pagamento.render_form_pagamento()

    mock_st.success.assert_not_called()
    mock_st.warning.assert_not_called()


def test_form_pagamento_sucesso(monkeypatch, mock_st):
    transacoes = [{"id_transacao": 1, "placa_veiculo": "ABC1D23", "valor_final_negociado": 50000.0}]
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value.data = [{"id": 10}]

    mock_st.selectbox.side_effect = [transacoes[0], "PIX"]
    mock_st.number_input.side_effect = [50000.0, 1, 0.0]
    mock_st.text_input.return_value = "Banco X"
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_pagamento, "st", mock_st)
    monkeypatch.setattr(form_pagamento, "supabase", mock_sb)
    monkeypatch.setattr(form_pagamento, "obter_dados", lambda *args, **kwargs: transacoes)

    form_pagamento.render_form_pagamento()

    mock_st.success.assert_called_once_with("Pagamento registrado com sucesso!")
    mock_st.rerun.assert_called_once()


def test_form_pagamento_sem_confirmacao_banco(monkeypatch, mock_st):
    transacoes = [{"id_transacao": 1, "placa_veiculo": "ABC1D23", "valor_final_negociado": 50000.0}]
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value.data = []

    mock_st.selectbox.side_effect = [transacoes[0], "PIX"]
    mock_st.number_input.side_effect = [50000.0, 1, 0.0]
    mock_st.text_input.return_value = "Banco X"
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_pagamento, "st", mock_st)
    monkeypatch.setattr(form_pagamento, "supabase", mock_sb)
    monkeypatch.setattr(form_pagamento, "obter_dados", lambda *args, **kwargs: transacoes)

    form_pagamento.render_form_pagamento()

    mock_st.warning.assert_called_once()


def test_form_pagamento_erro_banco(monkeypatch, mock_st):
    transacoes = [{"id_transacao": 1, "placa_veiculo": "ABC1D23", "valor_final_negociado": 50000.0}]
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.side_effect = RuntimeError("falha")
    mock_erro = MagicMock()

    mock_st.selectbox.side_effect = [transacoes[0], "PIX"]
    mock_st.number_input.side_effect = [50000.0, 1, 0.0]
    mock_st.text_input.return_value = "Banco X"
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_pagamento, "st", mock_st)
    monkeypatch.setattr(form_pagamento, "supabase", mock_sb)
    monkeypatch.setattr(form_pagamento, "obter_dados", lambda *args, **kwargs: transacoes)
    monkeypatch.setattr(form_pagamento, "mostrar_erro", mock_erro)

    form_pagamento.render_form_pagamento()

    mock_erro.assert_called_once()


# --- FORM VENDA ---
def _mock_supabase_opcoes(veiculos, clientes, funcionarios, insert_data=None, update_data=None, erro_insert=False):
    mock_sb = MagicMock()

    def table_side_effect(nome_tabela):
        tbl = MagicMock()
        if nome_tabela == "veiculo":
            tbl.select.return_value.eq.return_value.execute.return_value.data = veiculos
            tbl.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = update_data
        elif nome_tabela == "cliente":
            tbl.select.return_value.execute.return_value.data = clientes
        elif nome_tabela == "funcionario":
            tbl.select.return_value.execute.return_value.data = funcionarios
        elif nome_tabela == "transacao":
            if erro_insert:
                tbl.insert.return_value.execute.side_effect = RuntimeError("falha insert")
            else:
                tbl.insert.return_value.execute.return_value.data = insert_data
        return tbl

    mock_sb.table.side_effect = table_side_effect
    return mock_sb


def test_form_venda_botao_atualizar_e_erro_opcoes(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.side_effect = RuntimeError("sem conexao")
    mock_st.button.return_value = True

    monkeypatch.setattr(form_venda, "st", mock_st)
    monkeypatch.setattr(form_venda, "supabase", mock_sb)

    form_venda.render_form_venda()

    mock_st.rerun.assert_called_once()
    mock_st.error.assert_called_once()


def test_form_venda_sem_veiculos(monkeypatch, mock_st):
    mock_sb = _mock_supabase_opcoes([], [{"cpf_cnpj": "1"}], [{"matricula": "1"}])
    monkeypatch.setattr(form_venda, "st", mock_st)
    monkeypatch.setattr(form_venda, "supabase", mock_sb)

    form_venda.render_form_venda()

    mock_st.warning.assert_called_once_with("Não há veículos disponíveis para venda no momento.")


def test_form_venda_sem_clientes(monkeypatch, mock_st):
    mock_sb = _mock_supabase_opcoes([{"placa": "ABC1D23"}], [], [{"matricula": "1"}])
    monkeypatch.setattr(form_venda, "st", mock_st)
    monkeypatch.setattr(form_venda, "supabase", mock_sb)

    form_venda.render_form_venda()

    mock_st.warning.assert_called_once_with("Cadastre um cliente antes de registrar uma venda.")


def test_form_venda_sem_funcionarios(monkeypatch, mock_st):
    mock_sb = _mock_supabase_opcoes([{"placa": "ABC1D23"}], [{"cpf_cnpj": "1"}], [])
    monkeypatch.setattr(form_venda, "st", mock_st)
    monkeypatch.setattr(form_venda, "supabase", mock_sb)

    form_venda.render_form_venda()

    mock_st.warning.assert_called_once_with("Cadastre um funcionário antes de registrar uma venda.")


def test_form_venda_sem_submit(monkeypatch, mock_st):
    veiculos = [{"placa": "ABC1D23", "modelo": "Civic"}]
    clientes = [{"cpf_cnpj": "123", "nome_completo": "João"}]
    funcionarios = [{"matricula": "001", "nome": "Ana"}]
    mock_sb = _mock_supabase_opcoes(veiculos, clientes, funcionarios)

    mock_st.selectbox.side_effect = [veiculos[0], clientes[0], funcionarios[0]]
    mock_st.date_input.return_value = date(2026, 5, 1)
    mock_st.number_input.return_value = 75000.0
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(form_venda, "st", mock_st)
    monkeypatch.setattr(form_venda, "supabase", mock_sb)

    form_venda.render_form_venda()

    mock_st.success.assert_not_called()
    mock_st.error.assert_not_called()


def test_form_venda_insert_sem_confirmacao(monkeypatch, mock_st):
    veiculos = [{"placa": "ABC1D23", "modelo": "Civic"}]
    clientes = [{"cpf_cnpj": "123", "nome_completo": "João"}]
    funcionarios = [{"matricula": "001", "nome": "Ana"}]
    mock_sb = _mock_supabase_opcoes(veiculos, clientes, funcionarios, insert_data=[])

    mock_st.selectbox.side_effect = [veiculos[0], clientes[0], funcionarios[0]]
    mock_st.date_input.return_value = date(2026, 5, 1)
    mock_st.number_input.return_value = 75000.0
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_venda, "st", mock_st)
    monkeypatch.setattr(form_venda, "supabase", mock_sb)

    form_venda.render_form_venda()

    mock_st.error.assert_called_once()


def test_form_venda_sucesso_completo(monkeypatch, mock_st):
    veiculos = [{"placa": "ABC1D23", "modelo": "Civic"}]
    clientes = [{"cpf_cnpj": "123", "nome_completo": "João"}]
    funcionarios = [{"matricula": "001", "nome": "Ana"}]
    mock_sb = _mock_supabase_opcoes(
        veiculos, clientes, funcionarios, insert_data=[{"id": 1}], update_data=[{"placa": "ABC1D23"}]
    )

    mock_st.selectbox.side_effect = [veiculos[0], clientes[0], funcionarios[0]]
    mock_st.date_input.return_value = date(2026, 5, 1)
    mock_st.number_input.return_value = 75000.0
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_venda, "st", mock_st)
    monkeypatch.setattr(form_venda, "supabase", mock_sb)

    form_venda.render_form_venda()

    mock_st.success.assert_called_once_with("Venda registrada e veículo atualizado com sucesso!")
    mock_st.rerun.assert_called_once()


def test_form_venda_update_veiculo_nao_confirmado(monkeypatch, mock_st):
    veiculos = [{"placa": "ABC1D23", "modelo": "Civic"}]
    clientes = [{"cpf_cnpj": "123", "nome_completo": "João"}]
    funcionarios = [{"matricula": "001", "nome": "Ana"}]
    mock_sb = _mock_supabase_opcoes(
        veiculos, clientes, funcionarios, insert_data=[{"id": 1}], update_data=[]
    )

    mock_st.selectbox.side_effect = [veiculos[0], clientes[0], funcionarios[0]]
    mock_st.date_input.return_value = date(2026, 5, 1)
    mock_st.number_input.return_value = 75000.0
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_venda, "st", mock_st)
    monkeypatch.setattr(form_venda, "supabase", mock_sb)

    form_venda.render_form_venda()

    mock_st.error.assert_called_once()


def test_form_venda_erro_banco(monkeypatch, mock_st):
    veiculos = [{"placa": "ABC1D23", "modelo": "Civic"}]
    clientes = [{"cpf_cnpj": "123", "nome_completo": "João"}]
    funcionarios = [{"matricula": "001", "nome": "Ana"}]
    mock_sb = _mock_supabase_opcoes(veiculos, clientes, funcionarios, erro_insert=True)
    mock_erro = MagicMock()

    mock_st.selectbox.side_effect = [veiculos[0], clientes[0], funcionarios[0]]
    mock_st.date_input.return_value = date(2026, 5, 1)
    mock_st.number_input.return_value = 75000.0
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_venda, "st", mock_st)
    monkeypatch.setattr(form_venda, "supabase", mock_sb)
    monkeypatch.setattr(form_venda, "mostrar_erro", mock_erro)

    form_venda.render_form_venda()

    mock_erro.assert_called_once()