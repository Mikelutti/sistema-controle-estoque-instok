"""Movimentações HTTP reais em SQLite temporário, sem tocar no banco local."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import sqlite3
import unittest
from unittest.mock import patch
import test_auth
import test_cadastros


class EstoqueFixture:
    @classmethod
    def setUpClass(cls):
        test_auth.AuthTests.setUpClass()
        cls.password = test_auth.AuthTests.password
        cls.password_hash = test_auth.AuthTests.password_hash

    sql = test_cadastros.CadastrosTests.sql
    token = test_auth.AuthTests.token
    login = test_auth.AuthTests.login
    post = test_cadastros.CadastrosTests.post

    def setUp(self):
        test_cadastros.CadastrosTests.setUp(self)
        self.sql("INSERT INTO setores(nome) VALUES ('Destino')")

    def dados(self, **changes):
        data = dict(produto_id='1', quantidade='5', setor_origem_id='1',
                    setor_destino_id='2', observacao=' Teste de movimentação ')
        data.update(changes)
        return data

    def saldo(self, setor_id=1):
        rows = self.sql('SELECT quantidade FROM estoques WHERE produto_id=1 AND setor_id=?', (setor_id,))
        return rows[0][0] if rows else 0

    def historico(self):
        return [dict(row) for row in self.sql('SELECT * FROM movimentacoes ORDER BY id')]


class EstoqueTests(EstoqueFixture, unittest.TestCase):
    def test_entrada_cria_saldo_e_historico_com_ator_da_sessao(self):
        self.login('operador')
        response = self.post('/estoque/entrada', self.dados(usuario_id='1', tipo='SAIDA'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.saldo(2), 5)
        row = self.historico()[0]
        self.assertEqual((row['usuario_id'], row['tipo'], row['setor_origem_id'], row['setor_destino_id']),
                         (2, 'ENTRADA', None, 2))
        self.assertEqual(row['observacao'], 'Teste de movimentação')
        self.assertTrue(row['data_hora'])
        self.assertEqual(self.post('/estoque/entrada', self.dados()).status_code, 302)
        self.assertEqual(self.saldo(2), 10)
        self.assertEqual(len(self.historico()), 2)
        self.client.get(response.location)
        self.assertEqual(len(self.historico()), 2)

    def test_saida_reduz_ate_zero_e_preserva_registro(self):
        self.login()
        self.post('/estoque/entrada', self.dados(setor_destino_id='1'))
        self.assertEqual(self.post('/estoque/saida', self.dados(quantidade='3')).status_code, 302)
        self.assertEqual(self.saldo(), 2)
        self.assertEqual(self.post('/estoque/saida', self.dados(quantidade='2')).status_code, 302)
        self.assertEqual(self.saldo(), 0)
        self.assertEqual(len(self.sql('SELECT * FROM estoques')), 1)
        self.assertEqual(self.historico()[-1]['tipo'], 'SAIDA')
        self.assertIsNone(self.historico()[-1]['setor_destino_id'])

    def test_saida_insuficiente_nao_altera_nem_registra(self):
        self.login()
        self.assertEqual(self.post('/estoque/saida', self.dados()).status_code, 400)
        self.assertEqual(self.sql('SELECT * FROM estoques'), [])
        self.post('/estoque/entrada', self.dados(setor_destino_id='1'))
        self.assertEqual(self.post('/estoque/saida', self.dados(quantidade='6')).status_code, 400)
        self.assertEqual(self.saldo(), 5)
        self.assertEqual(len(self.historico()), 1)

    def test_campos_invalidos_preservam_formulario_sem_gravar(self):
        self.login()
        for path in ['/estoque/entrada', '/estoque/saida', '/estoque/transferencia']:
            for value in ['', '0', '-1', '1.5', '1e3', 'abc', '9'*100, '١']:
                with self.subTest(path=path, quantidade=value):
                    response = self.post(path, self.dados(quantidade=value))
                    self.assertEqual(response.status_code, 400)
                    self.assertIn('Teste de movimentação', response.get_data(as_text=True))
                    self.assertEqual(self.historico(), [])
            self.assertEqual(self.post(path, self.dados(observacao='x'*2001)).status_code, 400)
        for field in ['produto_id', 'setor_destino_id']:
            for value in ['', '0', '999', '9'*100, 'abc']:
                self.assertEqual(self.post('/estoque/entrada', self.dados(**{field:value})).status_code, 400)
        self.assertEqual(self.sql('SELECT * FROM estoques'), [])

    def test_inativos_nao_movimentam_e_categoria_inativa_mantem_produto(self):
        self.login()
        for table, id in [('produtos',1), ('setores',1), ('setores',2)]:
            self.sql(f"UPDATE {table} SET status='INATIVO' WHERE id=?", (id,))
            for path in ['/estoque/entrada', '/estoque/saida', '/estoque/transferencia']:
                dados = self.dados(setor_destino_id=str(id)) if table == 'setores' and path.endswith('entrada') else self.dados(setor_origem_id=str(id)) if table == 'setores' and path.endswith('saida') else self.dados()
                self.assertEqual(self.post(path, dados).status_code, 400)
            self.sql(f"UPDATE {table} SET status='ATIVO' WHERE id=?", (id,))
        self.assertEqual(self.historico(), [])
        self.sql("UPDATE categorias SET status='INATIVO' WHERE id=1")
        self.assertEqual(self.post('/estoque/entrada', self.dados()).status_code, 302)

    def test_visitante_csrf_e_perda_de_sessao(self):
        for path in ['/estoque/entrada', '/estoque/saida', '/estoque/transferencia']:
            self.assertEqual(self.client.get(path).status_code, 302)
            self.assertEqual(self.client.post(path, data=self.dados()).status_code, 302)
        self.login('operador')
        for path in ['/estoque/entrada', '/estoque/saida', '/estoque/transferencia']:
            self.assertEqual(self.client.get(path).status_code, 200)
            self.assertEqual(self.client.post(path, data=self.dados()).status_code, 400)
        self.sql("UPDATE usuarios SET status='INATIVO' WHERE id=2")
        self.assertEqual(self.post('/estoque/entrada', self.dados()).status_code, 302)
        self.assertEqual(self.historico(), [])

    def test_erro_no_historico_reverte_saldo_e_linha_nova(self):
        self.login()
        with patch('app.repositories.movimentacao_repository.registrar_movimentacao',
                   side_effect=sqlite3.OperationalError('falha simulada')):
            with self.assertLogs(self.app.logger, level='ERROR'):
                response = self.post('/estoque/entrada', self.dados())
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('falha simulada', response.get_data(as_text=True))
        self.assertEqual(self.sql('SELECT * FROM estoques'), [])
        self.assertEqual(self.historico(), [])

    def test_entrada_nao_excede_limite_integer(self):
        self.login()
        limite = '9223372036854775807'
        self.assertEqual(self.post('/estoque/entrada', self.dados(quantidade=limite)).status_code, 302)
        self.assertEqual(self.post('/estoque/entrada', self.dados(quantidade='1')).status_code, 400)
        self.assertEqual(self.saldo(2), int(limite))
        self.assertEqual(self.sql('SELECT typeof(quantidade) FROM estoques')[0][0], 'integer')
        self.assertEqual(len(self.historico()), 1)

    def test_inventario_e_historico_incluem_sem_saldo_e_referencias(self):
        self.login()
        html = self.client.get('/estoque/inventario').get_data(as_text=True)
        self.assertIn('Produto inicial', html)
        self.assertIn('Sem movimentação', html)
        self.post('/estoque/entrada', self.dados(observacao='<script>alert(1)</script>'))
        self.sql("UPDATE produtos SET status='INATIVO' WHERE id=1")
        for path in ['/estoque/inventario', '/movimentacoes/']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('Produto inicial', html)
            self.assertNotIn('<script>alert(1)</script>', html)
            self.assertNotIn(self.password_hash, html)
        html = self.client.get('/movimentacoes/').get_data(as_text=True)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('admin', html)
        self.assertIn('UTC', html)
        self.assertEqual(self.client.post('/movimentacoes/').status_code, 405)

    def test_service_revalida_ator_e_aceita_somente_tipos_oficiais(self):
        from app.services import estoque_service as service
        from app.services.usuario_service import AcessoNegado
        with self.app.app_context():
            for actor in [3, 999]:
                with self.assertRaises(AcessoNegado):
                    service.movimentar('ENTRADA', **self.dados(), usuario_id=actor)
            for tipo in ['entrada', 'AJUSTE', '', 'DELETE']:
                with self.assertRaises(ValueError):
                    service.movimentar(tipo, **self.dados(), usuario_id=1)
            for quantidade in [True, 1.5, None]:
                with self.assertRaises(ValueError):
                    service.movimentar('ENTRADA', **self.dados(quantidade=quantidade), usuario_id=1)

    def test_duas_saidas_concorrentes_nao_tornam_saldo_negativo(self):
        from app.services import estoque_service as service
        self.sql('INSERT INTO estoques(produto_id,setor_id,quantidade) VALUES (1,1,5)')
        barreira = Barrier(2)
        def retirar(_):
            with self.app.app_context():
                barreira.wait(timeout=5)
                try:
                    service.movimentar('SAIDA', **self.dados(quantidade='4'), usuario_id=1)
                    return 'sucesso'
                except ValueError:
                    return 'insuficiente'
        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(executor.map(retirar, [1,2]))
        self.assertCountEqual(resultados, ['sucesso','insuficiente'])
        self.assertEqual(self.saldo(), 1)
        self.assertEqual(len(self.historico()), 1)

    def test_movimentacao_bloqueia_inativacao_e_saida_libera(self):
        self.login()
        self.post('/estoque/entrada', self.dados(setor_destino_id='1'))
        self.assertEqual(self.post('/produtos/1/inativar').status_code, 400)
        self.assertEqual(self.post('/setores/1/inativar').status_code, 400)
        self.post('/estoque/saida', self.dados())
        self.assertEqual(self.post('/produtos/1/inativar').status_code, 302)
        self.assertEqual(self.post('/setores/1/inativar').status_code, 302)
        self.assertEqual(len(self.historico()), 2)
        self.assertEqual(self.sql('PRAGMA foreign_key_check'), [])
