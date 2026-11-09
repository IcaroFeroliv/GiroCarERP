def filtrar_texto_contem(df, coluna, texto):
    return df[df[coluna].str.contains(texto)] if texto else df