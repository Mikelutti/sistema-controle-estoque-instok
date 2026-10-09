"""
app/routes/categorias.py

Modulo responsavel por: categorias de produtos.

Relacionamento planejado: categorias 1:N produtos
(cada categoria pode ter varios produtos associados).

Funcionalidades previstas:
- Listar categorias
- Cadastrar/editar/remover categoria
"""

from flask import Blueprint, render_template

categorias_bp = Blueprint("categorias", __name__, url_prefix="/categorias")


# TODO: listar categorias cadastradas
@categorias_bp.route("/")
def index():
    return render_template("categorias/index.html")
