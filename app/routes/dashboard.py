"""
app/routes/dashboard.py

Modulo responsavel por: pagina inicial do sistema (Dashboard).

Aqui futuramente serao exibidos:
- Resumo geral do estoque
- Alertas de estoque baixo / sem estoque (via alerta_service)
- Indicadores gerais do sistema
"""

from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


# TODO: buscar dados reais de estoque e alertas via services
@dashboard_bp.route("/")
def index():
    return render_template("dashboard/index.html")
