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

def formatar_moeda_br(valor):
    """Formata um valor float para o padrão de moeda brasileiro."""
    if not isinstance(valor, (int, float)):
        raise TypeError("O valor deve ser numérico.")
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")