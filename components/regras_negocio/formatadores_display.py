from components.regras_negocio.formatar_reais import formatar_reais

def nome_cliente(cliente):
    return f"{cliente.get('nome_completo', 'Sem nome')} — {cliente.get('cpf_cnpj', '')}"

def nome_funcionario(funcionario):
    return f"{funcionario.get('nome', 'Sem nome')} — Matrícula {funcionario.get('matricula', '')}"

def nome_veiculo(veiculo):
    return f"{veiculo.get('placa', '')} — {veiculo.get('modelo', 'Modelo não informado')}"

def nome_transacao(transacao):
    return (
        f"Venda #{transacao.get('id_transacao')} — "
        f"{transacao.get('placa_veiculo', '')} — "
        f"{formatar_reais(transacao.get('valor_final_negociado', 0))}"
    )