"""SQL de saldos. Escritas compartilham a transação de movimentação do service."""
from app.database.connection import conexao_consulta

MAX_INTEIRO = 9223372036854775807


def buscar_quantidade_por_setor(produto_id, setor_id, conexao=None):
    with conexao_consulta(conexao) as db:
        row = db.execute("SELECT quantidade FROM estoques WHERE produto_id=? AND setor_id=?",
                         (produto_id, setor_id)).fetchone()
        return row["quantidade"] if row else 0


def setor_possui_saldo(setor_id, conexao):
    return conexao.execute(
        "SELECT 1 FROM estoques WHERE setor_id=? AND quantidade>0 LIMIT 1",
        (setor_id,)).fetchone() is not None


def produto_possui_saldo(produto_id, conexao):
    return conexao.execute(
        "SELECT 1 FROM estoques WHERE produto_id=? AND quantidade>0 LIMIT 1",
        (produto_id,)).fetchone() is not None


def adicionar_quantidade(produto_id, setor_id, quantidade, conexao):
    return conexao.execute(
        "INSERT INTO estoques(produto_id,setor_id,quantidade) VALUES (?,?,?) "
        "ON CONFLICT(produto_id,setor_id) DO UPDATE SET quantidade=estoques.quantidade+excluded.quantidade "
        "WHERE estoques.quantidade<=?",
        (produto_id, setor_id, quantidade, MAX_INTEIRO-quantidade)).rowcount


def remover_quantidade(produto_id, setor_id, quantidade, conexao):
    return conexao.execute(
        "UPDATE estoques SET quantidade=quantidade-? "
        "WHERE produto_id=? AND setor_id=? AND quantidade>=?",
        (quantidade, produto_id, setor_id, quantidade)).rowcount


def listar_inventario(conexao=None):
    # LEFT JOIN também apresenta produto que nunca teve registro de saldo.
    with conexao_consulta(conexao) as db:
        return db.execute(
            "SELECT p.id AS produto_id,p.codigo,p.nome AS produto_nome,p.status AS produto_status,"
            "p.estoque_minimo,c.nome AS categoria_nome,s.id AS setor_id,s.nome AS setor_nome,"
            "s.status AS setor_status,COALESCE(e.quantidade,0) AS quantidade "
            "FROM produtos p JOIN categorias c ON c.id=p.categoria_id "
            "LEFT JOIN estoques e ON e.produto_id=p.id LEFT JOIN setores s ON s.id=e.setor_id "
            "ORDER BY p.nome,p.id,s.nome,s.id").fetchall()


def somar_quantidade_total(produto_id, conexao=None):
    # SUM INTEGER SQLite pode estourar ao somar saldos válidos de vários setores.
    with conexao_consulta(conexao) as db:
        return sum(row["quantidade"] for row in db.execute(
            "SELECT quantidade FROM estoques WHERE produto_id=?", (produto_id,)))
