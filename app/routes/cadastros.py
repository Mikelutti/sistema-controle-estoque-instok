"""Tratamento HTTP comum, sem regras de negócio ou acesso ao banco."""
from flask import render_template
from app.services.cadastro_service import RegistroNaoEncontrado
from app.services.usuario_service import AcessoNegado


def registrar_erros(blueprint):
    @blueprint.errorhandler(RegistroNaoEncontrado)
    def nao_encontrado(erro):
        return render_template('erro.html', titulo='Registro não encontrado', mensagem=str(erro)), 404

    @blueprint.errorhandler(AcessoNegado)
    def acesso_negado(erro):
        return render_template('erro.html', titulo='Acesso restrito', mensagem=str(erro)), 403
