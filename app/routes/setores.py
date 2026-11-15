"""Rotas de setores; permissões e CSRF são aplicados em security."""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from app.services import setor_service as service
from app.services.cadastro_service import RegistroNaoEncontrado
from app.routes.cadastros import registrar_erros

setores_bp = Blueprint("setores", __name__, url_prefix="/setores")
registrar_erros(setores_bp)
CONTEXTO = dict(modulo="setores", titulo="Setores", entidade="setor", produto=False)


def pagina(template, **contexto):
    return render_template("setores/" + template + ".html", **CONTEXTO, **contexto)


@setores_bp.get("/")
def index():
    return pagina("index", registros=service.listar_setores())


def dados_formulario():
    return {campo: request.form.get(campo, "") for campo in ("nome", "descricao")}


@setores_bp.route("/formulario", methods=["GET", "POST"])
def formulario():
    dados = {}
    if request.method == "POST":
        dados = dados_formulario()
        try:
            service.cadastrar_setor(**dados, administrador_id=g.usuario["id"])
        except ValueError as erro:
            flash(str(erro), "erro")
            return pagina("formulario", dados=dados, editando=False), 400
        flash("Setor cadastrado com sucesso.", "sucesso")
        return redirect(url_for("setores.index"))
    return pagina("formulario", dados=dados, editando=False)


@setores_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
def editar(registro_id):
    atual = service.obter_setor(registro_id)
    dados = dict(atual)
    if request.method == "POST":
        dados = dados_formulario()
        try:
            service.atualizar_setor(registro_id, **dados, administrador_id=g.usuario["id"])
        except RegistroNaoEncontrado:
            raise
        except ValueError as erro:
            flash(str(erro), "erro")
            return pagina("formulario", dados=dados, editando=True), 400
        flash("Setor atualizado com sucesso.", "sucesso")
        return redirect(url_for("setores.index"))
    return pagina("formulario", dados=dados, editando=True)


@setores_bp.post("/<int:registro_id>/inativar")
def inativar(registro_id):
    try:
        service.inativar_setor(registro_id, administrador_id=g.usuario["id"])
    except RegistroNaoEncontrado:
        raise
    except ValueError as erro:
        flash(str(erro), "erro")
        return pagina("index", registros=service.listar_setores()), 400
    flash("Setor inativado. Os vínculos e o histórico foram preservados.", "sucesso")
    return redirect(url_for("setores.index"))
