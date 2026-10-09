"""
app/routes/auth.py

Modulo responsavel por: login e logout de usuarios.

Responsabilidade desta camada (routes):
- Receber requisicoes HTTP relacionadas a autenticacao.
- Validar dados basicos de entrada (formato).
- Chamar a camada de services para regras de negocio (quando existir).
- Renderizar os templates correspondentes.

Nao implementar aqui: regras de negocio complexas (ex: validacao de senha,
geracao de sessao/token) — isso ficara em app/services futuramente.
"""

from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# TODO: implementar rota de login (GET para exibir formulario, POST para autenticar)
@auth_bp.route("/login")
def login():
    return render_template("auth/login.html")


# TODO: implementar rota de logout (encerrar sessao do usuario)
# @auth_bp.route("/logout")
# def logout():
#     pass
