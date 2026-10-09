"""
app/routes/produtos.py

Modulo responsavel por: gerenciamento de produtos (CRUD).

Cada produto possui, entre outros campos, um "estoque_minimo" utilizado
futuramente pelo alerta_service para classificar o status do estoque.

Funcionalidades previstas:
- Listar produtos
- Cadastrar novo produto
- Editar produto existente
- Remover/inativar produto
"""

from flask import Blueprint, render_template

produtos_bp = Blueprint("produtos", __name__, url_prefix="/produtos")


# TODO: listar produtos cadastrados
@produtos_bp.route("/")
def index():
    return render_template("produtos/index.html")


# TODO: exibir formulario de cadastro/edicao de produto
@produtos_bp.route("/formulario")
def formulario():
    return render_template("produtos/formulario.html")
