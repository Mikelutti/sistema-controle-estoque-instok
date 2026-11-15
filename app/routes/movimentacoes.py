"""Histórico de estoque somente para consulta por usuários autenticados."""
from flask import Blueprint, render_template
from app.services import movimentacao_service as service

movimentacoes_bp = Blueprint("movimentacoes", __name__, url_prefix="/movimentacoes")


@movimentacoes_bp.get("/")
def index():
    return render_template("movimentacoes/index.html", registros=service.listar_movimentacoes())
