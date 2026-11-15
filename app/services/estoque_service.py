"""Saldo e histórico são alterados juntos; nunca há commit parcial."""
from app.database.connection import transacao_escrita
from app.repositories import (
    estoque_repository as estoque, movimentacao_repository as movimentos,
    produto_repository as produtos, setor_repository as setores, usuario_repository as usuarios,
)
from app.services.cadastro_service import MAX_INTEIRO, inteiro, texto
from app.services.usuario_service import AcessoNegado

TIPOS = ("ENTRADA", "SAIDA", "TRANSFERENCIA")


def opcoes_movimentacao():
    return dict(produtos=[p for p in produtos.listar_produtos() if p["status"] == "ATIVO"],
                setores=[s for s in setores.listar_setores() if s["status"] == "ATIVO"])


def listar_inventario():
    return estoque.listar_inventario()


def validar_ator(usuario_id, conexao):
    if type(usuario_id) is not int or not 1 <= usuario_id <= MAX_INTEIRO:
        raise AcessoNegado("A operação exige um usuário ativo.")
    usuario = usuarios.buscar_usuario_por_id(usuario_id, conexao)
    if (usuario is None or usuario["status"] != "ATIVO"
            or usuario["nivel_acesso"] not in ("ADMINISTRADOR", "OPERADOR")):
        raise AcessoNegado("A operação exige um usuário ativo.")


def validar_setor(setor_id, conexao):
    setor = setores.buscar_setor(setor_id, conexao)
    if setor is None or setor["status"] != "ATIVO":
        raise ValueError("Selecione setores existentes e ativos.")


def movimentar(tipo, produto_id, quantidade, *, usuario_id, setor_origem_id=None,
               setor_destino_id=None, observacao=""):
    if tipo not in TIPOS:
        raise ValueError("Tipo de movimentação inválido.")
    produto_id = inteiro(produto_id, "produto", 1)
    quantidade = inteiro(quantidade, "quantidade", 1)
    observacao = texto(observacao, "motivo da movimentação", 2000)
    origem = inteiro(setor_origem_id, "setor de origem", 1) if tipo != "ENTRADA" else None
    destino = inteiro(setor_destino_id, "setor de destino", 1) if tipo != "SAIDA" else None
    if origem is not None and origem == destino:
        raise ValueError("Origem e destino devem ser setores diferentes.")

    with transacao_escrita() as db:
        validar_ator(usuario_id, db)
        produto = produtos.buscar_produto_por_id(produto_id, db)
        if produto is None or produto["status"] != "ATIVO":
            raise ValueError("Selecione um produto existente e ativo.")
        for setor_id in (origem, destino):
            if setor_id is not None:
                validar_setor(setor_id, db)
        if destino is not None:
            saldo = estoque.buscar_quantidade_por_setor(produto_id, destino, db)
            if saldo > MAX_INTEIRO - quantidade:
                raise ValueError("A operação excede o limite de saldo permitido no setor de destino.")
        if origem is not None:
            if not estoque.remover_quantidade(produto_id, origem, quantidade, db):
                raise ValueError("Saldo insuficiente no setor de origem.")
        if destino is not None:
            if not estoque.adicionar_quantidade(produto_id, destino, quantidade, db):
                raise ValueError("A operação excede o limite de saldo permitido no setor de destino.")
        return movimentos.registrar_movimentacao(
            produto_id=produto_id, usuario_id=usuario_id, tipo=tipo, quantidade=quantidade,
            setor_origem_id=origem, setor_destino_id=destino, observacao=observacao, conexao=db)
