import pandas as pd
from database import supabase
from components.regras_negocio.formatar_reais import formatar_reais

NOMES_COLUNAS_AMIGAVEIS = {
    "id_transacao": "ID da Transação",
    "data": "Data da Venda",
    "placa_veiculo": "Placa do Veículo",
    "veiculo_modelo": "Modelo do Veículo",
    "cpf_cnpj_cliente": "CPF/CNPJ do Cliente",
    "cliente_nome": "Nome do Cliente",
    "matricula_funcionario": "Matrícula do Funcionário",
    "funcionario_nome": "Nome do Vendedor",
    "valor_final_negociado": "Valor Negociado",
}


def obter_dados_auditoria() -> pd.DataFrame:
    """Busca transações e enriquece com nomes legíveis de veículo, cliente e vendedor."""
    res_trans = supabase.table("transacao").select("*").execute()
    df_trans = pd.DataFrame(res_trans.data or [])
    if df_trans.empty:
        return pd.DataFrame()

    veiculos_data = supabase.table("veiculo").select("placa, modelo").execute().data or []
    clientes_data = supabase.table("cliente").select("cpf_cnpj, nome_completo").execute().data or []
    funcionarios_data = supabase.table("funcionario").select("matricula, nome").execute().data or []

    map_veiculos = {v["placa"]: v.get("modelo", "Modelo não informado") for v in veiculos_data}
    map_clientes = {c["cpf_cnpj"]: c.get("nome_completo", "Cliente não informado") for c in clientes_data}
    map_func = {f["matricula"]: f.get("nome", "Funcionário não informado") for f in funcionarios_data}

    df_exibicao = df_trans.copy()

    if "placa_veiculo" in df_exibicao.columns:
        df_exibicao["veiculo_modelo"] = df_exibicao["placa_veiculo"].map(map_veiculos).fillna(df_exibicao["placa_veiculo"])

    if "cpf_cnpj_cliente" in df_exibicao.columns:
        df_exibicao["cliente_nome"] = df_exibicao["cpf_cnpj_cliente"].map(map_clientes).fillna(df_exibicao["cpf_cnpj_cliente"])

    if "matricula_funcionario" in df_exibicao.columns:
        df_exibicao["funcionario_nome"] = df_exibicao["matricula_funcionario"].map(map_func).fillna(df_exibicao["matricula_funcionario"])

    colunas_finais = [col for col in NOMES_COLUNAS_AMIGAVEIS if col in df_exibicao.columns]
    df_final = df_exibicao[colunas_finais].rename(columns=NOMES_COLUNAS_AMIGAVEIS)

    if "Valor Negociado" in df_final.columns:
        df_final["Valor Negociado"] = pd.to_numeric(df_final["Valor Negociado"], errors="coerce").map(
            lambda x: formatar_reais(x) if pd.notna(x) else "R$ 0,00"
        )

    return df_final 