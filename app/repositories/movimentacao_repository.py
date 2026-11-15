"""Persistência do histórico; nenhuma operação de alteração ou exclusão."""
from app.database.connection import conexao_consulta


def registrar_movimentacao(produto_id, usuario_id, tipo, quantidade, setor_origem_id,
                          setor_destino_id, observacao, conexao):
    return conexao.execute(
        "INSERT INTO movimentacoes(produto_id,usuario_id,tipo,quantidade,"
        "setor_origem_id,setor_destino_id,observacao) VALUES (?,?,?,?,?,?,?)",
        (produto_id, usuario_id, tipo, quantidade, setor_origem_id,
         setor_destino_id, observacao)).lastrowid


def listar_movimentacoes(conexao=None):
    with conexao_consulta(conexao) as db:
        return db.execute(
            "SELECT m.id,m.tipo,m.quantidade,m.observacao,m.data_hora,"
            "p.codigo,p.nome AS produto_nome,u.usuario AS usuario_login,u.nome AS usuario_nome,"
            "origem.nome AS origem_nome,destino.nome AS destino_nome "
            "FROM movimentacoes m JOIN produtos p ON p.id=m.produto_id "
            "JOIN usuarios u ON u.id=m.usuario_id "
            "LEFT JOIN setores origem ON origem.id=m.setor_origem_id "
            "LEFT JOIN setores destino ON destino.id=m.setor_destino_id "
            "ORDER BY m.data_hora DESC,m.id DESC").fetchall()
