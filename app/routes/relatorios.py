"""
app/routes/relatorios.py

Modulo responsavel por: consultas e relatorios do sistema.

Funcionalidades previstas (futuras):
- Relatorio de movimentacoes por periodo
- Relatorio de estoque atual por setor/categoria
- Relatorio de produtos com estoque baixo/sem estoque
"""

from flask import Blueprint, render_template

relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


# TODO: exibir relatorios do sistema
@relatorios_bp.route("/")
def index():
    return render_template("relatorios/index.html")
