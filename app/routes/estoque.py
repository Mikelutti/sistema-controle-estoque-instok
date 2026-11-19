"""Formulários de movimentação e consulta de inventário."""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from app.routes.cadastros import registrar_erros
from app.services import estoque_service as service

estoque_bp = Blueprint("estoque", __name__, url_prefix="/estoque")
registrar_erros(estoque_bp)
TITULOS = {"ENTRADA": "Entrada de estoque", "SAIDA": "Saída de estoque",
           "TRANSFERENCIA": "Transferência entre setores"}


@estoque_bp.get("/inventario")
def inventario():
    return render_template("estoque/inventario.html", registros=service.listar_inventario())


def formulario(tipo):
    dados = {}
    status = 200
    if request.method == "POST":
        dados = {campo: request.form.get(campo, "") for campo in
                 ("produto_id", "quantidade", "setor_origem_id", "setor_destino_id", "observacao")}
        try:
            movimento_id = service.movimentar(tipo, **dados, usuario_id=g.usuario["id"])
        except ValueError as erro:
            flash(str(erro), "erro")
            status = 400
        else:
            flash(f"Movimentação #{movimento_id} registrada com sucesso. Saldo atualizado.", "sucesso")
            return redirect(url_for("estoque.inventario"))
    return render_template("estoque/" + tipo.lower() + ".html", tipo=tipo, titulo=TITULOS[tipo],
                           dados=dados, **service.opcoes_movimentacao()), status


@estoque_bp.route("/entrada", methods=["GET", "POST"])
def entrada():
    return formulario("ENTRADA")


@estoque_bp.route("/saida", methods=["GET", "POST"])
def saida():
    return formulario("SAIDA")


@estoque_bp.route("/transferencia", methods=["GET", "POST"])
def transferencia():
    return formulario("TRANSFERENCIA")
