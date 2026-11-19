"""Consulta dos alertas; classificação centralizada no service."""
from flask import Blueprint, render_template
from app.services.alerta_service import obter_resumo

alertas_bp = Blueprint('alertas', __name__, url_prefix='/alertas')


@alertas_bp.route('/')
def index():
    return render_template('alertas/index.html', resumo=obter_resumo())
