"""
app/routes/estoque.py

Modulo responsavel por: entrada, saida, inventario e transferencia de estoque.

Regras de negocio (validar entrada/saida, impedir estoque negativo,
processar transferencia) ficam em app/services/estoque_service.py.
Esta camada apenas recebe a requisicao e delega para o service.

Funcionalidades previstas:
- Visualizar inventario atual
- Registrar entrada de produtos
- Registrar saida de produtos
- Registrar transferencia entre setores
"""

from flask import Blueprint, render_template

estoque_bp = Blueprint("estoque", __name__, url_prefix="/estoque")


# TODO: exibir inventario atual (quantidades por produto/setor)
@estoque_bp.route("/inventario")
def inventario():
    return render_template("estoque/inventario.html")


# TODO: registrar entrada de produtos no estoque
@estoque_bp.route("/entrada")
def entrada():
    return render_template("estoque/entrada.html")


# TODO: registrar saida de produtos do estoque
@estoque_bp.route("/saida")
def saida():
    return render_template("estoque/saida.html")


# TODO: registrar transferencia de produtos entre setores
@estoque_bp.route("/transferencia")
def transferencia():
    return render_template("estoque/transferencia.html")
