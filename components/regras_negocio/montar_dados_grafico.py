def montar_dados_grafico(df_vendas):
    df_lucro = df_vendas[["data", "placa_veiculo", "Lucro Bruto (R$)"]].sort_values("data")
    df_lucro["Veículo"] = (
        df_vendas["marca"] + " " + df_vendas["modelo"] + " (" + df_vendas["placa_veiculo"] + ")"
    )
    return df_lucro