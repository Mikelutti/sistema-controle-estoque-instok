"""Validação e regras de usuários, independentes da camada HTTP."""
import re
import sqlite3
from werkzeug.security import generate_password_hash
from app.database.connection import transacao_escrita
from app.repositories import usuario_repository as repository

NIVEIS_ACESSO_PERMITIDOS = ("ADMINISTRADOR", "OPERADOR")


class UsuarioNaoEncontrado(ValueError):
    pass


class AcessoNegado(PermissionError):
    pass


def validar_dados(nome, usuario, email, nivel_acesso):
    dados = dict(nome=(nome or "").strip(), usuario=(usuario or "").strip(),
                 email=(email or "").strip().lower(),
                 nivel_acesso=(nivel_acesso or "").strip().upper())
    for campo, limite in (("nome", 150), ("usuario", 80), ("email", 254)):
        if not dados[campo] or len(dados[campo]) > limite:
            raise ValueError(f"O campo {campo} é obrigatório e deve ter até {limite} caracteres.")
    if any(c.isspace() for c in dados["usuario"]):
        raise ValueError("O usuário não pode conter espaços.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", dados["email"]):
        raise ValueError("Informe um e-mail válido.")
    if dados["nivel_acesso"] not in NIVEIS_ACESSO_PERMITIDOS:
        raise ValueError("Selecione um nível de acesso válido.")
    return dados


def validar_administrador(administrador_id, conexao):
    ator = repository.buscar_usuario_por_id(administrador_id, conexao)
    if not ator or ator["status"] != "ATIVO" or ator["nivel_acesso"] != "ADMINISTRADOR":
        raise AcessoNegado("A operação exige um administrador ativo.")


def validar_duplicidade(dados, conexao, excluir_id=None):
    duplicado = repository.buscar_duplicado(dados["usuario"], dados["email"], excluir_id, conexao)
    if duplicado:
        campo = "login" if duplicado["usuario"] == dados["usuario"] else "e-mail"
        raise ValueError(f"Já existe um usuário com esse {campo}, inclusive entre os inativos.")


def conflito_unicidade(erro):
    codigo = getattr(erro, "sqlite_errorcode", None)
    if codigo == sqlite3.SQLITE_CONSTRAINT_UNIQUE or (
            codigo is None and "UNIQUE constraint failed" in str(erro)):
        raise ValueError("Login ou e-mail já cadastrado. Confira os dados.") from None
    raise erro


def cadastrar_usuario(nome, usuario, email, senha, nivel_acesso, *, administrador_id=None):
    # Sem ator: API de bootstrap usada exclusivamente pelo script local criar_admin.py.
    # A rota web sempre fornece o ID autenticado; a autorização é revalidada sob lock.
    dados = validar_dados(nome, usuario, email, nivel_acesso)
    if not senha or not senha.strip() or not 8 <= len(senha) <= 256:
        raise ValueError("A senha deve ter entre 8 e 256 caracteres.")
    senha_hash = generate_password_hash(senha)
    try:
        with transacao_escrita() as db:
            if administrador_id is not None:
                validar_administrador(administrador_id, db)
            validar_duplicidade(dados, db)
            return repository.inserir_usuario(**dados, senha_hash=senha_hash, conexao=db)
    except sqlite3.IntegrityError as erro:
        conflito_unicidade(erro)


def listar_usuarios():
    return repository.listar_usuarios()


def obter_usuario(usuario_id, conexao=None):
    usuario = repository.buscar_usuario_por_id(usuario_id, conexao)
    if usuario is None:
        raise UsuarioNaoEncontrado("Usuário não encontrado.")
    return usuario


def proteger_ultimo_administrador(usuario, conexao):
    if (usuario["status"] == "ATIVO" and usuario["nivel_acesso"] == "ADMINISTRADOR"
            and repository.contar_administradores_ativos(conexao) <= 1):
        raise ValueError("Não é possível inativar ou remover o perfil do último administrador ativo.")


def editar_usuario(usuario_id, nome, usuario, email, nivel_acesso, *, administrador_id):
    dados = validar_dados(nome, usuario, email, nivel_acesso)
    try:
        with transacao_escrita() as db:
            validar_administrador(administrador_id, db)
            atual = obter_usuario(usuario_id, db)
            if dados["nivel_acesso"] != "ADMINISTRADOR":
                proteger_ultimo_administrador(atual, db)
            validar_duplicidade(dados, db, usuario_id)
            repository.atualizar_usuario(usuario_id, **dados, conexao=db)
    except sqlite3.IntegrityError as erro:
        conflito_unicidade(erro)


def inativar_usuario(usuario_id, *, administrador_id):
    with transacao_escrita() as db:
        validar_administrador(administrador_id, db)
        atual = obter_usuario(usuario_id, db)
        proteger_ultimo_administrador(atual, db)
        repository.inativar_usuario(usuario_id, db)
