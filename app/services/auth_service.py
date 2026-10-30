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

from app.repositories.usuario_repository import buscar_usuario_por_id, buscar_usuario_por_login


def dados_publicos(usuario):
    return {campo: usuario[campo] for campo in ("id", "nome", "nivel_acesso")}


def obter_usuario_autenticado(usuario_id):
    """Revalida status e perfil no banco em cada requisição autenticada."""
    if type(usuario_id) is not int or usuario_id <= 0:
        return None
    usuario = buscar_usuario_por_id(usuario_id)
    if (usuario is None or usuario["status"] != "ATIVO"
            or usuario["nivel_acesso"] not in ("ADMINISTRADOR", "OPERADOR")):
        return None
    return dados_publicos(usuario)


def validar_usuario_ativo(usuario):
    """
    Verifica se o usuario pode acessar o sistema.
    """

    if usuario["status"] != "ATIVO":
        raise ValueError("Usuario ou senha invalidos.")

    return True


def verificar_senha(usuario, senha):
    """
    Compara a senha informada com o hash armazenado.
    """

    try:
        return check_password_hash(usuario["senha_hash"], senha)
    except (ValueError, TypeError):
        # Registros antigos/irregulares nunca usam comparação em texto puro.
        return False


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

    return dados_publicos(usuario)
