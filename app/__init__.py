"""
app/__init__.py

Responsabilidade:
- Definir a fabrica de aplicacao (Application Factory) do sistema.
- Criar e configurar a instancia do Flask.
- Registrar os blueprints dos modulos.

Este arquivo NAO deve conter regras de negocio.
As regras de negocio ficam na camada app/services/.
"""

from flask import Flask


def create_app():
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

    # ---------------------------------------------------------
    # CONFIGURACOES
    # ---------------------------------------------------------
    # As configuracoes de seguranca, banco de dados e variaveis
    # de ambiente serao adicionadas nas proximas etapas.

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

    return app