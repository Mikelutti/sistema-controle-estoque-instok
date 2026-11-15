"""Regras de categorias, incluindo validações sob transação de escrita."""
from app.repositories import categoria_repository as repository
from app.services.cadastro_service import (
    RegistroNaoEncontrado, alteracao_administrativa, identificador, texto,
)


def listar_categorias():
    return repository.listar_categorias()


def obter_categoria(categoria_id, conexao=None):
    categoria_id = identificador(categoria_id)
    registro = repository.buscar_categoria(categoria_id, conexao)
    if registro is None:
        raise RegistroNaoEncontrado("Categoria não encontrada.")
    return registro


def validar_dados(nome, descricao):
    return dict(nome=texto(nome, "nome", 150), descricao=texto(descricao, "descrição", 2000, False))


def validar_duplicidade(nome, conexao, excluir_id=None):
    if repository.buscar_duplicado(nome, excluir_id, conexao):
        raise ValueError("Já existe uma categoria com esse nome, inclusive entre os inativos.")


def cadastrar_categoria(nome, descricao="", *, administrador_id):
    dados = validar_dados(nome, descricao)
    with alteracao_administrativa(administrador_id) as db:
        validar_duplicidade(dados["nome"], db)
        return repository.inserir_categoria(**dados, conexao=db)


def atualizar_categoria(categoria_id, nome, descricao="", *, administrador_id):
    dados = validar_dados(nome, descricao)
    with alteracao_administrativa(administrador_id) as db:
        atual = obter_categoria(categoria_id, db)
        validar_duplicidade(dados["nome"], db, atual["id"])
        repository.atualizar_categoria(atual["id"], **dados, conexao=db)


def inativar_categoria(categoria_id, *, administrador_id):
    with alteracao_administrativa(administrador_id) as db:
        atual = obter_categoria(categoria_id, db)
        repository.inativar_categoria(atual["id"], db)
