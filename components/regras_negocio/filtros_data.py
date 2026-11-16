import pandas as pd
import datetime

def filtrar_por_periodo(df, coluna_data, data_inicial, data_final):
    """Filtra um DataFrame garantindo que a data esteja dentro do período informado."""
    if df.empty or coluna_data not in df.columns:
        return df

    # Trata valores vazios/nulos
    df_temp = df.copy()
    
    # Cria máscara booleana: se for nulo OR estiver dentro do período
    mask = df_temp[coluna_data].isna() | (
        (df_temp[coluna_data] >= data_inicial) & (df_temp[coluna_data] <= data_final)
    )
    
    return df_temp[mask]