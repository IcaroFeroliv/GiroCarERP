import pytest
from regras_negocio import calcular_lucro_bruto, validar_venda_rn01, formatar_moeda_br

# --- Testes de Cálculo de Lucro ---
def test_deve_calcular_lucro_corretamente():
    # Se comprou por 40k e vendeu por 50k, o lucro tem que ser 10k
    assert calcular_lucro_bruto(50000.0, 40000.0) == 10000.0

def test_deve_rejeitar_valores_negativos():
    # Garante que o sistema levanta um erro se o usuário digitar valor negativo
    with pytest.raises(ValueError, match="Os valores não podem ser negativos."):
        calcular_lucro_bruto(-5000, 40000)

# --- Testes da RN01 (Status do Veículo) ---
def test_deve_permitir_venda_de_veiculo_disponivel():
    assert validar_venda_rn01("Disponivel") == True
    assert validar_venda_rn01("disponivel") == True # Testa se ignora maiúsculas

def test_deve_bloquear_venda_de_veiculo_em_preparacao():
    assert validar_venda_rn01("Em preparacao") == False

def test_deve_bloquear_venda_de_veiculo_ja_vendido():
    assert validar_venda_rn01("Vendido") == False

# --- Testes de Formatação ---
def test_deve_formatar_moeda_no_padrao_brasileiro():
    assert formatar_moeda_br(45000.0) == "45.000,00"
    assert formatar_moeda_br(1250.50) == "1.250,50"
    assert formatar_moeda_br(0.0) == "0,00"

def test_deve_rejeitar_texto_na_formatacao_de_moeda():
    with pytest.raises(TypeError, match="O valor deve ser numérico."):
        formatar_moeda_br("cinquenta mil")

# --- Teste Extra de Lucro ---
def test_deve_retornar_zero_em_venda_sem_lucro():
    # Vendeu pelo mesmo preço que comprou (empate)
    assert calcular_lucro_bruto(30000.0, 30000.0) == 0.0