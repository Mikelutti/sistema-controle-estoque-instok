"""Formulários e consultas de produtos; regras ficam no service."""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from app.services import produto_service as service
from app.services.cadastro_service import RegistroNaoEncontrado
from app.routes.cadastros import registrar_erros

produtos_bp = Blueprint("produtos", __name__, url_prefix="/produtos")
registrar_erros(produtos_bp)
CONTEXTO = dict(modulo="produtos", titulo="Produtos", entidade="produto", produto=True)


def pagina(template, **contexto):
    return render_template("produtos/" + template + ".html", **CONTEXTO, **contexto)


@produtos_bp.get("/")
def index():
    return pagina("index", registros=service.listar_produtos())


def dados_formulario():
    return {campo: request.form.get(campo, "") for campo in
            ("codigo", "nome", "descricao", "categoria_id", "estoque_minimo")}


@produtos_bp.route("/formulario", methods=["GET", "POST"])
def formulario():
    dados = {"estoque_minimo": "0"}
    if request.method == "POST":
        dados = dados_formulario()
        try:
            service.cadastrar_produto(**dados, administrador_id=g.usuario["id"])
        except ValueError as erro:
            flash(str(erro), "erro")
            return pagina("formulario", dados=dados, editando=False,
                          categorias=service.categorias_para_formulario()), 400
        flash("Produto cadastrado com sucesso.", "sucesso")
        return redirect(url_for("produtos.index"))
    return pagina("formulario", dados=dados, editando=False,
                  categorias=service.categorias_para_formulario())


@produtos_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
def editar(registro_id):
    atual = service.obter_produto(registro_id)
    dados = dict(atual)
    if request.method == "POST":
        dados = dados_formulario()
        try:
            service.atualizar_produto(registro_id, **dados, administrador_id=g.usuario["id"])
        except RegistroNaoEncontrado:
            raise
        except ValueError as erro:
            flash(str(erro), "erro")
            # Reconsulta para refletir mudanças de categoria ocorridas durante o envio.
            atual = service.obter_produto(registro_id)
            return pagina("formulario", dados=dados, editando=True,
                          categorias=service.categorias_para_formulario(atual)), 400
        flash("Produto atualizado com sucesso.", "sucesso")
        return redirect(url_for("produtos.index"))
    return pagina("formulario", dados=dados, editando=True,
                  categorias=service.categorias_para_formulario(atual))


@produtos_bp.post("/<int:registro_id>/inativar")
def inativar(registro_id):
    try:
        service.inativar_produto(registro_id, administrador_id=g.usuario["id"])
    except RegistroNaoEncontrado:
        raise
    except ValueError as erro:
        flash(str(erro), "erro")
        return pagina("index", registros=service.listar_produtos()), 400
    flash("Produto inativado. Os vínculos e o histórico foram preservados.", "sucesso")
    return redirect(url_for("produtos.index"))
