"""Classificação global de produtos ativos, recalculada em cada consulta."""
from app.repositories.estoque_repository import listar_inventario


def verificar_sem_estoque(quantidade):
    return quantidade == 0


def verificar_estoque_baixo(quantidade, estoque_minimo):
    return 0 < quantidade <= estoque_minimo


def obter_status_estoque(quantidade, estoque_minimo):
    if verificar_sem_estoque(quantidade):
        return 'SEM ESTOQUE'
    if verificar_estoque_baixo(quantidade, estoque_minimo):
        return 'ESTOQUE BAIXO'
    return 'ESTOQUE NORMAL'


def obter_resumo():
    # Uma consulta garante que os indicadores partam do mesmo retrato do saldo.
    # A soma em Python suporta totais maiores que o INTEGER do SQLite.
    produtos = {}
    for row in listar_inventario():
        if row['produto_status'] != 'ATIVO':
            continue
        produto = produtos.setdefault(row['produto_id'], dict(
            id=row['produto_id'], codigo=row['codigo'], nome=row['produto_nome'],
            categoria=row['categoria_nome'], minimo=row['estoque_minimo'], quantidade=0))
        produto['quantidade'] += row['quantidade']
    sem_estoque, baixo = [], []
    normal = 0
    for produto in produtos.values():
        status = obter_status_estoque(produto['quantidade'], produto['minimo'])
        if status == 'SEM ESTOQUE':
            sem_estoque.append(produto)
        elif status == 'ESTOQUE BAIXO':
            baixo.append(produto)
        else:
            normal += 1
    return dict(total_produtos=len(produtos),
                total_unidades=sum(p['quantidade'] for p in produtos.values()),
                total_normal=normal, sem_estoque=sem_estoque, estoque_baixo=baixo)
