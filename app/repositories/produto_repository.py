"""SQL de produtos; saldos pertencem exclusivamente ao repository de estoque."""
from app.database.connection import conexao_consulta


def listar_produtos(conexao=None):
    with conexao_consulta(conexao) as db:
        return db.execute(
            "SELECT p.*, c.nome AS categoria_nome, c.status AS categoria_status "
            "FROM produtos p JOIN categorias c ON c.id=p.categoria_id ORDER BY p.nome,p.id"
        ).fetchall()


def buscar_produto_por_id(produto_id, conexao=None):
    with conexao_consulta(conexao) as db:
        return db.execute("SELECT * FROM produtos WHERE id=?", (produto_id,)).fetchone()


def buscar_produto_por_codigo(codigo, conexao=None):
    with conexao_consulta(conexao) as db:
        return db.execute("SELECT * FROM produtos WHERE codigo=?", (codigo,)).fetchone()


def buscar_duplicado(codigo, excluir_id, conexao):
    return conexao.execute("SELECT id FROM produtos WHERE codigo=? AND (? IS NULL OR id<>?)",
                          (codigo, excluir_id, excluir_id)).fetchone()


def inserir_produto(codigo, nome, descricao, categoria_id, estoque_minimo, conexao):
    return conexao.execute(
        "INSERT INTO produtos(codigo,nome,descricao,categoria_id,estoque_minimo) VALUES (?,?,?,?,?)",
        (codigo, nome, descricao, categoria_id, estoque_minimo)).lastrowid


def atualizar_produto(produto_id, codigo, nome, descricao, categoria_id, estoque_minimo, conexao):
    return conexao.execute(
        "UPDATE produtos SET codigo=?,nome=?,descricao=?,categoria_id=?,estoque_minimo=? WHERE id=?",
        (codigo, nome, descricao, categoria_id, estoque_minimo, produto_id)).rowcount


def inativar_produto(produto_id, conexao):
    return conexao.execute("UPDATE produtos SET status='INATIVO' WHERE id=?", (produto_id,)).rowcount


def consultar_estoque_minimo(produto_id):
    produto = buscar_produto_por_id(produto_id)
    return produto["estoque_minimo"] if produto else None
