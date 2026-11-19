"""Interface administrativa. Autorização e CSRF também são aplicados em security."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from app.services import usuario_service as service

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.errorhandler(service.AcessoNegado)
def acesso_negado(erro):
    abort(403)


@usuarios_bp.errorhandler(service.UsuarioNaoEncontrado)
def nao_encontrado(erro):
    return render_template("erro.html", titulo="Usuário não encontrado", mensagem=str(erro)), 404


@usuarios_bp.route("/")
def index():
    return render_template("usuarios/index.html", usuarios=service.listar_usuarios())


def dados_formulario():
    return {campo: request.form.get(campo, "") for campo in ("nome", "usuario", "email", "nivel_acesso")}


@usuarios_bp.route("/formulario", methods=["GET", "POST"])
def formulario():
    dados = {"nivel_acesso": "OPERADOR"}
    if request.method == "POST":
        dados = dados_formulario()
        try:
            service.cadastrar_usuario(**dados, senha=request.form.get("senha", ""),
                                      administrador_id=g.usuario["id"])
        except ValueError as erro:
            flash(str(erro), "erro")
            return render_template("usuarios/formulario.html", dados=dados, editando=False), 400
        flash("Usuário cadastrado com sucesso.", "sucesso")
        return redirect(url_for("usuarios.index"))
    return render_template("usuarios/formulario.html", dados=dados, editando=False)


@usuarios_bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
def editar(usuario_id):
    atual = service.obter_usuario(usuario_id)
    dados = dict(atual)
    if request.method == "POST":
        dados = dados_formulario()
        try:
            service.editar_usuario(usuario_id, **dados, administrador_id=g.usuario["id"])
        except service.UsuarioNaoEncontrado:
            raise
        except ValueError as erro:
            flash(str(erro), "erro")
            return render_template("usuarios/formulario.html", dados=dados, editando=True), 400
        flash("Usuário atualizado com sucesso.", "sucesso")
        destino = "dashboard.index" if usuario_id == g.usuario["id"] and dados["nivel_acesso"] != "ADMINISTRADOR" else "usuarios.index"
        return redirect(url_for(destino))
    return render_template("usuarios/formulario.html", dados=dados, editando=True)


@usuarios_bp.route("/<int:usuario_id>/inativar", methods=["POST"])
def inativar(usuario_id):
    try:
        service.inativar_usuario(usuario_id, administrador_id=g.usuario["id"])
    except service.UsuarioNaoEncontrado:
        raise
    except ValueError as erro:
        flash(str(erro), "erro")
        return render_template("usuarios/index.html", usuarios=service.listar_usuarios()), 400
    if usuario_id == g.usuario["id"]:
        session.clear()
        flash("Sua conta foi inativada e a sessão foi encerrada.", "sucesso")
        return redirect(url_for("auth.login"))
    flash("Usuário inativado. Seus registros e histórico foram preservados.", "sucesso")
    return redirect(url_for("usuarios.index"))
