def calcular_lucro_bruto(valor_venda, valor_compra):
    """Calcula o lucro de uma venda e impede valores negativos acidentais."""
    if valor_venda < 0 or valor_compra < 0:
        raise ValueError("Os valores não podem ser negativos.")
    return valor_venda - valor_compra

def validar_venda_rn01(status_veiculo):
    """RN01: Um veículo só pode ser vendido se estiver 'Disponivel'."""
    status_formatado = status_veiculo.strip().lower()
    if status_formatado == "em preparacao":
        return False
    elif status_formatado == "vendido":
        return False
    elif status_formatado == "disponivel":
        return True
    return False