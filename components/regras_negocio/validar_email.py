import re

def validar_formato_email(email):
    """
    Valida se o e-mail possui um formato estrutural correto (ex: usuario@dominio.com).
    Retorna True se for válido, False caso contrário.
    """
    if not isinstance(email, str):
        return False
        
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(padrao, email.strip()))