"""
app/routes/setores.py

Modulo responsavel por: setores/localizacoes de estoque.

Relacionamento planejado: setores 1:N estoques
Setores tambem podem atuar como origem e destino em movimentacoes
de transferencia entre estoques.

Funcionalidades previstas:
- Listar setores
- Cadastrar/editar/remover setor
"""

from flask import Blueprint, render_template

setores_bp = Blueprint("setores", __name__, url_prefix="/setores")


# TODO: listar setores cadastrados
@setores_bp.route("/")
def index():
    return render_template("setores/index.html")
