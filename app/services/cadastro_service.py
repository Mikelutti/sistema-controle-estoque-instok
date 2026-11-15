"""Validações e transação comuns aos cadastros de estoque."""
from contextlib import contextmanager
import re
import sqlite3

from app.database.connection import transacao_escrita
from app.services.usuario_service import validar_administrador

MAX_INTEIRO = 9223372036854775807


class RegistroNaoEncontrado(ValueError):
    pass


def texto(valor, rotulo, limite, obrigatorio=True):
    if not isinstance(valor, str):
        raise ValueError(f"Informe {rotulo} válido.")
    valor = valor.strip()
    if obrigatorio and not valor:
        raise ValueError(f"O campo {rotulo} é obrigatório.")
    if len(valor) > limite:
        raise ValueError(f"O campo {rotulo} deve ter até {limite} caracteres.")
    return valor


def inteiro(valor, rotulo, minimo=0):
    # Evita truncamento de floats, booleanos e overflow no binding do SQLite.
    if type(valor) is int:
        numero = valor
    elif isinstance(valor, str) and re.fullmatch(r"[0-9]{1,19}", valor.strip()):
        numero = int(valor.strip())
    else:
        raise ValueError(f"O campo {rotulo} deve ser um número inteiro de {minimo} até {MAX_INTEIRO}.")
    if not minimo <= numero <= MAX_INTEIRO:
        raise ValueError(f"O campo {rotulo} deve estar entre {minimo} e {MAX_INTEIRO}.")
    return numero


def identificador(valor):
    try:
        return inteiro(valor, 'identificador', 1)
    except ValueError:
        raise RegistroNaoEncontrado('Registro não encontrado.') from None


@contextmanager
def alteracao_administrativa(administrador_id):
    try:
        with transacao_escrita() as db:
            validar_administrador(administrador_id, db)
            yield db
    except sqlite3.IntegrityError as erro:
        codigo = getattr(erro, 'sqlite_errorcode', None)
        if codigo == sqlite3.SQLITE_CONSTRAINT_UNIQUE or (
                codigo is None and 'UNIQUE constraint failed' in str(erro)):
            raise ValueError("Já existe um registro com esse nome ou código, inclusive entre os inativos.") from None
        raise
