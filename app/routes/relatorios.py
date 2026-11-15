"""Relatórios de consulta e exportação para usuários autenticados."""
from flask import Blueprint, Response, render_template, request, url_for
from app.services.relatorio_service import gerar_relatorio, gerar_csv
from app.repositories.produto_repository import listar_produtos
from app.repositories.categoria_repository import listar_categorias
from app.repositories.setor_repository import listar_setores

relatorios_bp=Blueprint('relatorios',__name__,url_prefix='/relatorios')


def pagina(erro=None, relatorio=None):
    return render_template('relatorios/index.html', erro=erro, resultado=relatorio,
        valores=request.args, produtos=listar_produtos(), categorias=listar_categorias(),
        setores=listar_setores(), export_url=url_for('relatorios.exportar',**{k: request.args[k] for k in ('relatorio', 'produto_id', 'categoria_id', 'setor_id', 'inicio', 'fim', 'tipo') if k in request.args}))


@relatorios_bp.route('/')
def index():
    try:
        return pagina(relatorio=gerar_relatorio(request.args))
    except ValueError as erro:
        return pagina(erro=str(erro)),400


@relatorios_bp.route('/exportar')
def exportar():
    try:
        resultado=gerar_relatorio(request.args)
    except ValueError as erro:
        return pagina(erro=str(erro)),400
    return Response(gerar_csv(resultado),content_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename="instok-'+resultado['filtros']['relatorio']+'.csv"'})
