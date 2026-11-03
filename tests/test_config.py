"""Configuração e isolamento: nenhuma conexão ao banco local é permitida."""

import inspect
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from app.database.connection import DATABASE_PATH, obter_conexao


class ConfigTests(unittest.TestCase):
    def make_app(self, **config):
        self.assertIn("test_config", inspect.signature(create_app).parameters,
                      "A factory precisa aceitar configuração isolada de testes")
        return create_app(config)

    def test_chave_ausente_impede_inicializacao(self):
        with patch.dict(os.environ, {"SECRET_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "SECRET_KEY"):
                create_app()

    def test_chave_do_exemplo_nao_e_aceita(self):
        with patch.dict(os.environ, {"SECRET_KEY": "troque-por-uma-chave-secreta-aleatoria"}):
            with self.assertRaisesRegex(ValueError, "SECRET_KEY"):
                create_app()

    def test_configuracao_do_ambiente(self):
        with patch.dict(os.environ, {"SECRET_KEY": "chave-apenas-de-teste-32-caracteres",
                                    "FLASK_DEBUG": "false", "SESSION_COOKIE_SECURE": "true"}):
            app = create_app()
        self.assertEqual(app.secret_key, "chave-apenas-de-teste-32-caracteres")
        self.assertFalse(app.debug)
        self.assertTrue(app.config["SESSION_COOKIE_HTTPONLY"])
        self.assertEqual(app.config["SESSION_COOKIE_SAMESITE"], "Lax")
        self.assertTrue(app.config["SESSION_COOKIE_SECURE"])

    def test_testing_exige_banco_explicito(self):
        with self.assertRaisesRegex(ValueError, "DATABASE_PATH"):
            self.make_app(TESTING=True, SECRET_KEY="chave-temporaria-de-teste")

    def test_testing_recusa_banco_real(self):
        with self.assertRaisesRegex(ValueError, "banco local"):
            self.make_app(TESTING=True, SECRET_KEY="chave-temporaria-de-teste",
                          DATABASE_PATH=str(DATABASE_PATH))

    def test_conexao_usa_banco_temporario_com_foreign_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "isolado.db"
            app = self.make_app(TESTING=True, SECRET_KEY="chave-temporaria-de-teste",
                                DATABASE_PATH=str(path))
            with app.app_context():
                db = obter_conexao()
                try:
                    self.assertEqual(Path(db.execute("PRAGMA database_list").fetchone()[2]).resolve(),
                                     path.resolve())
                    self.assertEqual(db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
                    self.assertEqual(db.execute("SELECT 1 AS valor").fetchone()["valor"], 1)
                finally:
                    db.close()

    def test_troca_de_config_para_banco_real_e_bloqueada_na_conexao(self):
        with tempfile.TemporaryDirectory() as directory:
            app = self.make_app(TESTING=True, SECRET_KEY="chave-temporaria-de-teste",
                                DATABASE_PATH=str(Path(directory) / "isolado.db"))
            app.config["DATABASE_PATH"] = str(DATABASE_PATH)
            with app.app_context(), self.assertRaisesRegex(ValueError, "banco local"):
                obter_conexao()


if __name__ == "__main__":
    unittest.main()
