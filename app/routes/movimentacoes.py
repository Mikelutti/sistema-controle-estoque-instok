"""
app/routes/movimentacoes.py

Modulo responsavel por: historico de movimentacoes de estoque
(entradas, saidas e transferencias ja realizadas).

Relacionamentos planejados:
- usuarios 1:N movimentacoes (quem realizou a movimentacao)
- produtos 1:N movimentacoes (qual produto foi movimentado)
"""

from flask import Blueprint, render_template

movimentacoes_bp = Blueprint("movimentacoes", __name__, url_prefix="/movimentacoes")


# TODO: listar historico de movimentacoes
@movimentacoes_bp.route("/")
def index():
    return render_template("movimentacoes/index.html")
