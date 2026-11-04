"""
GiroCar ERP - Módulo de Regras de Negócio (Core)
Este módulo concentra todas as lógicas financeiras, logísticas e comerciais do sistema.
Isolando essas funções da interface (Streamlit), garantimos a aplicação do Clean Code 
(Separação de Responsabilidades) e permitimos testes unitários precisos via Pytest.
"""

def formatar_moeda(valor):
    """
    Formata valores numéricos para o padrão de moeda brasileiro (BRL).
    Trata exceções de tipagem e valores nulos.
    """
    try:
        valor = float(valor or 0)
        numero = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {numero}"
    except (ValueError, TypeError):
        return "R$ 0,00"


def limpar_valor_fipe(valor_str):
    """
    Recebe a string suja da API da FIPE (ex: 'R$ 45.000,00') 
    e a converte em um float limpo (45000.0) para salvar no banco de dados.
    """
    try:
        if not isinstance(valor_str, str):
            return 0.0
        limpo = valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(limpo)
    except Exception:
        return 0.0


def calcular_lucro_bruto(valor_venda, valor_compra, custos_oficina=0):
    """
    Calcula o lucro bruto da transação financeira subtraindo 
    o valor de aquisição e os custos de manutenção do valor final de venda.
    """
    try:
        venda = float(valor_venda or 0)
        compra = float(valor_compra or 0)
        custos = float(custos_oficina or 0)
        return venda - (compra + custos)
    except Exception:
        return 0.0


def validar_rn01_venda(status_veiculo):
    """
    RN01: Validação de bloqueio logístico.
    O sistema só permite o faturamento de veículos que não estejam na oficina.
    """
    status_permitidos = ["Disponivel", "Disponível"]
    return status_veiculo in status_permitidos


def calcular_comissao(valor_venda, cargo):
    """
    Regra RH: Define a comissão baseada na hierarquia.
    Vendedores recebem 1% e Gerentes recebem 1.5% do valor da venda.
    """
    try:
        venda = float(valor_venda or 0)
        if venda <= 0:
            return 0.0
        cargo_str = str(cargo).strip().upper()
        if cargo_str == "VENDEDOR":
            return venda * 0.01
        elif cargo_str == "GERENTE":
            return venda * 0.015
        return 0.0
    except Exception:
        return 0.0


def limpar_e_validar_documento(doc):
    """
    Regra CRM: Remove máscaras (pontos e traços) e valida 
    se o documento é um CPF (11 dígitos) ou CNPJ (14 dígitos) válido.
    """
    try:
        if not isinstance(doc, str):
            return False
        limpo = ''.join(filter(str.isdigit, doc))
        return len(limpo) in [11, 14]
    except Exception:
        return False


def calcular_depreciacao_estoque(valor_fipe, dias_patio):
    """
    Regra Comercial: Se o veículo ficar mais de 90 dias parado no pátio,
    sofre uma remarcação (desconto automático de 5% sobre o valor).
    """
    try:
        valor = float(valor_fipe or 0)
        dias = int(dias_patio or 0)
        if valor <= 0 or dias < 0:
            return valor if valor > 0 else 0.0
        
        # Desconto de 5% após 90 dias
        if dias > 90:
            return valor * 0.95
        return valor
    except Exception:
        return 0.0


def validar_financiamento(ano_veiculo, score_cliente):
    """
    Regra Financeira: Avaliação de crédito para financiamento.
    Reprova veículos muito antigos (idade > 15 anos) ou clientes com score < 500.
    """
    try:
        ano = int(ano_veiculo)
        score = int(score_cliente)
        ano_atual = 2026 # Ano base considerado para o sistema
        idade = ano_atual - ano
        
        if idade > 15:
            return "Recusado: Veículo muito antigo"
        if score < 500:
            return "Recusado: Score baixo"
        return "Aprovado"
    except Exception:
        return "Erro na análise"