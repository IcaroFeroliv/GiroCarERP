import pandas as pd
from database import supabase

def carregar_dados():
    res_veiculos = (
        supabase.table("veiculo")
        .select("placa, modelo, marca, valor_aquisicao, status_veiculo")
        .execute()
    )
    res_transacoes = (
        supabase.table("transacao")
        .select("placa_veiculo, valor_final_negociado, data")
        .execute()
    )
    return pd.DataFrame(res_veiculos.data), pd.DataFrame(res_transacoes.data)