"""Fluxos HTTP reais contra SQLite temporário, sem mocks de autenticação."""

from contextlib import closing
from html.parser import HTMLParser
from pathlib import Path
import re
import sqlite3
import tempfile
import unittest

from werkzeug.security import generate_password_hash

from app import create_app


class PageElements(HTMLParser):
    """Inspeciona os controles entregues pelo servidor, sem snapshots de HTML."""

    def __init__(self, html):
        super().__init__()
        self.links = []
        self.forms = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))
        elif tag == "form":
            self.forms.append(dict(attrs))


class AuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = "senha-somente-dos-testes"
        cls.password_hash = generate_password_hash(cls.password)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.db_path = Path(self.directory.name) / "test.db"
        self.app = create_app({"TESTING": True, "SECRET_KEY": "chave-temporaria-de-teste",
                               "DATABASE_PATH": str(self.db_path),
                               "SESSION_COOKIE_SECURE": False})
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.executescript((Path(__file__).resolve().parents[1] / "database/schema.sql")
                             .read_text(encoding="utf-8"))
            for login, role, status, hashed in [
                ("admin", "ADMINISTRADOR", "ATIVO", self.password_hash),
                ("operador", "OPERADOR", "ATIVO", self.password_hash),
                ("inativo", "OPERADOR", "INATIVO", self.password_hash),
                ("hash_invalido", "OPERADOR", "ATIVO", "senha_teste"),
            ]:
                db.execute("INSERT INTO usuarios (nome, usuario, email, senha_hash, nivel_acesso, status) "
                           "VALUES (?, ?, ?, ?, ?, ?)",
                           (login, login, login + "@example.test", hashed, role, status))
        self.client = self.app.test_client()

    def token(self, client=None):
        client = client or self.client
        response = client.get("/auth/login")
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
        self.assertIsNotNone(match, "O formulario precisa incluir um token CSRF")
        return match.group(1)

    def login(self, usuario="admin", senha=None, **extra):
        return self.client.post("/auth/login", data={
            "usuario": usuario, "senha": self.password if senha is None else senha,
            "csrf_token": self.token(), **extra,
        })

    def test_login_exibe_formulario_real(self):
        html = self.client.get("/auth/login").get_data(as_text=True)
        self.assertIn('name="usuario"', html)
        self.assertIn('name="senha"', html)
        self.assertNotIn('name="nivel_acesso"', html)
        self.assertIn('method="post"', html)

    def test_raiz_redireciona_para_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/auth/login"))

    def test_todas_as_paginas_internas_exigem_login(self):
        for rule in self.app.url_map.iter_rules():
            if rule.endpoint.startswith("auth.") or rule.endpoint == "static" or rule.rule == "/":
                continue
            with self.subTest(path=rule.rule):
                response = self.client.get(rule.rule)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.location.endswith("/auth/login"))

    def test_login_valido_cria_sessao_sem_hash(self):
        response = self.login()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/dashboard/"))
        with self.client.session_transaction() as session:
            self.assertEqual(session["usuario_id"], 1)
            self.assertNotIn("senha_hash", session)
            self.assertNotIn("nivel_acesso", session)
        self.assertEqual(self.client.get("/dashboard/").status_code, 200)

    def test_credenciais_invalidas_nao_autenticam(self):
        for login, password in [("admin", "errada"), ("inexistente", self.password),
                                ("inativo", self.password), ("hash_invalido", "senha_teste"),
                                ("' OR 1=1 --", self.password)]:
            with self.subTest(usuario=login):
                response = self.login(login, password)
                self.assertEqual(response.status_code, 200)
                self.assertIn("Usuario ou senha invalidos.", response.get_data(as_text=True))
                with self.client.session_transaction() as session:
                    self.assertNotIn("usuario_id", session)

    def test_campos_vazios_exibem_mensagem(self):
        for login, password in [("", "senha"), ("   ", "senha"), ("admin", "")]:
            with self.subTest(usuario=login, campo_senha_vazio=not password):
                response = self.login(login, password)
                self.assertEqual(response.status_code, 200)
                self.assertIn('role="alert"', response.get_data(as_text=True))

    def test_login_sem_csrf_ou_com_token_incorreto_e_rejeitado(self):
        self.token()
        for token in [None, "incorreto", "á"]:
            with self.subTest(token=token):
                data = {"usuario": "admin", "senha": self.password}
                if token is not None:
                    data["csrf_token"] = token
                response = self.client.post("/auth/login", data=data)
                self.assertEqual(response.status_code, 400)
                with self.client.session_transaction() as session:
                    self.assertNotIn("usuario_id", session)

    def test_token_de_outro_cliente_e_rejeitado(self):
        token = self.token(self.app.test_client())
        self.token()
        response = self.client.post("/auth/login", data={"usuario": "admin", "senha": self.password,
                                                        "csrf_token": token})
        self.assertEqual(response.status_code, 400)

    def test_login_renova_token_e_remove_dados_da_sessao_antiga(self):
        old_token = self.token()
        with self.client.session_transaction() as session:
            session["dado_antigo"] = "remover"
        self.login()
        with self.client.session_transaction() as session:
            self.assertNotIn("dado_antigo", session)
            self.assertNotEqual(session.get("csrf_token"), old_token)

    def test_logout_so_aceita_post_e_exige_csrf(self):
        self.login()
        self.assertEqual(self.client.get("/auth/logout").status_code, 405)
        self.assertEqual(self.client.post("/auth/logout").status_code, 400)
        with self.client.session_transaction() as session:
            self.assertEqual(session["usuario_id"], 1)
            token = session["csrf_token"]
        response = self.client.post("/auth/logout", data={"csrf_token": token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get("/dashboard/").status_code, 302)
        with self.client.session_transaction() as session:
            self.assertNotIn("usuario_id", session)

    def test_operador_nao_pode_escolher_perfil_nem_acessar_usuarios(self):
        self.login("operador", nivel_acesso="ADMINISTRADOR")
        self.assertEqual(self.client.get("/dashboard/").status_code, 200)
        for path in ["/usuarios/", "/usuarios/formulario"]:
            self.assertEqual(self.client.get(path).status_code, 403)

    def test_administrador_pode_acessar_usuarios(self):
        self.login()
        self.assertEqual(self.client.get("/usuarios/").status_code, 200)

    def test_usuario_inativado_perde_sessao(self):
        self.login()
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("UPDATE usuarios SET status='INATIVO' WHERE id=1")
        self.assertEqual(self.client.get("/dashboard/").status_code, 302)
        with self.client.session_transaction() as session:
            self.assertNotIn("usuario_id", session)

    def test_alteracao_de_perfil_vale_na_proxima_requisicao(self):
        self.login()
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("UPDATE usuarios SET nivel_acesso='OPERADOR' WHERE id=1")
        self.assertEqual(self.client.get("/usuarios/").status_code, 403)

    def test_banco_sem_schema_exibe_erro_controlado(self):
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("DROP TABLE usuarios")
        with self.assertLogs(self.app.logger, level="ERROR"):
            response = self.login()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("no such table", response.get_data(as_text=True))

    def test_conteudo_autenticado_nao_e_armazenado_em_cache(self):
        self.login()
        response = self.client.get("/dashboard/")
        self.assertIn("no-store", response.headers.get("Cache-Control", ""))

    def test_navegacao_marca_pagina_atual_e_links_abrem(self):
        self.login()
        html = self.client.get("/estoque/inventario").get_data(as_text=True)
        page = PageElements(html)
        active = [link.get("href") for link in page.links if link.get("aria-current") == "page"]
        self.assertEqual(active, ["/estoque/inventario"])
        for link in page.links:
            href = link.get("href", "")
            if href.startswith("/"):
                with self.subTest(href=href):
                    self.assertEqual(self.client.get(href, follow_redirects=True).status_code, 200)

    def test_menu_operador_nao_exibe_link_administrativo(self):
        self.login("operador")
        page = PageElements(self.client.get("/dashboard/").get_data(as_text=True))
        self.assertFalse(any(link.get("href", "").startswith("/usuarios") for link in page.links))
        self.assertEqual([f.get("method") for f in page.forms if f.get("action") == "/auth/logout"],
                         ["post"])

    def test_nome_do_usuario_e_escapado_na_navegacao(self):
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("UPDATE usuarios SET nome=? WHERE id=1", ('<script>alert(1)</script>',))
        self.login()
        html = self.client.get("/dashboard/").get_data(as_text=True)
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)


if __name__ == "__main__":
    unittest.main()
