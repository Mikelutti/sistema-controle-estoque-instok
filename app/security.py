"""Proteção HTTP central: sessão, autorização e CSRF."""

import secrets

from flask import abort, g, redirect, request, session, url_for

from app.services.auth_service import obter_usuario_autenticado


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def proteger_requisicao():
    g.usuario = None
    # Deixa o Flask produzir 404/405 e servir os assets sem consultar o banco.
    if request.endpoint is None or request.endpoint == "static":
        return None

    if "usuario_id" in session:
        g.usuario = obter_usuario_autenticado(session["usuario_id"])
        if g.usuario is None:
            session.clear()

    if request.endpoint not in {"auth.login", "index"}:
        if g.usuario is None:
            return redirect(url_for("auth.login"))
        if request.blueprint == "usuarios" and g.usuario["nivel_acesso"] != "ADMINISTRADOR":
            abort(403)

    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        esperado = session.get("csrf_token", "")
        recebido = request.form.get("csrf_token", "") or request.headers.get("X-CSRF-Token", "")
        if not esperado or not recebido or not secrets.compare_digest(
            esperado.encode("utf-8"), recebido.encode("utf-8")
        ):
            abort(400, description="O formulario expirou ou e invalido. Recarregue a pagina e tente novamente.")
    return None


def proteger_resposta(response):
    if request.endpoint != "static":
        response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    return response


def init_app(app):
    app.before_request(proteger_requisicao)
    app.after_request(proteger_resposta)
    app.jinja_env.globals["csrf_token"] = csrf_token
