import pandas as pd
from components.regras_negocio.constantes import STATUS_DISPONIVEL, STATUS_PREPARACAO

def calcular_estoque(df_veiculos):
    df_preparacao = pd.DataFrame()
    if df_veiculos.empty:
        return 0, 0, 0.0, df_preparacao

    df_disponivel = df_veiculos[df_veiculos["status_veiculo"] == STATUS_DISPONIVEL]
    df_preparacao = df_veiculos[df_veiculos["status_veiculo"] == STATUS_PREPARACAO]

    capital = (
        df_disponivel["valor_aquisicao"].sum()
        + df_preparacao["valor_aquisicao"].sum()
    )
    return len(df_disponivel), len(df_preparacao), capital, df_preparacao