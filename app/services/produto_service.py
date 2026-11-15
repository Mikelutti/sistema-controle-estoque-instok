"""Cadastro de produtos sem alteração de estoque ou histórico."""
from app.repositories import produto_repository as repository, categoria_repository
from app.repositories.estoque_repository import produto_possui_saldo
from app.services.cadastro_service import (
    RegistroNaoEncontrado, alteracao_administrativa, identificador, inteiro, texto,
)


def listar_produtos():
    return repository.listar_produtos()


def obter_produto(produto_id, conexao=None):
    produto_id = identificador(produto_id)
    produto = repository.buscar_produto_por_id(produto_id, conexao)
    if produto is None:
        raise RegistroNaoEncontrado("Produto não encontrado.")
    return produto


def categorias_para_formulario(produto=None):
    return [c for c in categoria_repository.listar_categorias()
            if c["status"] == "ATIVO" or (produto is not None and c["id"] == produto["categoria_id"])]


def validar_dados(codigo, nome, descricao, categoria_id, estoque_minimo):
    return dict(codigo=texto(codigo, "código", 80), nome=texto(nome, "nome", 150),
                descricao=texto(descricao, "descrição", 2000, False),
                categoria_id=inteiro(categoria_id, "categoria", 1),
                estoque_minimo=inteiro(estoque_minimo, "estoque mínimo"))


def validar_relacoes(dados, conexao, atual=None):
    categoria = categoria_repository.buscar_categoria(dados["categoria_id"], conexao)
    if categoria is None:
        raise ValueError("Selecione uma categoria existente.")
    mantendo_vinculo = atual is not None and atual["categoria_id"] == categoria["id"]
    if categoria["status"] != "ATIVO" and not mantendo_vinculo:
        raise ValueError("Selecione uma categoria ativa para a nova associação.")
    if repository.buscar_duplicado(dados["codigo"], atual["id"] if atual else None, conexao):
        raise ValueError("Já existe um produto com esse código, inclusive entre os inativos.")


def cadastrar_produto(codigo, nome, descricao, categoria_id, estoque_minimo, *, administrador_id):
    dados = validar_dados(codigo, nome, descricao, categoria_id, estoque_minimo)
    with alteracao_administrativa(administrador_id) as db:
        validar_relacoes(dados, db)
        return repository.inserir_produto(**dados, conexao=db)


def atualizar_produto(produto_id, codigo, nome, descricao, categoria_id, estoque_minimo, *, administrador_id):
    dados = validar_dados(codigo, nome, descricao, categoria_id, estoque_minimo)
    with alteracao_administrativa(administrador_id) as db:
        atual = obter_produto(produto_id, db)
        validar_relacoes(dados, db, atual)
        repository.atualizar_produto(atual["id"], **dados, conexao=db)


def inativar_produto(produto_id, *, administrador_id):
    with alteracao_administrativa(administrador_id) as db:
        atual = obter_produto(produto_id, db)
        if produto_possui_saldo(atual["id"], db):
            raise ValueError("Não é possível inativar um produto com saldo em algum setor.")
        repository.inativar_produto(atual["id"], db)
