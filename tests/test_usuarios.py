"""Gestão de usuários em banco descartável, incluindo autorização e histórico."""
from contextlib import closing
import sqlite3
import unittest
from unittest.mock import patch
from werkzeug.security import check_password_hash
import test_auth
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from app.services import usuario_service as service


class UsuariosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_auth.AuthTests.setUpClass()
        cls.password_hash = test_auth.AuthTests.password_hash
        cls.password = test_auth.AuthTests.password

    setUp = test_auth.AuthTests.setUp
    token = test_auth.AuthTests.token
    login = test_auth.AuthTests.login

    def post(self, path, **data):
        with self.client.session_transaction() as session:
            data.setdefault("csrf_token", session["csrf_token"])
        return self.client.post(path, data=data, follow_redirects=True)

    def dados(self, **changes):
        return dict(nome="Pessoa Teste", usuario="novo", email="Novo@Example.Test",
                    senha="senha-temporaria", nivel_acesso="OPERADOR", **changes)

    def row(self, id):
        with closing(sqlite3.connect(self.db_path)) as db:
            db.row_factory = sqlite3.Row
            return db.execute("SELECT * FROM usuarios WHERE id=?", (id,)).fetchone()

    def test_cadastro_persistencia_hash_e_listagem_sem_segredos(self):
        self.login()
        response = self.post('/usuarios/formulario', **self.dados())
        self.assertEqual(response.status_code, 200)
        row = self.row(5)
        self.assertIsNotNone(row)
        self.assertEqual(row['email'], 'novo@example.test')
        self.assertTrue(check_password_hash(row['senha_hash'], 'senha-temporaria'))
        html = response.get_data(as_text=True)
        self.assertIn('Pessoa Teste', html)
        self.assertIn('inativo@example.test', html)
        self.assertNotIn(row['senha_hash'], html)
        self.assertNotIn('senha-temporaria', html)

    def test_campos_invalidos_e_duplicados_nao_gravam(self):
        self.login()
        for field, value in [('nome', ''), ('usuario', ''), ('email', 'invalido'),
                             ('senha', ''), ('senha', 'curta'), ('nivel_acesso', 'ROOT'),
                             ('usuario', 'admin'), ('email', ' ADMIN@EXAMPLE.TEST '),
                             ('email', 'INATIVO@EXAMPLE.TEST')]:
            with self.subTest(field=field, value=value):
                data = self.dados(); data[field] = value
                response = self.post('/usuarios/formulario', **data)
                self.assertEqual(response.status_code, 400)
                self.assertIsNone(self.row(5))

    def test_edicao_proprios_dados_e_conflitos(self):
        self.login()
        data = dict(nome='Operador editado', usuario='operador',
                    email=' OPERADOR@EXAMPLE.TEST ', nivel_acesso='OPERADOR')
        self.assertEqual(self.post('/usuarios/2/editar', **data).status_code, 200)
        self.assertEqual(self.row(2)['nome'], 'Operador editado')
        self.assertEqual(self.row(2)['senha_hash'], self.password_hash)
        for field, value in [('usuario', 'admin'), ('email', 'ADMIN@EXAMPLE.TEST')]:
            other = dict(data); other[field] = value
            self.assertEqual(self.post('/usuarios/2/editar', **other).status_code, 400)
            self.assertEqual(self.row(2)['usuario'], 'operador')

    def test_ultimo_administrador_protegido(self):
        self.login()
        self.assertEqual(self.post('/usuarios/1/inativar').status_code, 400)
        self.assertEqual(self.post('/usuarios/1/editar', nome='admin', usuario='admin',
                         email='admin@example.test', nivel_acesso='OPERADOR').status_code, 400)
        self.assertEqual(self.row(1)['status'], 'ATIVO')
        self.assertEqual(self.row(1)['nivel_acesso'], 'ADMINISTRADOR')

    def test_inativacao_preserva_historico_e_revoga_sessao(self):
        other = self.app.test_client()
        other.post('/auth/login', data={'usuario':'operador','senha':self.password,
                                       'csrf_token':self.token(other)})
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("INSERT INTO categorias(nome) VALUES ('Categoria')")
            db.execute("INSERT INTO produtos(codigo,nome,categoria_id) VALUES ('P','Produto',1)")
            db.execute("INSERT INTO setores(nome) VALUES ('Setor')")
            db.execute("INSERT INTO movimentacoes(produto_id,usuario_id,tipo,quantidade,setor_destino_id) VALUES (1,2,'ENTRADA',1,1)")
        self.login()
        self.assertEqual(self.post('/usuarios/2/inativar').status_code, 200)
        self.assertEqual(self.row(2)['status'], 'INATIVO')
        self.assertEqual(other.get('/dashboard/').status_code, 302)
        other.post('/auth/login', data={'usuario':'operador','senha':self.password,
                                       'csrf_token':self.token(other)})
        with other.session_transaction() as session:
            self.assertNotIn('usuario_id', session)
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute('SELECT usuario_id FROM movimentacoes').fetchone()[0], 2)
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_visitante_operador_e_csrf(self):
        paths = ['/usuarios/', '/usuarios/formulario', '/usuarios/2/editar']
        mutations = ['/usuarios/formulario', '/usuarios/2/editar', '/usuarios/2/inativar']
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 302)
        for path in mutations:
            self.assertEqual(self.client.post(path, data=self.dados()).status_code, 302)
        self.login('operador')
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 403)
        for path in mutations:
            self.assertEqual(self.post(path, **self.dados()).status_code, 403)
        self.client = self.app.test_client(); self.login()
        for path in mutations:
            self.assertEqual(self.client.post(path, data=self.dados()).status_code, 400)
        self.assertEqual(self.client.get('/usuarios/2/inativar').status_code, 405)
        self.assertEqual(self.row(2)['status'], 'ATIVO')

    def test_demover_admin_revoga_permissao_da_sessao(self):
        self.login()
        data = self.dados(); data['nivel_acesso'] = 'ADMINISTRADOR'
        self.post('/usuarios/formulario', **data)
        other = self.app.test_client()
        other.post('/auth/login', data={'usuario':'novo','senha':data['senha'],
                                       'csrf_token':self.token(other)})
        data['nivel_acesso'] = 'OPERADOR'
        self.assertEqual(self.post('/usuarios/5/editar', **data).status_code, 200)
        self.assertEqual(other.get('/usuarios/').status_code, 403)
        self.assertEqual(other.post('/usuarios/2/inativar').status_code, 403)

    def test_inexistente_e_integridade_tratada(self):
        self.login()
        self.assertEqual(self.client.get('/usuarios/999/editar').status_code, 404)
        with patch('app.repositories.usuario_repository.inserir_usuario',
                   side_effect=sqlite3.IntegrityError('UNIQUE constraint failed: usuarios.email')):
            response = self.post('/usuarios/formulario', **self.dados())
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('UNIQUE constraint', response.get_data(as_text=True))

    def test_duas_inativacoes_simultaneas_preservam_um_admin(self):
        with self.app.app_context():
            segundo = service.cadastrar_usuario('Admin dois', 'admin2', 'admin2@example.test',
                                                self.password, 'ADMINISTRADOR', administrador_id=1)
        barreira = Barrier(2)
        def inativar_proprio(id):
            with self.app.app_context():
                barreira.wait(timeout=5)
                try:
                    service.inativar_usuario(id, administrador_id=id)
                    return 'sucesso'
                except ValueError:
                    return 'bloqueado'
        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(executor.map(inativar_proprio, [1, segundo]))
        self.assertCountEqual(resultados, ['sucesso', 'bloqueado'])
        self.assertEqual(sum(self.row(id)['status'] == 'ATIVO' for id in [1, segundo]), 1)

    def test_service_revalida_ator_e_edicao_nao_expoe_hash(self):
        with self.app.app_context():
            for id in [2, 3, 999]:
                with self.assertRaises(service.AcessoNegado):
                    service.cadastrar_usuario(**self.dados(), administrador_id=id)
                with self.assertRaises(service.AcessoNegado):
                    service.inativar_usuario(2, administrador_id=id)
                dados = self.dados(); dados.pop('senha')
                with self.assertRaises(service.AcessoNegado):
                    service.editar_usuario(2, **dados, administrador_id=id)
        self.login()
        html = self.client.get('/usuarios/2/editar').get_data(as_text=True)
        self.assertNotIn(self.password_hash, html)
        self.assertNotIn('name="senha"', html)

    def test_edicao_escapa_html_e_inativacao_propria_encerra_sessao(self):
        self.login()
        self.post('/usuarios/2/editar', nome='<script>alert(1)</script>', usuario='operador',
                  email='operador@example.test', nivel_acesso='ADMINISTRADOR')
        html = self.client.get('/usuarios/').get_data(as_text=True)
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;', html)
        response = self.post('/usuarios/1/inativar')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/auth/login', response.request.path)
        with self.client.session_transaction() as session:
            self.assertNotIn('usuario_id', session)
