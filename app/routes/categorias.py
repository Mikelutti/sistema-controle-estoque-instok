"""Rotas de categorias; permissões e CSRF são aplicados em security."""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from app.services import categoria_service as service
from app.services.cadastro_service import RegistroNaoEncontrado
from app.routes.cadastros import registrar_erros

categorias_bp = Blueprint("categorias", __name__, url_prefix="/categorias")
registrar_erros(categorias_bp)
CONTEXTO = dict(modulo="categorias", titulo="Categorias", entidade="categoria", produto=False)


def pagina(template, **contexto):
    return render_template("categorias/" + template + ".html", **CONTEXTO, **contexto)


@categorias_bp.get("/")
def index():
    return pagina("index", registros=service.listar_categorias())


def dados_formulario():
    return {campo: request.form.get(campo, "") for campo in ("nome", "descricao")}


@categorias_bp.route("/formulario", methods=["GET", "POST"])
def formulario():
    dados = {}
    if request.method == "POST":
        dados = dados_formulario()
        try:
            service.cadastrar_categoria(**dados, administrador_id=g.usuario["id"])
        except ValueError as erro:
            flash(str(erro), "erro")
            return pagina("formulario", dados=dados, editando=False), 400
        flash("Categoria cadastrada com sucesso.", "sucesso")
        return redirect(url_for("categorias.index"))
    return pagina("formulario", dados=dados, editando=False)


@categorias_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
def editar(registro_id):
    atual = service.obter_categoria(registro_id)
    dados = dict(atual)
    if request.method == "POST":
        dados = dados_formulario()
        try:
            service.atualizar_categoria(registro_id, **dados, administrador_id=g.usuario["id"])
        except RegistroNaoEncontrado:
            raise
        except ValueError as erro:
            flash(str(erro), "erro")
            return pagina("formulario", dados=dados, editando=True), 400
        flash("Categoria atualizada com sucesso.", "sucesso")
        return redirect(url_for("categorias.index"))
    return pagina("formulario", dados=dados, editando=True)


@categorias_bp.post("/<int:registro_id>/inativar")
def inativar(registro_id):
    try:
        service.inativar_categoria(registro_id, administrador_id=g.usuario["id"])
    except RegistroNaoEncontrado:
        raise
    except ValueError as erro:
        flash(str(erro), "erro")
        return pagina("index", registros=service.listar_categorias()), 400
    flash("Categoria inativada. Os vínculos e o histórico foram preservados.", "sucesso")
    return redirect(url_for("categorias.index"))
