"""SQL de categorias; escritas recebem a conexão transacional do service."""
from app.database.connection import conexao_consulta


def listar_categorias(conexao=None):
    with conexao_consulta(conexao) as db:
        return db.execute("SELECT * FROM categorias ORDER BY nome, id").fetchall()


def buscar_categoria(categoria_id, conexao=None):
    with conexao_consulta(conexao) as db:
        return db.execute("SELECT * FROM categorias WHERE id=?", (categoria_id,)).fetchone()


def buscar_duplicado(nome, excluir_id, conexao):
    return conexao.execute(
        "SELECT id FROM categorias WHERE nome=? AND (? IS NULL OR id<>?)",
        (nome, excluir_id, excluir_id)).fetchone()


def inserir_categoria(nome, descricao, conexao):
    return conexao.execute("INSERT INTO categorias(nome,descricao) VALUES (?,?)",
                          (nome, descricao)).lastrowid


def atualizar_categoria(categoria_id, nome, descricao, conexao):
    return conexao.execute("UPDATE categorias SET nome=?, descricao=? WHERE id=?",
                          (nome, descricao, categoria_id)).rowcount


def inativar_categoria(categoria_id, conexao):
    return conexao.execute("UPDATE categorias SET status='INATIVO' WHERE id=?",
                          (categoria_id,)).rowcount
