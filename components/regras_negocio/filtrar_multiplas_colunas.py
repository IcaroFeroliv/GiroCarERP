def filtrar_multiplas_colunas(df, colunas, termo):
    """
    Realiza uma busca textual ignorando maiúsculas/minúsculas 
    em múltiplas colunas de um DataFrame simultaneamente.
    """
    if not termo:
        return df
        
    colunas_presentes = [col for col in colunas if col in df.columns]
    if not colunas_presentes:
        return df

    encontrados = (
        df[colunas_presentes]
        .fillna("")
        .astype(str)
        .apply(lambda col: col.str.contains(termo, case=False, regex=False))
        .any(axis=1)
    )
    return df[encontrados]