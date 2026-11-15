"""Regras de setores, incluindo validações sob transação de escrita."""
from app.repositories import setor_repository as repository
from app.repositories.estoque_repository import setor_possui_saldo
from app.services.cadastro_service import (
    RegistroNaoEncontrado, alteracao_administrativa, identificador, texto,
)


def listar_setores():
    return repository.listar_setores()


def obter_setor(setor_id, conexao=None):
    setor_id = identificador(setor_id)
    registro = repository.buscar_setor(setor_id, conexao)
    if registro is None:
        raise RegistroNaoEncontrado("Setor não encontrado.")
    return registro


def validar_dados(nome, descricao):
    return dict(nome=texto(nome, "nome", 150), descricao=texto(descricao, "descrição", 2000, False))


def validar_duplicidade(nome, conexao, excluir_id=None):
    if repository.buscar_duplicado(nome, excluir_id, conexao):
        raise ValueError("Já existe um setor com esse nome, inclusive entre os inativos.")


def cadastrar_setor(nome, descricao="", *, administrador_id):
    dados = validar_dados(nome, descricao)
    with alteracao_administrativa(administrador_id) as db:
        validar_duplicidade(dados["nome"], db)
        return repository.inserir_setor(**dados, conexao=db)


def atualizar_setor(setor_id, nome, descricao="", *, administrador_id):
    dados = validar_dados(nome, descricao)
    with alteracao_administrativa(administrador_id) as db:
        atual = obter_setor(setor_id, db)
        validar_duplicidade(dados["nome"], db, atual["id"])
        repository.atualizar_setor(atual["id"], **dados, conexao=db)


def inativar_setor(setor_id, *, administrador_id):
    with alteracao_administrativa(administrador_id) as db:
        atual = obter_setor(setor_id, db)
        if setor_possui_saldo(atual["id"], db):
            raise ValueError("Não é possível inativar um setor com saldo de estoque.")
        repository.inativar_setor(atual["id"], db)
