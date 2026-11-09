def valor_fipe_para_float(texto):
    """Converte 'R$ 45.000,00' em 45000.0."""
    return float(texto.replace("R$ ", "").replace(".", "").replace(",", "."))