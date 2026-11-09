import pandas as pd

def preparar_vendas(df_transacoes, df_veiculos):
    df_vendas = pd.merge(
        df_transacoes, df_veiculos, left_on="placa_veiculo", right_on="placa"
    )
    df_vendas["Lucro Bruto (R$)"] = (
        df_vendas["valor_final_negociado"] - df_vendas["valor_aquisicao"]
    )
    df_vendas["data"] = pd.to_datetime(df_vendas["data"])
    df_vendas["mes_ano"] = df_vendas["data"].dt.strftime("%m/%Y")
    return df_vendas