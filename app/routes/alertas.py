"""
app/routes/alertas.py

Modulo responsavel por: produtos com estoque baixo ou sem estoque.

A logica de classificacao (SEM ESTOQUE / ESTOQUE BAIXO / ESTOQUE NORMAL)
fica centralizada em app/services/alerta_service.py. Esta rota apenas
exibe os resultados retornados pelo service.
"""

from flask import Blueprint, render_template

alertas_bp = Blueprint("alertas", __name__, url_prefix="/alertas")


# TODO: listar produtos com estoque baixo ou sem estoque (via alerta_service)
@alertas_bp.route("/")
def index():
    return render_template("alertas/index.html")
