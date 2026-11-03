"""Constraints reais verificadas somente em banco descartável."""

from pathlib import Path
import sqlite3
import tempfile
import unittest

from werkzeug.security import generate_password_hash

from app import create_app
from app.database.connection import obter_conexao


class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = generate_password_hash("senha-exclusiva-de-fixture")

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        app = create_app({"TESTING": True, "SECRET_KEY": "chave-temporaria-de-teste",
                          "DATABASE_PATH": str(Path(directory.name) / "constraints.db")})
        context = app.app_context()
        context.push()
        self.addCleanup(context.pop)
        self.db = obter_conexao()
        self.addCleanup(self.db.close)
        self.db.executescript((Path(__file__).resolve().parents[1] / "database/schema.sql")
                              .read_text(encoding="utf-8"))
        self.db.execute("INSERT INTO categorias (nome) VALUES ('Categoria teste')")
        self.db.execute("INSERT INTO setores (nome) VALUES ('Setor teste')")
        self.db.execute("INSERT INTO produtos (codigo,nome,categoria_id) VALUES ('P1','Produto teste',1)")
        self.db.execute("INSERT INTO usuarios (nome,usuario,email,senha_hash,nivel_acesso) "
                        "VALUES ('Teste','teste','teste@example.test',?,'OPERADOR')", (self.password_hash,))
        self.db.commit()

    def test_estoque_negativo_e_bloqueado_por_check(self):
        with self.assertRaisesRegex(sqlite3.IntegrityError, "CHECK constraint failed"):
            self.db.execute("INSERT INTO estoques (produto_id,setor_id,quantidade) VALUES (1,1,-1)")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM estoques").fetchone()[0], 0)

    def test_categoria_inexistente_e_bloqueada_por_foreign_key(self):
        with self.assertRaisesRegex(sqlite3.IntegrityError, "FOREIGN KEY constraint failed"):
            self.db.execute("INSERT INTO produtos (codigo,nome,categoria_id) VALUES ('P2','Teste',999)")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0], 1)

    def test_login_duplicado_e_bloqueado_por_unique(self):
        with self.assertRaisesRegex(sqlite3.IntegrityError, "UNIQUE constraint failed: usuarios.usuario"):
            self.db.execute("INSERT INTO usuarios (nome,usuario,email,senha_hash,nivel_acesso) "
                            "VALUES ('Outro','teste','outro@example.test',?,'OPERADOR')", (self.password_hash,))
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
