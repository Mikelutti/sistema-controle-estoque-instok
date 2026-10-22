"""
app/services/auth_service.py

Responsabilidade:
- Validar as credenciais de login.
- Verificar se o usuario existe.
- Verificar se o usuario esta ativo.
- Comparar a senha informada com o hash armazenado no banco.

Este service nunca armazena ou compara senhas em texto puro.
"""

from werkzeug.security import check_password_hash

from app.repositories.usuario_repository import buscar_usuario_por_login


def validar_usuario_ativo(usuario):
    """
    Verifica se o usuario pode acessar o sistema.
    """

    if usuario["status"] != "ATIVO":
        raise ValueError("Usuario inativo.")

    return True


def verificar_senha(usuario, senha):
    """
    Compara a senha informada com o hash armazenado.
    """

    return check_password_hash(
        usuario["senha_hash"],
        senha,
    )


def validar_login(login, senha):
    """
    Valida as credenciais informadas no login.

    Retorna o usuario quando as credenciais forem validas.
    """

    if not login or not login.strip():
        raise ValueError("Informe o usuario.")

    if not senha:
        raise ValueError("Informe a senha.")

    usuario = buscar_usuario_por_login(login.strip())

    if usuario is None:
        raise ValueError("Usuario ou senha invalidos.")

    validar_usuario_ativo(usuario)

    if not verificar_senha(usuario, senha):
        raise ValueError("Usuario ou senha invalidos.")

    return usuario