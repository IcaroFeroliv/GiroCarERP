import streamlit as st
from components.comercial.form_pagamento import render_form_pagamento

def render_aba_pagamento():
    st.subheader("Lançar pagamento")
    st.caption("Registre os dados do pagamento de uma venda existente.")
    render_form_pagamento()