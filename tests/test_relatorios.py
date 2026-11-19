"""Relatórios usam apenas o SQLite temporário da fixture."""
import csv
import io
import unittest
from test_estoque import EstoqueFixture


class RelatoriosTests(EstoqueFixture, unittest.TestCase):
    def preparar(self):
        self.login()
        self.post('/estoque/entrada', self.dados(quantidade='10', setor_destino_id='1'))
        self.post('/estoque/saida', self.dados(quantidade='2'))
        self.post('/estoque/transferencia', self.dados(quantidade='3'))
        self.sql("UPDATE movimentacoes SET data_hora='2026-11-01 23:59:59' WHERE id=1")
        self.sql("UPDATE movimentacoes SET data_hora='2026-11-02 00:00:00' WHERE id>1")

    def csv(self, query):
        response = self.client.get('/relatorios/exportar?' + query)
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response.headers['Content-Disposition'])
        return list(csv.reader(io.StringIO(response.data.decode('utf-8-sig')), delimiter=';'))

    def test_periodo_inclusivo_tipo_e_csv(self):
        self.preparar()
        rows = self.csv('inicio=2026-11-01&fim=2026-11-01')
        self.assertEqual(len(rows), 2)
        self.assertIn('ENTRADA', rows[1])
        rows = self.csv('inicio=2026-11-02&fim=2026-11-02&tipo=SAIDA')
        self.assertEqual(len(rows), 2)
        self.assertIn('SAIDA', rows[1])

    def test_filtros_produto_setor_categoria(self):
        self.preparar()
        self.assertEqual(len(self.csv('setor_id=2')), 2)
        self.assertEqual(len(self.csv('produto_id=999')), 1)
        self.assertEqual(len(self.csv('categoria_id=999')), 1)
        self.assertEqual(len(self.csv('produto_id=1&categoria_id=1')), 4)

    def test_inventario_e_alertas(self):
        self.preparar()
        self.sql('UPDATE produtos SET estoque_minimo=8')
        rows = self.csv('relatorio=estoque&setor_id=2')
        self.assertEqual(len(rows), 2)
        self.assertIn('3', rows[1])
        rows = self.csv('relatorio=alertas')
        self.assertEqual(len(rows), 2)
        self.assertIn('ESTOQUE BAIXO', rows[1])
        self.assertIn('8', rows[1])

    def test_validacao_filtros_e_exportacao(self):
        self.login()
        for query in ['inicio=2026-02-30', 'inicio=2026-11-03&fim=2026-11-01',
                      'tipo=INVALIDO', 'produto_id=abc', 'setor_id=-1',
                      'relatorio=desconhecido', 'relatorio=estoque&inicio=2026-11-01',
                      'relatorio=alertas&setor_id=1']:
            for path in ['/relatorios/', '/relatorios/exportar']:
                with self.subTest(query=query, path=path):
                    self.assertEqual(self.client.get(path+'?'+query).status_code, 400)

    def test_perfis_vazio_e_somente_leitura(self):
        for path in ['/relatorios/', '/relatorios/exportar']:
            self.assertEqual(self.client.get(path).status_code, 302)
        for perfil in ['admin', 'operador']:
            self.client = self.app.test_client()
            self.login(perfil)
            self.assertIn('Nenhum registro', self.client.get('/relatorios/').get_data(as_text=True))
            self.assertEqual(len(self.csv('')), 1)
        self.assertEqual(self.sql('SELECT * FROM movimentacoes'), [])

    def test_csv_neutraliza_formulas_e_html_escapa(self):
        self.preparar()
        self.sql("UPDATE produtos SET nome='=1+1'")
        self.sql("UPDATE movimentacoes SET observacao='<script>alert(1)</script>; teste'")
        rows = self.csv('')
        self.assertIn("'=1+1", rows[1])
        html = self.client.get('/relatorios/').get_data(as_text=True)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertNotIn(self.password_hash, html)

    def test_historico_inativo_preservado_alerta_exclui(self):
        self.preparar()
        self.sql("UPDATE produtos SET status='INATIVO'")
        self.assertEqual(len(self.csv('')), 4)
        self.assertEqual(len(self.csv('relatorio=alertas')), 1)
        self.assertEqual(len(self.csv('relatorio=estoque')), 3)
