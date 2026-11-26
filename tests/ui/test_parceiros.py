from unittest.mock import MagicMock

from components.parceiros import (
    aba_clientes,
    aba_fornecedores,
    cabecalho,
    consulta_cliente,
    consulta_fornecedor,
    form_cliente,
    form_fornecedor,
)


# --- ABAS ---
def test_render_aba_clientes(monkeypatch, mock_st):
    mock_form = MagicMock()
    mock_consulta = MagicMock()

    monkeypatch.setattr(aba_clientes, "st", mock_st)
    monkeypatch.setattr(aba_clientes, "render_form_cliente", mock_form)
    monkeypatch.setattr(aba_clientes, "render_consulta_cliente", mock_consulta)

    aba_clientes.render_aba_clientes()

    mock_st.subheader.assert_called_once_with("Cadastro de Clientes")
    mock_form.assert_called_once()
    mock_st.divider.assert_called_once()
    mock_consulta.assert_called_once()


def test_render_aba_fornecedores(monkeypatch, mock_st):
    mock_form = MagicMock()
    mock_consulta = MagicMock()

    monkeypatch.setattr(aba_fornecedores, "st", mock_st)
    monkeypatch.setattr(aba_fornecedores, "render_form_fornecedor", mock_form)
    monkeypatch.setattr(aba_fornecedores, "render_consulta_fornecedor", mock_consulta)

    aba_fornecedores.render_aba_fornecedores()

    mock_st.subheader.assert_called_once_with("Cadastro de Fornecedores")
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
    mock_st.title.assert_called_once_with("Gestão de Parceiros Comerciais")


def test_render_cabecalho_sem_logo(monkeypatch, mock_st, tmp_path):
    logo_inexistente = tmp_path / "nao_existe.png"
    mock_logger = MagicMock()

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_inexistente)
    monkeypatch.setattr(cabecalho, "logger", mock_logger)

    cabecalho.render_cabecalho()

    mock_st.image.assert_not_called()
    mock_logger.error.assert_called_once()


# --- CONSULTA CLIENTE ---
def test_consulta_cliente_vazio(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = []

    monkeypatch.setattr(consulta_cliente, "st", mock_st)
    monkeypatch.setattr(consulta_cliente, "supabase", mock_sb)

    consulta_cliente.render_consulta_cliente()

    mock_st.info.assert_called_once_with("Nenhum cliente cadastrado.")


def test_consulta_cliente_com_dados_e_filtro_status(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {
            "cpf_cnpj": "12345678901",
            "nome_completo": "Carlos Silva",
            "telefone": "31999990000",
            "email": "carlos@email.com",
            "status_funil_vendas": "Em Negociação",
        },
        {
            "cpf_cnpj": "98765432100",
            "nome_completo": "Maria Souza",
            "telefone": "31988880000",
            "email": "maria@email.com",
            "status_funil_vendas": "Venda Fechada",
        },
    ]
    mock_st.text_input.return_value = "Carlos"
    mock_st.selectbox.return_value = "Em Negociação"

    monkeypatch.setattr(consulta_cliente, "st", mock_st)
    monkeypatch.setattr(consulta_cliente, "supabase", mock_sb)

    consulta_cliente.render_consulta_cliente()

    mock_st.dataframe.assert_called_once()
    mock_st.caption.assert_called_once_with("1 cliente(s) encontrado(s)")


def test_consulta_cliente_sem_coluna_status_e_sem_resultado(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {
            "cpf_cnpj": "12345678901",
            "nome_completo": "Carlos Silva",
            "telefone": "31999990000",
            "email": "carlos@email.com",
        }
    ]
    mock_st.text_input.return_value = "Inexistente"

    monkeypatch.setattr(consulta_cliente, "st", mock_st)
    monkeypatch.setattr(consulta_cliente, "supabase", mock_sb)

    consulta_cliente.render_consulta_cliente()

    mock_st.info.assert_called_once_with("Nenhum cliente corresponde à sua pesquisa.")


def test_consulta_cliente_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.side_effect = RuntimeError("erro banco")

    monkeypatch.setattr(consulta_cliente, "st", mock_st)
    monkeypatch.setattr(consulta_cliente, "supabase", mock_sb)

    consulta_cliente.render_consulta_cliente()

    mock_st.error.assert_called_once_with("Erro ao carregar a lista de clientes.")


# --- CONSULTA FORNECEDOR ---
def test_consulta_fornecedor_vazio(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = []

    monkeypatch.setattr(consulta_fornecedor, "st", mock_st)
    monkeypatch.setattr(consulta_fornecedor, "supabase", mock_sb)

    consulta_fornecedor.render_consulta_fornecedor()

    mock_st.info.assert_called_once_with("Nenhum fornecedor cadastrado.")


def test_consulta_fornecedor_com_dados(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {
            "cnpj_cpf": "12345678000199",
            "nome_razao_social": "Auto Repasse BH",
            "telefone": "3133334444",
            "tipo_origem": "Repasse",
        }
    ]
    mock_st.text_input.return_value = "Repasse"

    monkeypatch.setattr(consulta_fornecedor, "st", mock_st)
    monkeypatch.setattr(consulta_fornecedor, "supabase", mock_sb)

    consulta_fornecedor.render_consulta_fornecedor()

    mock_st.dataframe.assert_called_once()
    mock_st.caption.assert_called_once_with("1 fornecedor(es) encontrado(s)")


def test_consulta_fornecedor_pesquisa_sem_resultado(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {
            "cnpj_cpf": "12345678000199",
            "nome_razao_social": "Auto Repasse BH",
            "telefone": "3133334444",
            "tipo_origem": "Repasse",
        }
    ]
    mock_st.text_input.return_value = "Inexistente"

    monkeypatch.setattr(consulta_fornecedor, "st", mock_st)
    monkeypatch.setattr(consulta_fornecedor, "supabase", mock_sb)

    consulta_fornecedor.render_consulta_fornecedor()

    mock_st.info.assert_called_once_with("Nenhum fornecedor corresponde à sua pesquisa.")


def test_consulta_fornecedor_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.side_effect = RuntimeError("erro banco")

    monkeypatch.setattr(consulta_fornecedor, "st", mock_st)
    monkeypatch.setattr(consulta_fornecedor, "supabase", mock_sb)

    consulta_fornecedor.render_consulta_fornecedor()

    mock_st.error.assert_called_once_with("Erro ao carregar a lista de fornecedores.")


# --- FORM CLIENTE ---
def test_form_cliente_sem_submit(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["", "", "", ""]
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(form_cliente, "st", mock_st)

    form_cliente.render_form_cliente()

    mock_st.warning.assert_not_called()
    mock_st.success.assert_not_called()


def test_form_cliente_campos_obrigatorios(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["", "Carlos", "31999990000", "carlos@email.com"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_cliente, "st", mock_st)

    form_cliente.render_form_cliente()

    mock_st.warning.assert_called_once_with("Preencha os campos obrigatórios (CPF/CNPJ e Nome).")


def test_form_cliente_documento_invalido(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["000", "Carlos", "31999990000", "carlos@email.com"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_cliente, "st", mock_st)
    monkeypatch.setattr(form_cliente, "limpar_e_validar_documento", lambda _: False)

    form_cliente.render_form_cliente()

    mock_st.error.assert_called_once_with("CPF/CNPJ inválido. Verifique a digitação.")


def test_form_cliente_sucesso(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_st.text_input.side_effect = ["12345678901", "Carlos", "31999990000", "carlos@email.com"]
    mock_st.selectbox.return_value = "Contato Inicial"
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_cliente, "st", mock_st)
    monkeypatch.setattr(form_cliente, "supabase", mock_sb)
    monkeypatch.setattr(form_cliente, "limpar_e_validar_documento", lambda _: True)

    form_cliente.render_form_cliente()

    mock_sb.table.assert_called_once_with("cliente")
    mock_st.success.assert_called_once_with("Cliente cadastrado com sucesso!")


def test_form_cliente_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.side_effect = RuntimeError("falha")
    mock_st.text_input.side_effect = ["12345678901", "Carlos", "31999990000", "carlos@email.com"]
    mock_st.selectbox.return_value = "Contato Inicial"
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_cliente, "st", mock_st)
    monkeypatch.setattr(form_cliente, "supabase", mock_sb)
    monkeypatch.setattr(form_cliente, "limpar_e_validar_documento", lambda _: True)

    form_cliente.render_form_cliente()

    mock_st.error.assert_called_once()


# --- FORM FORNECEDOR ---
def test_form_fornecedor_sem_submit(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["", "", ""]
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(form_fornecedor, "st", mock_st)

    form_fornecedor.render_form_fornecedor()

    mock_st.warning.assert_not_called()
    mock_st.success.assert_not_called()


def test_form_fornecedor_campos_obrigatorios(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["", "Auto Repasse", "3133334444"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_fornecedor, "st", mock_st)

    form_fornecedor.render_form_fornecedor()

    mock_st.warning.assert_called_once_with("Preencha os campos obrigatórios (CNPJ/CPF e Nome).")


def test_form_fornecedor_documento_invalido(monkeypatch, mock_st):
    mock_st.text_input.side_effect = ["000", "Auto Repasse", "3133334444"]
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_fornecedor, "st", mock_st)
    monkeypatch.setattr(form_fornecedor, "limpar_e_validar_documento", lambda _: False)

    form_fornecedor.render_form_fornecedor()

    mock_st.error.assert_called_once_with("CPF/CNPJ inválido. Verifique a digitação.")


def test_form_fornecedor_sucesso(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_st.text_input.side_effect = ["12345678000199", "Auto Repasse", "3133334444"]
    mock_st.selectbox.return_value = "Repasse"
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_fornecedor, "st", mock_st)
    monkeypatch.setattr(form_fornecedor, "supabase", mock_sb)
    monkeypatch.setattr(form_fornecedor, "limpar_e_validar_documento", lambda _: True)

    form_fornecedor.render_form_fornecedor()

    mock_sb.table.assert_called_once_with("fornecedor")
    mock_st.success.assert_called_once_with("Fornecedor cadastrado com sucesso!")


def test_form_fornecedor_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.side_effect = RuntimeError("falha")
    mock_st.text_input.side_effect = ["12345678000199", "Auto Repasse", "3133334444"]
    mock_st.selectbox.return_value = "Repasse"
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(form_fornecedor, "st", mock_st)
    monkeypatch.setattr(form_fornecedor, "supabase", mock_sb)
    monkeypatch.setattr(form_fornecedor, "limpar_e_validar_documento", lambda _: True)

    form_fornecedor.render_form_fornecedor()

    mock_st.error.assert_called_once()