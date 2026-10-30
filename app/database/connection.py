"""
app/database/connection.py

Responsabilidade:
- Localizar o arquivo SQLite dentro de instance/.
- Abrir conexoes com o banco.
- Configurar sqlite3.Row.
- Habilitar chaves estrangeiras.
- Entregar conexoes prontas para os repositories.

Este arquivo NAO contem queries especificas de entidades.
"""

import os
import sqlite3
from pathlib import Path

from flask import current_app, has_app_context


# Diretorio raiz do projeto
BASE_DIR = Path(__file__).resolve().parents[2]

# Pasta onde o banco local sera armazenado
INSTANCE_DIR = BASE_DIR / "instance"

# Arquivo SQLite
DATABASE_PATH = INSTANCE_DIR / "controle_estoque.db"


def resolver_caminho(caminho):
    caminho = Path(caminho).expanduser()
    if not caminho.is_absolute():
        caminho = BASE_DIR / caminho
    return caminho.resolve()


def validar_banco_de_testes(caminho):
    """Impede que a configuração de testes reutilize o banco local."""
    caminho = resolver_caminho(caminho)
    banco_local = resolver_caminho(os.environ.get("DATABASE_PATH", str(DATABASE_PATH)))
    if (caminho.is_relative_to(INSTANCE_DIR.resolve()) or caminho == banco_local
            or (caminho.exists() and banco_local.exists() and caminho.samefile(banco_local))):
        raise ValueError("Testes nao podem utilizar o banco local do projeto.")
    return caminho


def obter_conexao():
    """
    Abre e retorna uma conexao configurada com o SQLite.
    """

    if has_app_context():
        caminho = resolver_caminho(current_app.config["DATABASE_PATH"])
        if current_app.testing:
            validar_banco_de_testes(caminho)
    else:
        caminho = resolver_caminho(os.environ.get("DATABASE_PATH", str(DATABASE_PATH)))

    caminho.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho)

    # Permite acessar colunas pelo nome.
    conexao.row_factory = sqlite3.Row

    # Habilita as FOREIGN KEYS no SQLite.
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def fechar_conexao(conexao=None):
    """
    Fecha uma conexao SQLite, caso exista.
    """

    if conexao is not None:
        conexao.close()
