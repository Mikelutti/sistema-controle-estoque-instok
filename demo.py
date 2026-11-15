"""Inicia uma demonstração local descartável do InStok."""
from contextlib import contextmanager
from pathlib import Path
from secrets import token_hex
from tempfile import TemporaryDirectory

from werkzeug.serving import make_server

from app import create_app
from app.database.connection import BASE_DIR, transacao_escrita
from app.services.usuario_service import cadastrar_usuario


@contextmanager
def ambiente_demo():
    with TemporaryDirectory(prefix="instok-demo-") as pasta:
        app = create_app({
            "TESTING": True,
            "DATABASE_PATH": str(Path(pasta) / "demo.db"),
            "SECRET_KEY": token_hex(32),
            "SESSION_COOKIE_SECURE": False,
        })
        with app.app_context():
            with transacao_escrita() as db:
                db.executescript((BASE_DIR / "database/schema.sql").read_text(encoding="utf-8"))
                db.execute("INSERT INTO categorias(nome) VALUES ('Categoria inicial')")
                db.executemany("INSERT INTO setores(nome) VALUES (?)", [("Setor inicial",), ("Destino",)])
                db.execute("INSERT INTO produtos(codigo,nome,categoria_id,estoque_minimo) VALUES ('P1','Produto inicial',1,5)")
            for login, perfil in [("admin", "ADMINISTRADOR"), ("operador", "OPERADOR")]:
                cadastrar_usuario(login, login, login+"@example.test", "senha-somente-dos-testes", perfil)
        yield app


if __name__ == "__main__":
    with ambiente_demo() as app, make_server("127.0.0.1", 5058, app) as servidor:
        print("InStok em http://127.0.0.1:5058 — Ctrl+C para encerrar.", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
