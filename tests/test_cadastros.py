"""Contratos de categorias, setores e produtos com SQLite descartável."""
from contextlib import closing
import sqlite3
import unittest
from unittest.mock import patch
import test_auth
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Barrier


class CadastrosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_auth.AuthTests.setUpClass()
        cls.password = test_auth.AuthTests.password
        cls.password_hash = test_auth.AuthTests.password_hash

    token = test_auth.AuthTests.token
    login = test_auth.AuthTests.login

    def setUp(self):
        test_auth.AuthTests.setUp(self)
        self.sql("INSERT INTO categorias(nome) VALUES ('Categoria inicial')")
        self.sql("INSERT INTO setores(nome) VALUES ('Setor inicial')")
        self.sql("INSERT INTO produtos(codigo,nome,categoria_id) VALUES ('P1','Produto inicial',1)")

    def sql(self, sql, args=()):
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')
            return db.execute(sql, args).fetchall()

    def row(self, module, id=1):
        # Nomes de tabelas controlados pelo teste, nunca por entrada HTTP.
        return dict(self.sql(f'SELECT * FROM {module} WHERE id=?', (id,))[0])

    def data(self, module, **updates):
        data = dict(nome=' Novo nome ', descricao=' Descrição nova ')
        if module == 'produtos':
            data.update(codigo=' P2 ', categoria_id='1', estoque_minimo='3')
        data.update(updates)
        return data

    def post(self, path, data=None):
        with self.client.session_transaction() as session:
            token = session['csrf_token']
        return self.client.post(path, data={**(data or {}), 'csrf_token': token})

    def test_cadastro_persiste_dados_e_nao_cria_saldo(self):
        self.login()
        for module in ('categorias', 'setores', 'produtos'):
            with self.subTest(module=module):
                response = self.post(f'/{module}/formulario', self.data(module))
                self.assertEqual(response.status_code, 302)
                row = self.row(module, 2)
                self.assertEqual(row['nome'], 'Novo nome')
                self.assertEqual(row['descricao'], 'Descrição nova')
                self.assertEqual(row['status'], 'ATIVO')
                html = self.client.get(f'/{module}/').get_data(as_text=True)
                self.assertIn('Novo nome', html)
                self.assertIn('InStok', html)
        self.assertEqual(self.row('produtos', 2)['estoque_minimo'], 3)
        self.assertEqual(self.sql('SELECT * FROM estoques'), [])

    def test_campos_obrigatorios_limites_e_texto_preservado(self):
        self.login()
        for module in ('categorias', 'setores', 'produtos'):
            invalidos = [('nome', ''), ('nome', ' '), ('nome', 'a'*151),
                         ('descricao', 'a'*2001)]
            if module == 'produtos':
                invalidos += [('codigo', ''), ('codigo', 'a'*81)]
            for field, value in invalidos:
                with self.subTest(module=module, field=field, tamanho=len(value)):
                    data = self.data(module, **{field:value})
                    response = self.post(f'/{module}/formulario', data)
                    self.assertEqual(response.status_code, 400)
                    self.assertIn('role="alert"', response.get_data(as_text=True))
                    self.assertEqual(len(self.sql(f'SELECT * FROM {module}')), 1)
            response = self.post(f'/{module}/formulario', self.data(module, descricao=''))
            self.assertEqual(response.status_code, 302)

    def test_duplicidade_inclui_inativos_exclui_proprio_e_respeita_case(self):
        self.login()
        for module in ('categorias', 'setores', 'produtos'):
            with self.subTest(module=module):
                field = 'codigo' if module == 'produtos' else 'nome'
                original = self.row(module)[field]
                own = self.data(module, **{field:original})
                self.assertEqual(self.post(f'/{module}/1/editar', own).status_code, 302)
                self.assertEqual(self.post(f'/{module}/formulario', own).status_code, 400)
                self.assertEqual(self.post(f'/{module}/1/inativar').status_code, 302)
                self.assertEqual(self.post(f'/{module}/formulario', own).status_code, 400)
                other = self.data(module, **{field:original.lower()})
                self.assertEqual(self.post(f'/{module}/formulario', other).status_code, 302)
                before = self.row(module, 2)
                self.assertEqual(self.post(f'/{module}/2/editar', own).status_code, 400)
                self.assertEqual(self.row(module, 2), before)
                self.assertIn('Inativo', self.client.get(f'/{module}/').get_data(as_text=True))
                # Restaura somente a fixture para não interferir no próximo subteste.
                self.sql(f"UPDATE {module} SET status='ATIVO' WHERE id=1")

    def test_produto_categoria_invalida_e_estoque_minimo_invalido(self):
        self.login()
        for field, values in {
            'categoria_id': ['', '0', '-1', '999', '1.0', 'abc', '9'*100, '١'],
            'estoque_minimo': ['', '-1', '1.5', '1e2', 'abc', '9'*100, 'NaN', '١'],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    response = self.post('/produtos/formulario', self.data('produtos', **{field:value}))
                    self.assertEqual(response.status_code, 400)
                    self.assertIn('Novo nome', response.get_data(as_text=True))
                    self.assertEqual(len(self.sql('SELECT * FROM produtos')), 1)
        for value in ['0', '9223372036854775807']:
            self.assertEqual(self.post('/produtos/1/editar', self.data('produtos', estoque_minimo=value)).status_code, 302)
            self.assertEqual(self.row('produtos')['estoque_minimo'], int(value))

    def test_categoria_inativa_preserva_vinculo_mas_recusa_nova_associacao(self):
        self.login()
        self.assertEqual(self.post('/categorias/1/inativar').status_code, 302)
        self.assertEqual(self.row('produtos')['categoria_id'], 1)
        self.assertEqual(self.post('/produtos/formulario', self.data('produtos')).status_code, 400)
        self.assertEqual(self.post('/produtos/1/editar', self.data('produtos')).status_code, 302)
        self.sql("INSERT INTO categorias(nome) VALUES ('Outra')")
        self.assertEqual(self.post('/produtos/1/editar', self.data('produtos', categoria_id='2')).status_code, 302)
        self.assertEqual(self.post('/produtos/1/editar', self.data('produtos', categoria_id='1')).status_code, 400)
        self.assertEqual(self.row('produtos')['categoria_id'], 2)

    def test_inativacao_bloqueia_saldo_em_qualquer_setor(self):
        self.login()
        self.sql("INSERT INTO setores(nome) VALUES ('Outro setor')")
        self.sql('INSERT INTO estoques(produto_id,setor_id,quantidade) VALUES (1,1,0),(1,2,5)')
        self.assertEqual(self.post('/produtos/1/inativar').status_code, 400)
        self.assertEqual(self.post('/setores/2/inativar').status_code, 400)
        self.assertEqual(self.row('produtos')['status'], 'ATIVO')
        self.assertEqual(self.row('setores', 2)['status'], 'ATIVO')
        self.assertEqual(self.post('/setores/1/inativar').status_code, 302)

    def test_edicao_e_inativacao_preservam_saldos_historico_e_ids(self):
        self.login()
        self.sql('INSERT INTO estoques(produto_id,setor_id,quantidade) VALUES (1,1,0)')
        self.sql("INSERT INTO movimentacoes(produto_id,usuario_id,tipo,quantidade,setor_destino_id) VALUES (1,1,'ENTRADA',5,1)")
        before_stock = [dict(r) for r in self.sql('SELECT * FROM estoques')]
        before_history = [dict(r) for r in self.sql('SELECT * FROM movimentacoes')]
        for module in ('produtos', 'setores', 'categorias'):
            self.assertEqual(self.post(f'/{module}/1/editar', self.data(module, status='INATIVO', quantidade='999')).status_code, 302)
            self.assertEqual(self.row(module)['status'], 'ATIVO')
            self.assertEqual(self.post(f'/{module}/1/inativar').status_code, 302)
            self.assertEqual(self.row(module)['status'], 'INATIVO')
        self.assertEqual([dict(r) for r in self.sql('SELECT * FROM estoques')], before_stock)
        self.assertEqual([dict(r) for r in self.sql('SELECT * FROM movimentacoes')], before_history)
        self.assertEqual(self.sql('PRAGMA foreign_key_check'), [])

    def test_visitante_operador_e_csrf_em_todas_as_rotas(self):
        for module in ('categorias', 'setores', 'produtos'):
            for path in [f'/{module}/', f'/{module}/formulario', f'/{module}/1/editar']:
                self.assertEqual(self.client.get(path).status_code, 302)
            for path in [f'/{module}/formulario', f'/{module}/1/editar', f'/{module}/1/inativar']:
                self.assertEqual(self.client.post(path).status_code, 302)
        self.login('operador')
        for module in ('categorias', 'setores', 'produtos'):
            response = self.client.get(f'/{module}/')
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('Confirmar inativação', response.get_data(as_text=True))
            self.assertNotIn(f'/{module}/formulario', response.get_data(as_text=True))
            for path in [f'/{module}/formulario', f'/{module}/1/editar']:
                self.assertEqual(self.client.get(path).status_code, 403)
            for path in [f'/{module}/formulario', f'/{module}/1/editar', f'/{module}/1/inativar']:
                self.assertEqual(self.post(path, self.data(module, nivel_acesso='ADMINISTRADOR')).status_code, 403)
        self.client = self.app.test_client(); self.login()
        for module in ('categorias', 'setores', 'produtos'):
            for path in [f'/{module}/formulario', f'/{module}/1/editar', f'/{module}/1/inativar']:
                self.assertEqual(self.client.post(path, data=self.data(module)).status_code, 400)
            self.assertEqual(self.client.get(f'/{module}/1/inativar').status_code, 405)

    def test_registro_inexistente_retorna_404(self):
        self.login()
        for module in ('categorias', 'setores', 'produtos'):
            self.assertEqual(self.client.get(f'/{module}/999/editar').status_code, 404)
            self.assertEqual(self.post(f'/{module}/999/editar', self.data(module)).status_code, 404)
            self.assertEqual(self.post(f'/{module}/999/inativar').status_code, 404)

    def test_ids_de_url_fora_da_faixa_retornam_404(self):
        self.login()
        for module in ('categorias', 'setores', 'produtos'):
            for id in ['0', '9'*100]:
                with self.subTest(module=module, id=id):
                    self.assertEqual(self.client.get(f'/{module}/{id}/editar').status_code, 404)
                    self.assertEqual(self.post(f'/{module}/{id}/inativar').status_code, 404)

    def test_edicao_com_saldo_positivo_nao_altera_estoque(self):
        self.login()
        self.sql('INSERT INTO estoques(produto_id,setor_id,quantidade) VALUES (1,1,7)')
        for module in ('produtos', 'setores'):
            self.assertEqual(self.post(f'/{module}/1/editar', self.data(module, quantidade='999')).status_code, 302)
        self.assertEqual(self.sql('SELECT quantidade FROM estoques')[0][0], 7)

    def test_services_bloqueiam_ator_inativo_e_operador(self):
        from app.services import categoria_service, setor_service, produto_service
        from app.services.usuario_service import AcessoNegado
        for entity, module, service in [('categoria','categorias',categoria_service),
                                        ('setor','setores',setor_service),
                                        ('produto','produtos',produto_service)]:
            with self.app.app_context():
                for actor in [2, 3, 999]:
                    with self.assertRaises(AcessoNegado):
                        getattr(service, f'cadastrar_{entity}')(**self.data(module), administrador_id=actor)
                    with self.assertRaises(AcessoNegado):
                        getattr(service, f'atualizar_{entity}')(1, **self.data(module), administrador_id=actor)
                    with self.assertRaises(AcessoNegado):
                        getattr(service, f'inativar_{entity}')(1, administrador_id=actor)

    def test_perfil_rebaixado_perde_escrita_mas_mantem_consulta(self):
        self.login()
        self.sql("UPDATE usuarios SET nivel_acesso='OPERADOR' WHERE id=1")
        for module in ('categorias', 'setores', 'produtos'):
            self.assertEqual(self.client.get(f'/{module}/').status_code, 200)
            self.assertEqual(self.post(f'/{module}/formulario', self.data(module)).status_code, 403)

    def test_categoria_e_revalidada_apos_esperar_lock(self):
        from app.services.produto_service import cadastrar_produto
        from app.database import connection
        original = connection.obter_conexao
        iniciou = Event()
        def conectar():
            db = original()
            iniciou.set()
            return db
        def cadastrar():
            with self.app.app_context():
                return cadastrar_produto(**self.data('produtos'), administrador_id=1)
        with closing(sqlite3.connect(self.db_path)) as bloqueador:
            bloqueador.execute('BEGIN IMMEDIATE')
            bloqueador.execute("UPDATE categorias SET status='INATIVO' WHERE id=1")
            with patch('app.database.connection.obter_conexao', side_effect=conectar):
                with ThreadPoolExecutor(max_workers=1) as executor:
                    futuro = executor.submit(cadastrar)
                    try:
                        self.assertTrue(iniciou.wait(3))
                    finally:
                        bloqueador.commit()
                    with self.assertRaisesRegex(ValueError, 'categoria ativa'):
                        futuro.result(timeout=5)
        self.assertEqual(len(self.sql('SELECT * FROM produtos')), 1)

    def test_cadastros_simultaneos_nao_duplicam_categoria(self):
        from app.services.categoria_service import cadastrar_categoria
        barreira = Barrier(2)
        def cadastrar(_):
            with self.app.app_context():
                barreira.wait(timeout=5)
                try:
                    cadastrar_categoria('Concorrente', administrador_id=1)
                    return 'criado'
                except ValueError:
                    return 'duplicado'
        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(executor.map(cadastrar, [1,2]))
        self.assertCountEqual(resultados, ['criado','duplicado'])
        self.assertEqual(len(self.sql("SELECT * FROM categorias WHERE nome='Concorrente'")), 1)

    def test_formularios_e_listas_escapam_html(self):
        self.login()
        for module in ('categorias', 'setores', 'produtos'):
            self.assertEqual(self.post(f'/{module}/formulario', self.data(module, nome='<script>alert(1)</script>')).status_code, 302)
            for path in [f'/{module}/', f'/{module}/2/editar']:
                html = self.client.get(path).get_data(as_text=True)
                self.assertNotIn('<script>alert(1)</script>', html)
                self.assertIn('&lt;script&gt;', html)

    def test_conflito_unique_do_banco_retorna_validacao(self):
        self.login()
        for module, entity in [('categorias','categoria'),('setores','setor'),('produtos','produto')]:
            with patch(f'app.repositories.{entity}_repository.inserir_{entity}',
                       side_effect=sqlite3.IntegrityError('UNIQUE constraint failed: tabela.campo')):
                response = self.post(f'/{module}/formulario', self.data(module))
            self.assertEqual(response.status_code, 400)
            self.assertNotIn('UNIQUE constraint', response.get_data(as_text=True))
            self.assertEqual(len(self.sql(f'SELECT * FROM {module}')), 1)
