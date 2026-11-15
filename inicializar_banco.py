"""Prepara tabelas e índices do banco configurado em uma única transação."""
import sqlite3
from contextlib import closing

from app.database.connection import BASE_DIR, obter_conexao


def inicializar_banco():
    schema = (BASE_DIR / "database/schema.sql").read_text(encoding="utf-8")
    with closing(obter_conexao()) as db:
        try:
            db.executescript("BEGIN IMMEDIATE;\n" + schema)
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("A verificação de integridade falhou.")
            if db.execute("PRAGMA foreign_key_check").fetchone():
                raise RuntimeError("Há referências inválidas no banco.")
            db.commit()
        except Exception:
            db.rollback()
            raise
    print("Banco inicializado e integridade verificada.")


if __name__ == "__main__":
    try:
        inicializar_banco()
    except (OSError, RuntimeError, sqlite3.Error) as erro:
        raise SystemExit(f"Falha na inicialização: {erro}")
