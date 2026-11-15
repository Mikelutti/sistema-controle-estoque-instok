"""Consultas de histórico, incluindo referências de cadastros inativos."""
from app.repositories import movimentacao_repository as repository


def listar_movimentacoes():
    return repository.listar_movimentacoes()
