import runpy
import sys
from unittest.mock import MagicMock
import pytest

import database
from components.regras_negocio import trava_seguranca, calcular_kpis_comercial
from components.veiculos import (
    cabecalho as veic_cabecalho,
    aba_consulta as veic_consulta,
    aba_cadastro as veic_cadastro,
    aba_fipe as veic_fipe,
    aba_historico as veic_historico,
)
from components.comercial import (
    cabecalho as com_cabecalho,
    kpis_comercial as com_kpis,
    aba_historico as com_historico,
    aba_venda as com_venda,
    aba_pagamento as com_pagamento,
)
from components.manutencoes import (
    cabecalho as man_cabecalho,
    aba_historico as man_historico,
    aba_nova as man_nova,
)
from components.parceiros import (
    cabecalho as parc_cabecalho,
    aba_clientes as parc_clientes,
    aba_fornecedores as parc_fornecedores,
)
from components.administracao import (
    cabecalho as adm_cabecalho,
    aba_lojas as adm_lojas,
    aba_funcionarios as adm_funcionarios,
)


class _StopStreamlit(Exception):
    """Exceção auxiliar para simular st.stop() interrompendo a execução da página."""


# ==========================================
# 01_Veiculos.py
# ==========================================
def test_page_01_veiculos_sucesso(monkeypatch, mock_st):
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", MagicMock())
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())

    m_cab = MagicMock()
    m_cons = MagicMock()
    m_cad = MagicMock()
    m_fipe = MagicMock()
    m_hist = MagicMock()

    monkeypatch.setattr(veic_cabecalho, "render_cabecalho", m_cab)
    monkeypatch.setattr(veic_consulta, "render_aba_consulta", m_cons)
    monkeypatch.setattr(veic_cadastro, "render_aba_cadastro", m_cad)
    monkeypatch.setattr(veic_fipe, "render_aba_fipe", m_fipe)
    monkeypatch.setattr(veic_historico, "render_aba_historico", m_hist)

    runpy.run_path("pages/01_Veiculos.py")

    m_cab.assert_called_once()
    m_cons.assert_called_once()
    m_cad.assert_called_once()
    m_fipe.assert_called_once()
    m_hist.assert_called_once()


def test_page_01_veiculos_sem_supabase(monkeypatch, mock_st):
    mock_st.stop.side_effect = _StopStreamlit
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", None)
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())
    monkeypatch.setattr(veic_cabecalho, "render_cabecalho", MagicMock())

    with pytest.raises(_StopStreamlit):
        runpy.run_path("pages/01_Veiculos.py")

    mock_st.error.assert_called_once()


# ==========================================
# 02_Comercial.py
# ==========================================
def test_page_02_comercial_sucesso(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"id_transacao": 1, "valor_final_negociado": 50000.0}
    ]

    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", mock_sb)
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())
    monkeypatch.setattr(calcular_kpis_comercial, "calcular_kpis_comercial", lambda df: (1, 50000.0, 50000.0))

    m_cab = MagicMock()
    m_kpis = MagicMock()
    m_hist = MagicMock()
    m_venda = MagicMock()
    m_pag = MagicMock()

    monkeypatch.setattr(com_cabecalho, "render_cabecalho", m_cab)
    monkeypatch.setattr(com_kpis, "render_kpis_comercial", m_kpis)
    monkeypatch.setattr(com_historico, "render_aba_historico", m_hist)
    monkeypatch.setattr(com_venda, "render_aba_venda", m_venda)
    monkeypatch.setattr(com_pagamento, "render_aba_pagamento", m_pag)

    runpy.run_path("pages/02_Comercial.py")

    mock_st.warning.assert_not_called()
    m_cab.assert_called_once()
    m_kpis.assert_called_once_with(1, 50000.0, 50000.0)
    m_hist.assert_called_once()
    m_venda.assert_called_once()
    m_pag.assert_called_once()


def test_page_02_comercial_erro_carregamento(monkeypatch, mock_st):
    mock_sb = MagicMock()
    mock_sb.table.side_effect = RuntimeError("erro conexao")

    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", mock_sb)
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())
    monkeypatch.setattr(calcular_kpis_comercial, "calcular_kpis_comercial", lambda df: (0, 0.0, 0.0))
    monkeypatch.setattr(com_cabecalho, "render_cabecalho", MagicMock())
    monkeypatch.setattr(com_kpis, "render_kpis_comercial", MagicMock())
    monkeypatch.setattr(com_historico, "render_aba_historico", MagicMock())
    monkeypatch.setattr(com_venda, "render_aba_venda", MagicMock())
    monkeypatch.setattr(com_pagamento, "render_aba_pagamento", MagicMock())

    runpy.run_path("pages/02_Comercial.py")

    mock_st.warning.assert_called_once()


# ==========================================
# 03_Manutencoes.py
# ==========================================
def test_page_03_manutencoes_sucesso(monkeypatch, mock_st):
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", MagicMock())
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())

    m_cab = MagicMock()
    m_hist = MagicMock()
    m_nova = MagicMock()

    monkeypatch.setattr(man_cabecalho, "render_cabecalho", m_cab)
    monkeypatch.setattr(man_historico, "render_aba_historico", m_hist)
    monkeypatch.setattr(man_nova, "render_aba_nova", m_nova)

    runpy.run_path("pages/03_Manutencoes.py")

    m_cab.assert_called_once()
    m_hist.assert_called_once()
    m_nova.assert_called_once()


def test_page_03_manutencoes_sem_supabase(monkeypatch, mock_st):
    mock_st.stop.side_effect = _StopStreamlit
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", None)
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())
    monkeypatch.setattr(man_cabecalho, "render_cabecalho", MagicMock())

    with pytest.raises(_StopStreamlit):
        runpy.run_path("pages/03_Manutencoes.py")

    mock_st.error.assert_called_once_with("Não foi possível conectar ao banco de dados.")


# ==========================================
# 04_Parceiros.py
# ==========================================
def test_page_04_parceiros_sucesso(monkeypatch, mock_st):
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", MagicMock())
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())

    m_cab = MagicMock()
    m_cli = MagicMock()
    m_forn = MagicMock()

    monkeypatch.setattr(parc_cabecalho, "render_cabecalho", m_cab)
    monkeypatch.setattr(parc_clientes, "render_aba_clientes", m_cli)
    monkeypatch.setattr(parc_fornecedores, "render_aba_fornecedores", m_forn)

    runpy.run_path("pages/04_Parceiros.py")

    m_cab.assert_called_once()
    m_cli.assert_called_once()
    m_forn.assert_called_once()


def test_page_04_parceiros_sem_supabase(monkeypatch, mock_st):
    mock_st.stop.side_effect = _StopStreamlit
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", None)
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())
    monkeypatch.setattr(parc_cabecalho, "render_cabecalho", MagicMock())

    with pytest.raises(_StopStreamlit):
        runpy.run_path("pages/04_Parceiros.py")

    mock_st.error.assert_called_once_with("Erro de conexão com o banco de dados.")


# ==========================================
# 05_Administracao.py
# ==========================================
def test_page_05_administracao_sucesso(monkeypatch, mock_st):
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", MagicMock())
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())

    m_cab = MagicMock()
    m_lojas = MagicMock()
    m_func = MagicMock()

    monkeypatch.setattr(adm_cabecalho, "render_cabecalho", m_cab)
    monkeypatch.setattr(adm_lojas, "render_aba_lojas", m_lojas)
    monkeypatch.setattr(adm_funcionarios, "render_aba_funcionarios", m_func)

    runpy.run_path("pages/05_Administracao.py")

    m_cab.assert_called_once()
    m_lojas.assert_called_once()
    m_func.assert_called_once()


def test_page_05_administracao_sem_supabase(monkeypatch, mock_st):
    mock_st.stop.side_effect = _StopStreamlit
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    monkeypatch.setattr(database, "supabase", None)
    monkeypatch.setattr(trava_seguranca, "verificar_acesso", MagicMock())
    monkeypatch.setattr(adm_cabecalho, "render_cabecalho", MagicMock())

    with pytest.raises(_StopStreamlit):
        runpy.run_path("pages/05_Administracao.py")

    mock_st.error.assert_called_once()