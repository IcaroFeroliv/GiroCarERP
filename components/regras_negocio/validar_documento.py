def limpar_e_validar_documento(documento):
    """
    Remove máscaras e valida se o CPF/CNPJ possui o tamanho correto.
    Retorna True se for válido, False caso contrário.
    """
    if not isinstance(documento, str):
        return False
        
    doc_limpo = "".join([c for c in documento if c.isdigit()])
    
    if len(doc_limpo) not in (11, 14):
        return False
        
    return True