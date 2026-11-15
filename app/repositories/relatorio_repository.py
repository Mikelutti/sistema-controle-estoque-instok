"""Consultas parametrizadas, sem escrita, para os relatórios."""
from app.database.connection import conexao_consulta


def consultar(f):
    movimento = f['relatorio'] == 'movimentacoes'
    if movimento:
        sql = ("SELECT m.id,m.data_hora,m.tipo,p.codigo,p.nome AS produto,"
               "c.nome AS categoria,m.quantidade,o.nome AS origem,d.nome AS destino,"
               "u.nome AS responsavel,m.observacao FROM movimentacoes m "
               "JOIN produtos p ON p.id=m.produto_id JOIN categorias c ON c.id=p.categoria_id "
               "JOIN usuarios u ON u.id=m.usuario_id "
               "LEFT JOIN setores o ON o.id=m.setor_origem_id "
               "LEFT JOIN setores d ON d.id=m.setor_destino_id WHERE 1=1")
    else:
        sql = ("SELECT p.id,p.codigo,p.nome AS produto,c.nome AS categoria,"
               "p.status,s.nome AS setor,COALESCE(e.quantidade,0) AS quantidade,"
               "p.estoque_minimo FROM produtos p JOIN categorias c ON c.id=p.categoria_id "
               "LEFT JOIN estoques e ON e.produto_id=p.id "
               "LEFT JOIN setores s ON s.id=e.setor_id WHERE 1=1")
    params=[]
    for campo,coluna in [('produto_id','p.id'),('categoria_id','p.categoria_id')]:
        if f[campo] is not None:
            sql += ' AND '+coluna+'=?'
            params.append(f[campo])
    if f['setor_id'] is not None:
        sql += ' AND (m.setor_origem_id=? OR m.setor_destino_id=?)' if movimento else ' AND e.setor_id=?'
        params.extend([f['setor_id']]* (2 if movimento else 1))
    if movimento:
        if f['inicio']:
            sql += ' AND m.data_hora>=?'
            params.append(f['inicio']+' 00:00:00')
        if f['fim']:
            sql += ' AND m.data_hora<=?'
            params.append(f['fim']+' 23:59:59')
        if f['tipo']:
            sql += ' AND m.tipo=?'
            params.append(f['tipo'])
        sql += ' ORDER BY m.data_hora DESC,m.id DESC'
    else:
        if f['relatorio']=='alertas':
            sql += " AND p.status='ATIVO'"
        sql += ' ORDER BY p.nome,p.id,s.nome,s.id'
    with conexao_consulta() as db:
        return [dict(r) for r in db.execute(sql,params).fetchall()]
