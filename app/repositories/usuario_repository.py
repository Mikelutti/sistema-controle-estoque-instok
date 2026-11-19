"""SQL de usuários; operações compostas compartilham a transação do service."""
from contextlib import contextmanager
from app.database.connection import obter_conexao

COLUNAS_PUBLICAS = "id, nome, usuario, email, nivel_acesso, status, data_cadastro"


@contextmanager
def conexao_usuario(conexao=None):
    if conexao is not None:
        yield conexao
    else:
        db = obter_conexao()
        try:
            with db:
                yield db
        finally:
            db.close()


def buscar_usuario_por_id(usuario_id, conexao=None):
    with conexao_usuario(conexao) as db:
        return db.execute("SELECT " + COLUNAS_PUBLICAS + " FROM usuarios WHERE id=?",
                          (usuario_id,)).fetchone()


def buscar_usuario_por_login(login, conexao=None):
    # Única consulta que entrega hash: usada pela autenticação.
    with conexao_usuario(conexao) as db:
        return db.execute("SELECT * FROM usuarios WHERE usuario=?", (login,)).fetchone()


def buscar_usuario_por_email(email, conexao=None):
    with conexao_usuario(conexao) as db:
        return db.execute("SELECT " + COLUNAS_PUBLICAS +
                          " FROM usuarios WHERE lower(trim(email))=?", (email,)).fetchone()


def listar_usuarios(conexao=None):
    with conexao_usuario(conexao) as db:
        return db.execute("SELECT " + COLUNAS_PUBLICAS +
                          " FROM usuarios ORDER BY nome COLLATE NOCASE, id").fetchall()


def buscar_duplicado(usuario, email, excluir_id=None, conexao=None):
    with conexao_usuario(conexao) as db:
        return db.execute(
            "SELECT usuario, email FROM usuarios WHERE (usuario=? OR lower(trim(email))=?) "
            "AND (? IS NULL OR id<>?) LIMIT 1",
            (usuario, email, excluir_id, excluir_id)).fetchone()


def contar_administradores_ativos(conexao):
    return conexao.execute("SELECT count(*) FROM usuarios WHERE status='ATIVO' "
                           "AND nivel_acesso='ADMINISTRADOR'").fetchone()[0]


def inserir_usuario(nome, usuario, email, senha_hash, nivel_acesso, conexao=None):
    with conexao_usuario(conexao) as db:
        return db.execute(
            "INSERT INTO usuarios(nome,usuario,email,senha_hash,nivel_acesso) VALUES (?,?,?,?,?)",
            (nome, usuario, email, senha_hash, nivel_acesso)).lastrowid


def atualizar_usuario(usuario_id, nome, usuario, email, nivel_acesso, conexao=None):
    with conexao_usuario(conexao) as db:
        return db.execute("UPDATE usuarios SET nome=?, usuario=?, email=?, nivel_acesso=? WHERE id=?",
                          (nome, usuario, email, nivel_acesso, usuario_id)).rowcount


def inativar_usuario(usuario_id, conexao=None):
    with conexao_usuario(conexao) as db:
        return db.execute("UPDATE usuarios SET status='INATIVO' WHERE id=?", (usuario_id,)).rowcount
