"""
app/__init__.py

Responsabilidade:
- Definir a fabrica de aplicacao (Application Factory) do sistema.
- Criar e configurar a instancia do Flask.
- Registrar os blueprints dos modulos.

Este arquivo NAO deve conter regras de negocio.
As regras de negocio ficam na camada app/services/.
"""

import os
import sqlite3
from datetime import timedelta

from flask import Flask, g, redirect, render_template, url_for

from app.database.connection import DATABASE_PATH, validar_banco_de_testes


def create_app(test_config=None):
    """
    Cria e configura a instancia principal da aplicacao Flask.

    Retorna:
        app (Flask): instancia configurada da aplicacao.
    """

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        DATABASE_PATH=os.environ.get("DATABASE_PATH", str(DATABASE_PATH)),
        DEBUG=os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "false").lower()
        in ("1", "true"),
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if test_config is not None:
        app.config.update(test_config)

    secret = app.config["SECRET_KEY"]
    if (not secret or secret == "troque-por-uma-chave-secreta-aleatoria"
            or (not app.testing and len(secret) < 32)):
        raise ValueError("Configure SECRET_KEY com uma chave aleatoria de pelo menos 32 caracteres.")

    if app.testing:
        if not test_config or not test_config.get("DATABASE_PATH"):
            raise ValueError("TESTING exige DATABASE_PATH explicito para um banco isolado.")
        validar_banco_de_testes(app.config["DATABASE_PATH"])

    # ---------------------------------------------------------
    # IMPORTACAO DOS BLUEPRINTS
    # ---------------------------------------------------------

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.produtos import produtos_bp
    from app.routes.categorias import categorias_bp
    from app.routes.setores import setores_bp
    from app.routes.estoque import estoque_bp
    from app.routes.movimentacoes import movimentacoes_bp
    from app.routes.alertas import alertas_bp
    from app.routes.relatorios import relatorios_bp

    # ---------------------------------------------------------
    # REGISTRO DOS BLUEPRINTS
    # ---------------------------------------------------------

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(setores_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(movimentacoes_bp)
    app.register_blueprint(alertas_bp)
    app.register_blueprint(relatorios_bp)

    from app.security import init_app as init_security
    init_security(app)

    @app.get("/")
    def index():
        return redirect(url_for("dashboard.index" if g.usuario else "auth.login"))

    @app.errorhandler(400)
    def requisicao_invalida(erro):
        return render_template("erro.html", titulo="Não foi possível enviar o formulário",
                               mensagem=erro.description), 400

    @app.errorhandler(403)
    def acesso_negado(erro):
        return render_template("erro.html", titulo="Acesso restrito",
                               mensagem="Esta função está disponível apenas para administradores."), 403

    @app.errorhandler(sqlite3.Error)
    def banco_indisponivel(erro):
        app.logger.error("Banco de dados indisponivel (%s).", type(erro).__name__)
        return render_template("erro.html", titulo="Serviço temporariamente indisponível",
                               mensagem="Não foi possível acessar os dados. Tente novamente mais tarde "
                               "ou entre em contato com o administrador."), 503

    return app
