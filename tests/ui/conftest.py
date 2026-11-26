from unittest.mock import MagicMock
import pytest


class DummyContextManager:
    """Simula blocos 'with' do Streamlit (st.form, st.expander, col, tab, etc.)."""
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


@pytest.fixture
def mock_st():
    """Retorna um mock do Streamlit pronto para componentes visuais."""
    st = MagicMock()
    st.session_state = {}

    # Simula st.columns(3) ou st.columns([1, 2]) retornando contextos válidos
    def fake_columns(spec, **kwargs):
        qtd = spec if isinstance(spec, int) else len(spec)
        return [DummyContextManager() for _ in range(qtd)]

    # Simula st.tabs(["Aba 1", "Aba 2"])
    def fake_tabs(labels):
        return [DummyContextManager() for _ in labels]

    st.columns.side_effect = fake_columns
    st.tabs.side_effect = fake_tabs
    st.form.return_value = DummyContextManager()
    st.expander.return_value = DummyContextManager()
    st.spinner.return_value = DummyContextManager()
    st.container.return_value = DummyContextManager()

    # Evita que botões ou submits disparem sem querer no teste padrão
    st.button.return_value = False
    st.form_submit_button.return_value = False

    return st