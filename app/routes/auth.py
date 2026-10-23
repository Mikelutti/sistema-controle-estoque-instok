"""
app/routes/auth.py

Responsabilidade:
- Receber requisicoes relacionadas a autenticacao.
- Exibir a pagina de login.
- Processar as credenciais.
- Criar e encerrar a sessao do usuario.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.services.auth_service import validar_login


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_informado = request.form.get("usuario", "")
        senha = request.form.get("senha", "")

        try:
            usuario = validar_login(
                login_informado,
                senha,
            )

            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["nivel_acesso"] = usuario["nivel_acesso"]

            return redirect(
                url_for("dashboard.index")
            )

        except ValueError as erro:
            flash(str(erro), "erro")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()

    return redirect(
        url_for("auth.login")
    )