import streamlit as st
from database import supabase
from components.regras_negocio.obter_dados import obter_dados
from components.regras_negocio.mostrar_erro import mostrar_erro
from components.regras_negocio.formatadores_display import nome_transacao

def render_form_pagamento():
    transacoes_pagamento = obter_dados("transacao", "id_transacao, placa_veiculo, valor_final_negociado")

    if not transacoes_pagamento:
        st.info("Registre uma venda antes de lançar um pagamento.")
        return

    modalidades = ["PIX", "Financiamento", "Cartão de Credito", "Transferência", "Dinheiro", "Consórcio"]

    with st.form("form_lancar_pagamento", clear_on_submit=True):
        transacao_selecionada = st.selectbox("Venda relacionada", options=transacoes_pagamento, format_func=nome_transacao)
        modalidade = st.selectbox("Modalidade de pagamento", options=modalidades)

        col1, col2 = st.columns(2)
        with col1:
            valor_pagamento = st.number_input("Valor da transação (R$)", min_value=0.1, step=500.0, format="%.2f")
            numero_parcelas = st.number_input("Número de parcelas", min_value=1, step=1, value=1)
        with col2:
            instituicao = st.text_input("Instituição processadora", placeholder="Ex.: nome do banco ou operadora")
            taxa_juros = st.number_input(
                "Taxa de juros", min_value=0.0, step=0.5, format="%.2f",
                help="Informe a taxa no formato numérico utilizado pelo sistema."
            )

        confirmar_pagamento = st.form_submit_button("Registrar pagamento", type="primary", width="stretch")

    if confirmar_pagamento:
        dados_pagamento = {
            "id_transacao": transacao_selecionada["id_transacao"],
            "modalidade_pagamento": modalidade,
            "valor_transacao": valor_pagamento,
            "numero_parcelas": int(numero_parcelas),
            "instituicao_processadora": instituicao.strip(),
            "taxa_juros": taxa_juros,
        }

        try:
            resposta = supabase.table("pagamento").insert(dados_pagamento).execute()
            if resposta.data:
                st.success("Pagamento registrado com sucesso!")
                st.rerun()
            else:
                st.warning("O banco não retornou a confirmação do pagamento. Verifique os registros antes de tentar novamente.")
        except Exception as erro:
            mostrar_erro("registrar o pagamento", erro)