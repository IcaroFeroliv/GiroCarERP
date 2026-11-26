import datetime
from unittest.mock import MagicMock
import pandas as pd

from components.manutencoes import (
    aba_historico,
    aba_nova,
    cabecalho,
    kpis_manutencao,
)


# --- CABEÇALHO ---
def test_render_cabecalho_com_logo(monkeypatch, mock_st, tmp_path):
    logo_falsa = tmp_path / "girocar.png"
    logo_falsa.write_bytes(b"fake")

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_falsa)

    cabecalho.render_cabecalho()

    mock_st.image.assert_called_once_with(str(logo_falsa), width=180)
    mock_st.title.assert_called_once_with("Oficina e Manutenções")
    mock_st.caption.assert_called_once()


def test_render_cabecalho_sem_logo(monkeypatch, mock_st, tmp_path):
    logo_inexistente = tmp_path / "nao_existe.png"
    mock_logger = MagicMock()

    monkeypatch.setattr(cabecalho, "st", mock_st)
    monkeypatch.setattr(cabecalho, "LOGO_PATH", logo_inexistente)
    monkeypatch.setattr(cabecalho, "logger", mock_logger)

    cabecalho.render_cabecalho()

    mock_st.image.assert_not_called()
    mock_logger.error.assert_called_once()


# --- KPIS MANUTENÇÃO ---
def test_render_kpis_manutencao_com_dados(monkeypatch, mock_st):
    cols = [MagicMock(), MagicMock(), MagicMock()]
    mock_st.columns.side_effect = lambda spec, **kwargs: cols
    df = pd.DataFrame([{"custo_total": 500.0}, {"custo_total": 1500.0}])

    monkeypatch.setattr(kpis_manutencao, "st", mock_st)

    kpis_manutencao.render_kpis_manutencao(df)

    cols[0].metric.assert_called_once_with("Serviços registrados", 2)
    cols[1].metric.assert_called_once()
    cols[2].metric.assert_called_once()


def test_render_kpis_manutencao_vazio(monkeypatch, mock_st):
    cols = [MagicMock(), MagicMock(), MagicMock()]
    mock_st.columns.side_effect = lambda spec, **kwargs: cols

    monkeypatch.setattr(kpis_manutencao, "st", mock_st)

    kpis_manutencao.render_kpis_manutencao(pd.DataFrame())

    cols[0].metric.assert_called_once_with("Serviços registrados", 0)
    cols[1].metric.assert_called_once()
    cols[2].metric.assert_called_once()


# --- ABA HISTÓRICO ---
def _mock_supabase_historico(dados):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.order.return_value.execute.return_value.data = dados
    return mock_sb


def test_aba_historico_vazio(monkeypatch, mock_st):
    mock_sb = _mock_supabase_historico([])

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)

    aba_historico.render_aba_historico()

    mock_st.info.assert_called_once_with("Nenhuma manutenção foi registrada até o momento.")


def test_aba_historico_sem_coluna_custo_total(monkeypatch, mock_st):
    mock_sb = _mock_supabase_historico([{"placa_veiculo": "ABC1D23", "data": "2026-05-01"}])

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)

    aba_historico.render_aba_historico()

    mock_st.error.assert_called_once_with("A coluna custo_total não foi retornada pelo banco.")


def test_aba_historico_com_dados_e_filtros(monkeypatch, mock_st):
    mock_sb = _mock_supabase_historico([
        {
            "placa_veiculo": "ABC1D23",
            "descricao_servico": "Troca de óleo",
            "data": "2026-05-10",
            "custo_total": 350.0,
        },
        {
            "placa_veiculo": "XYZ9K88",
            "descricao_servico": "Alinhamento",
            "data": "2026-05-12",
            "custo_total": 200.0,
        },
    ])
    mock_kpis = MagicMock()
    mock_st.text_input.return_value = "abc"
    mock_st.date_input.side_effect = [datetime.date(2026, 5, 1), datetime.date(2026, 5, 31)]

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)
    monkeypatch.setattr(aba_historico, "render_kpis_manutencao", mock_kpis)

    aba_historico.render_aba_historico()

    mock_kpis.assert_called_once()
    mock_st.dataframe.assert_called_once()
    mock_st.metric.assert_called_once()


def test_aba_historico_sem_coluna_data_e_data_inicial_maior_que_final(monkeypatch, mock_st):
    mock_sb = _mock_supabase_historico([
        {"placa_veiculo": "ABC1D23", "descricao_servico": "Revisão", "custo_total": 500.0}
    ])
    mock_kpis = MagicMock()
    mock_st.text_input.return_value = ""
    mock_st.date_input.side_effect = [datetime.date(2026, 6, 10), datetime.date(2026, 6, 1)]

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)
    monkeypatch.setattr(aba_historico, "render_kpis_manutencao", mock_kpis)

    aba_historico.render_aba_historico()

    mock_st.warning.assert_called_once_with("A data inicial não pode ser posterior à data final.")
    mock_st.dataframe.assert_called_once()


def test_aba_historico_filtro_sem_resultado(monkeypatch, mock_st):
    mock_sb = _mock_supabase_historico([
        {
            "placa_veiculo": "ABC1D23",
            "descricao_servico": "Troca de óleo",
            "data": "2026-05-10",
            "custo_total": 350.0,
        }
    ])
    mock_kpis = MagicMock()
    mock_st.text_input.return_value = "INEXISTENTE"
    mock_st.date_input.side_effect = [datetime.date(2026, 5, 1), datetime.date(2026, 5, 31)]

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)
    monkeypatch.setattr(aba_historico, "render_kpis_manutencao", mock_kpis)

    aba_historico.render_aba_historico()

    mock_st.info.assert_called_once_with("Nenhum registro corresponde aos filtros selecionados.")


def test_aba_historico_erro_banco(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.side_effect = RuntimeError("falha conexao")
    mock_erro = MagicMock()

    monkeypatch.setattr(aba_historico, "st", mock_st)
    monkeypatch.setattr(aba_historico, "supabase", mock_sb)
    monkeypatch.setattr(aba_historico, "mostrar_erro", mock_erro)

    aba_historico.render_aba_historico()

    mock_erro.assert_called_once()


# --- ABA NOVA ---
def test_aba_nova_sem_veiculos_disponiveis(monkeypatch, mock_st):
    monkeypatch.setattr(aba_nova, "st", mock_st)
    monkeypatch.setattr(aba_nova, "obter_dados", lambda *args, **kwargs: [{"placa": "AAA1111", "status_veiculo": "Vendido"}])

    aba_nova.render_aba_nova()

    mock_st.warning.assert_called_once_with("Não há veículos disponíveis para registrar uma manutenção.")


def test_aba_nova_veiculos_sem_placa(monkeypatch, mock_st):
    monkeypatch.setattr(aba_nova, "st", mock_st)
    monkeypatch.setattr(aba_nova, "obter_dados", lambda *args, **kwargs: [{"modelo": "Civic"}])

    aba_nova.render_aba_nova()

    mock_st.warning.assert_called_once_with("Não foi possível identificar as placas dos veículos.")


def test_aba_nova_sem_submit(monkeypatch, mock_st):
    frota = [{"placa": "ABC1D23", "modelo": "Civic"}]
    mock_st.selectbox.return_value = "ABC1D23 - Civic"
    mock_st.date_input.return_value = datetime.date(2026, 5, 10)
    mock_st.text_area.return_value = ""
    mock_st.number_input.return_value = 0.0
    mock_st.form_submit_button.return_value = False

    monkeypatch.setattr(aba_nova, "st", mock_st)
    monkeypatch.setattr(aba_nova, "obter_dados", lambda *args, **kwargs: frota)

    aba_nova.render_aba_nova()

    mock_st.warning.assert_not_called()
    mock_st.success.assert_not_called()


def test_aba_nova_descricao_vazia(monkeypatch, mock_st):
    frota = [{"placa": "ABC1D23", "modelo": "Civic"}]
    mock_st.selectbox.return_value = "ABC1D23 - Civic"
    mock_st.date_input.return_value = datetime.date(2026, 5, 10)
    mock_st.text_area.return_value = "   "
    mock_st.number_input.return_value = 200.0
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(aba_nova, "st", mock_st)
    monkeypatch.setattr(aba_nova, "obter_dados", lambda *args, **kwargs: frota)

    aba_nova.render_aba_nova()

    mock_st.warning.assert_called_once_with("Informe a descrição do serviço.")


def test_aba_nova_custo_invalido(monkeypatch, mock_st):
    frota = [{"placa": "ABC1D23", "modelo": "Civic"}]
    mock_st.selectbox.return_value = "ABC1D23 - Civic"
    mock_st.date_input.return_value = datetime.date(2026, 5, 10)
    mock_st.text_area.return_value = "Troca de freio"
    mock_st.number_input.return_value = 0.0
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(aba_nova, "st", mock_st)
    monkeypatch.setattr(aba_nova, "obter_dados", lambda *args, **kwargs: frota)

    aba_nova.render_aba_nova()

    mock_st.warning.assert_called_once_with("O custo total deve ser maior que zero.")


def test_aba_nova_sucesso(monkeypatch, mock_st):
    frota = [{"placa": "ABC1D23", "modelo": "Civic"}]
    mock_sb = MagicMock()
    mock_st.selectbox.return_value = "ABC1D23 - Civic"
    mock_st.date_input.return_value = datetime.date(2026, 5, 10)
    mock_st.text_area.return_value = "Troca de freio"
    mock_st.number_input.return_value = 450.0
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(aba_nova, "st", mock_st)
    monkeypatch.setattr(aba_nova, "supabase", mock_sb)
    monkeypatch.setattr(aba_nova, "obter_dados", lambda *args, **kwargs: frota)

    aba_nova.render_aba_nova()

    assert mock_sb.table.call_count == 2
    mock_st.success.assert_called_once_with("Manutenção registrada para ABC1D23.")
    mock_st.rerun.assert_called_once()


def test_aba_nova_erro_salvar_os(monkeypatch, mock_st):
    frota = [{"placa": "ABC1D23", "modelo": "Civic"}]
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.side_effect = RuntimeError("falha insert")
    mock_erro = MagicMock()

    mock_st.selectbox.return_value = "ABC1D23 - Civic"
    mock_st.date_input.return_value = datetime.date(2026, 5, 10)
    mock_st.text_area.return_value = "Troca de freio"
    mock_st.number_input.return_value = 450.0
    mock_st.form_submit_button.return_value = True

    monkeypatch.setattr(aba_nova, "st", mock_st)
    monkeypatch.setattr(aba_nova, "supabase", mock_sb)
    monkeypatch.setattr(aba_nova, "obter_dados", lambda *args, **kwargs: frota)
    monkeypatch.setattr(aba_nova, "mostrar_erro", mock_erro)

    aba_nova.render_aba_nova()

    mock_erro.assert_called_once()


def test_aba_nova_erro_carregar_veiculos(monkeypatch, mock_st):
    mock_erro = MagicMock()

    def _erro(*args, **kwargs):
        raise RuntimeError("erro banco")

    monkeypatch.setattr(aba_nova, "st", mock_st)
    monkeypatch.setattr(aba_nova, "obter_dados", _erro)
    monkeypatch.setattr(aba_nova, "mostrar_erro", mock_erro)

    aba_nova.render_aba_nova()

    mock_erro.assert_called_once()