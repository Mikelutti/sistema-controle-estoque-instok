"""SQL de setores; escritas recebem a conexão transacional do service."""
from app.database.connection import conexao_consulta


def listar_setores(conexao=None):
    with conexao_consulta(conexao) as db:
        return db.execute("SELECT * FROM setores ORDER BY nome, id").fetchall()


def buscar_setor(setor_id, conexao=None):
    with conexao_consulta(conexao) as db:
        return db.execute("SELECT * FROM setores WHERE id=?", (setor_id,)).fetchone()


def buscar_duplicado(nome, excluir_id, conexao):
    return conexao.execute(
        "SELECT id FROM setores WHERE nome=? AND (? IS NULL OR id<>?)",
        (nome, excluir_id, excluir_id)).fetchone()


def inserir_setor(nome, descricao, conexao):
    return conexao.execute("INSERT INTO setores(nome,descricao) VALUES (?,?)",
                          (nome, descricao)).lastrowid


def atualizar_setor(setor_id, nome, descricao, conexao):
    return conexao.execute("UPDATE setores SET nome=?, descricao=? WHERE id=?",
                          (nome, descricao, setor_id)).rowcount


def inativar_setor(setor_id, conexao):
    return conexao.execute("UPDATE setores SET status='INATIVO' WHERE id=?",
                          (setor_id,)).rowcount
