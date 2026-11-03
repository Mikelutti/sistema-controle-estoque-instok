"""O comando de diagnóstico deve recusar qualquer conexão fora da pasta temporária."""

from contextlib import redirect_stderr
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import testar_banco


class ScriptTests(unittest.TestCase):
    def test_script_executa_somente_em_bancos_temporarios(self):
        connect = sqlite3.connect
        temp_root = Path(tempfile.gettempdir()).resolve()

        def conectar_apenas_temporario(path, *args, **kwargs):
            self.assertTrue(Path(path).resolve().is_relative_to(temp_root),
                            "O script tentou acessar um banco fora da pasta temporaria")
            return connect(path, *args, **kwargs)

        with patch.object(sqlite3, "connect", side_effect=conectar_apenas_temporario), redirect_stderr(io.StringIO()):
            self.assertTrue(testar_banco.testar_banco())


if __name__ == "__main__":
    unittest.main()
