import unicodedata
from database import supabase

CREDENCIAIS_GERENTES = {
    "icaro@girocar.com": "Icaro2026",
    "kaio@girocar.com": "Kaio2026",
    "erick@girocar.com": "Erick2026",
}


def normalizar_texto(texto: str) -> str:
    """Remove acentos, espaços e converte para minúsculas para padronizar o login."""
    if not texto:
        return ""
    nfkd_form = unicodedata.normalize("NFKD", str(texto))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().replace(" ", "")


def autenticar_gerente(email_digitado: str, senha_limpa: str) -> tuple[bool, str, str]:
    """Valida credenciais de gerente pelo e-mail autorizado e senha."""
    email_normalizado = (email_digitado or "").strip().lower()
    if email_normalizado not in CREDENCIAIS_GERENTES:
        return False, "", ""

    if senha_limpa == CREDENCIAIS_GERENTES[email_normalizado]:
        return True, email_normalizado, "Login efetuado com sucesso como Gerente!"

    return False, "", "Senha incorreta para o perfil de Gerente."


def autenticar_vendedor(usuario_digitado: str, senha_limpa: str) -> tuple[bool, str, str]:
    """Valida vendedor pelo nome completo sem espaços/acentos e matrícula como senha."""
    if not supabase:
        return False, "", "Conexão com o banco de dados indisponível."

    entrada_limpa = normalizar_texto(usuario_digitado)
    res = supabase.table("funcionario").select("*").execute()
    funcionarios = res.data or []

    for func in funcionarios:
        nome_banco = func.get("nome", "")
        nome_formatado = normalizar_texto(nome_banco)
        matricula_banco = str(func.get("matricula", "")).strip()

        if entrada_limpa == nome_formatado and senha_limpa == matricula_banco:
            nome_exibicao = nome_banco or entrada_limpa
            return True, nome_exibicao, f"Login efetuado com sucesso, {nome_exibicao}!"

    return False, "", (
        "Usuário ou senha inválidos. Vendedor: digite o nome completo sem espaços e a matrícula como senha."
    )