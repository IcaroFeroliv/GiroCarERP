import pandas as pd

def calcular_kpis_comercial(df_vendas):
    total_vendas = len(df_vendas)
    
    if not df_vendas.empty and "valor_final_negociado" in df_vendas.columns:
        valores = pd.to_numeric(df_vendas["valor_final_negociado"], errors="coerce").fillna(0)
        faturamento_negociado = float(valores.sum())
    else:
        faturamento_negociado = 0.0

    ticket_medio = (faturamento_negociado / total_vendas) if total_vendas > 0 else 0.0
    
    return total_vendas, faturamento_negociado, ticket_medio