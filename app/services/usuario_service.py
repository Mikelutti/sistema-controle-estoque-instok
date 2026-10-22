"""
app/services/usuario_service.py

Responsabilidade:
- Aplicar as regras de negocio relacionadas aos usuarios.
- Validar dados antes de envia-los ao repository.
- Gerar hash seguro das senhas.
- Impedir usuarios duplicados.
- Controlar os niveis de acesso permitidos.
"""

from werkzeug.security import generate_password_hash

from app.repositories.usuario_repository import (
    buscar_usuario_por_email,
    buscar_usuario_por_login,
    inserir_usuario,
    inativar_usuario as repository_inativar_usuario,
)


NIVEIS_ACESSO_PERMITIDOS = (
    "ADMINISTRADOR",
    "OPERADOR",
)


def validar_campos_obrigatorios(
    nome,
    usuario,
    email,
    senha,
    nivel_acesso,
):
    if not nome or not nome.strip():
        raise ValueError("O nome e obrigatorio.")

    if not usuario or not usuario.strip():
        raise ValueError("O usuario e obrigatorio.")

    if not email or not email.strip():
        raise ValueError("O e-mail e obrigatorio.")

    if not senha:
        raise ValueError("A senha e obrigatoria.")

    if not nivel_acesso:
        raise ValueError("O nivel de acesso e obrigatorio.")


def validar_usuario_duplicado(usuario, email):
    usuario_existente = buscar_usuario_por_login(usuario)

    if usuario_existente:
        raise ValueError("Ja existe um usuario com esse login.")

    email_existente = buscar_usuario_por_email(email)

    if email_existente:
        raise ValueError("Ja existe um usuario com esse e-mail.")


def controlar_nivel_acesso(nivel_acesso):
    nivel_acesso = nivel_acesso.upper()

    if nivel_acesso not in NIVEIS_ACESSO_PERMITIDOS:
        raise ValueError(
            "Nivel de acesso invalido. "
            "Use ADMINISTRADOR ou OPERADOR."
        )

    return nivel_acesso


def gerar_hash_senha(senha):
    return generate_password_hash(senha)


def validar_cadastro(
    nome,
    usuario,
    email,
    senha,
    nivel_acesso,
):
    validar_campos_obrigatorios(
        nome,
        usuario,
        email,
        senha,
        nivel_acesso,
    )

    nivel_acesso = controlar_nivel_acesso(nivel_acesso)

    validar_usuario_duplicado(
        usuario.strip(),
        email.strip(),
    )

    return nivel_acesso


def cadastrar_usuario(
    nome,
    usuario,
    email,
    senha,
    nivel_acesso,
):
    nivel_acesso = validar_cadastro(
        nome,
        usuario,
        email,
        senha,
        nivel_acesso,
    )

    senha_hash = gerar_hash_senha(senha)

    usuario_id = inserir_usuario(
        nome=nome.strip(),
        usuario=usuario.strip(),
        email=email.strip().lower(),
        senha_hash=senha_hash,
        nivel_acesso=nivel_acesso,
    )

    return usuario_id


def inativar_usuario(usuario_id):
    if not usuario_id:
        raise ValueError("ID do usuario invalido.")

    linhas_alteradas = repository_inativar_usuario(usuario_id)

    if linhas_alteradas == 0:
        raise ValueError("Usuario nao encontrado.")

    return True