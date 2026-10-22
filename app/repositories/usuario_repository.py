"""
app/repositories/usuario_repository.py

Responsabilidade:
- Executar o SQL relacionado a tabela usuarios.
- Nao conter regras de negocio.
- Utilizar a conexao definida em app/database/connection.py.
"""

from app.database.connection import obter_conexao, fechar_conexao


def buscar_usuario_por_id(usuario_id):
    conexao = obter_conexao()

    try:
        usuario = conexao.execute(
            """
            SELECT *
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,),
        ).fetchone()

        return usuario

    finally:
        fechar_conexao(conexao)


def buscar_usuario_por_login(login):
    conexao = obter_conexao()

    try:
        usuario = conexao.execute(
            """
            SELECT *
            FROM usuarios
            WHERE usuario = ?
            """,
            (login,),
        ).fetchone()

        return usuario

    finally:
        fechar_conexao(conexao)


def buscar_usuario_por_email(email):
    conexao = obter_conexao()

    try:
        usuario = conexao.execute(
            """
            SELECT *
            FROM usuarios
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

        return usuario

    finally:
        fechar_conexao(conexao)


def listar_usuarios():
    conexao = obter_conexao()

    try:
        usuarios = conexao.execute(
            """
            SELECT *
            FROM usuarios
            WHERE status = 'ATIVO'
            ORDER BY nome
            """
        ).fetchall()

        return usuarios

    finally:
        fechar_conexao(conexao)


def inserir_usuario(nome, usuario, email, senha_hash, nivel_acesso):
    conexao = obter_conexao()

    try:
        cursor = conexao.execute(
            """
            INSERT INTO usuarios
            (
                nome,
                usuario,
                email,
                senha_hash,
                nivel_acesso
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                nome,
                usuario,
                email,
                senha_hash,
                nivel_acesso,
            ),
        )

        conexao.commit()

        return cursor.lastrowid

    except Exception:
        conexao.rollback()
        raise

    finally:
        fechar_conexao(conexao)


def atualizar_usuario(
    usuario_id,
    nome,
    usuario,
    email,
    nivel_acesso,
):
    conexao = obter_conexao()

    try:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET
                nome = ?,
                usuario = ?,
                email = ?,
                nivel_acesso = ?
            WHERE id = ?
            """,
            (
                nome,
                usuario,
                email,
                nivel_acesso,
                usuario_id,
            ),
        )

        conexao.commit()

        return cursor.rowcount

    except Exception:
        conexao.rollback()
        raise

    finally:
        fechar_conexao(conexao)


def inativar_usuario(usuario_id):
    conexao = obter_conexao()

    try:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET status = 'INATIVO'
            WHERE id = ?
            """,
            (usuario_id,),
        )

        conexao.commit()

        return cursor.rowcount

    except Exception:
        conexao.rollback()
        raise

    finally:
        fechar_conexao(conexao)