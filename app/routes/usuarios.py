"""
app/routes/usuarios.py

Modulo responsavel por: gerenciamento de usuarios (CRUD).

Funcionalidades previstas:
- Listar usuarios
- Cadastrar novo usuario
- Editar usuario existente
- Remover/inativar usuario
"""

from flask import Blueprint, render_template

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


# TODO: listar usuarios cadastrados
@usuarios_bp.route("/")
def index():
    return render_template("usuarios/index.html")


# TODO: exibir formulario de cadastro/edicao de usuario
@usuarios_bp.route("/formulario")
def formulario():
    return render_template("usuarios/formulario.html")
