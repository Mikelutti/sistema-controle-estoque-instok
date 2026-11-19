"""Painel de indicadores do estoque real."""
from flask import Blueprint, render_template
from app.services.alerta_service import obter_resumo

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
def index():
    return render_template('dashboard/index.html', resumo=obter_resumo())
