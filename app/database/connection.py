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

import sqlite3
from pathlib import Path


# Diretorio raiz do projeto
BASE_DIR = Path(__file__).resolve().parents[2]

# Pasta onde o banco local sera armazenado
INSTANCE_DIR = BASE_DIR / "instance"

# Arquivo SQLite
DATABASE_PATH = INSTANCE_DIR / "controle_estoque.db"


def obter_conexao():
    """
    Abre e retorna uma conexao configurada com o SQLite.
    """

    # Garante que a pasta instance exista.
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(DATABASE_PATH)

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