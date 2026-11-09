def filtrar_em_lista(df, coluna, valores):
    return df[df[coluna].isin(valores)] if valores else df