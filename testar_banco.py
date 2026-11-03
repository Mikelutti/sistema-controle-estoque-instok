"""Executa os testes de constraints em SQLite temporário, nunca no banco local."""

from pathlib import Path
import unittest


def testar_banco():
    pasta_testes = Path(__file__).resolve().parent / "tests"
    suite = unittest.defaultTestLoader.discover(str(pasta_testes), pattern="test_database.py")
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


if __name__ == "__main__":
    raise SystemExit(0 if testar_banco() else 1)
