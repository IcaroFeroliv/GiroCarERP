import pandas as pd

def formatar_reais(valor):
    """Formata número no padrão brasileiro (R$ 1.234,56). Valores nulos viram texto vazio."""
    if pd.isnull(valor):
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")