"""Real stock summaries using isolated databases."""
import unittest
from test_estoque import EstoqueFixture
from app.services import alerta_service

class AlertasTests(EstoqueFixture, unittest.TestCase):
    def resumo(self):
        with self.app.app_context():
            return alerta_service.obter_resumo()

    def test_limites_exclusivos(self):
        for q, m, expected in [(0,0,'SEM ESTOQUE'),(0,5,'SEM ESTOQUE'),(1,5,'ESTOQUE BAIXO'),(5,5,'ESTOQUE BAIXO'),(6,5,'ESTOQUE NORMAL'),(1,0,'ESTOQUE NORMAL')]:
            with self.subTest(q=q,m=m):
                self.assertEqual(alerta_service.obter_status_estoque(q,m),expected)

    def test_sem_movimentacao_e_inativo(self):
        r=self.resumo()
        self.assertEqual((r['total_produtos'],r['total_unidades']),(1,0))
        self.assertEqual(len(r['sem_estoque']),1)
        self.assertEqual(r['estoque_baixo'],[])
        self.sql("UPDATE produtos SET status='INATIVO'")
        self.assertEqual(self.resumo()['total_produtos'],0)

    def test_soma_setores_sem_duplicar_e_sem_overflow(self):
        self.sql('UPDATE produtos SET estoque_minimo=5')
        self.sql('INSERT INTO estoques(produto_id,setor_id,quantidade) VALUES (1,1,3),(1,2,3)')
        r=self.resumo()
        self.assertEqual((r['total_produtos'],r['total_unidades'],r['total_normal']),(1,6,1))
        self.sql('UPDATE estoques SET quantidade=9223372036854775807')
        self.assertEqual(self.resumo()['total_unidades'],18446744073709551614)

    def test_atualiza_apos_movimentacoes(self):
        self.login()
        self.sql('UPDATE produtos SET estoque_minimo=5')
        self.post('/estoque/entrada',self.dados(quantidade='6',setor_destino_id='1'))
        self.assertEqual(self.resumo()['total_normal'],1)
        self.post('/estoque/transferencia',self.dados(quantidade='2'))
        self.assertEqual(self.resumo()['total_unidades'],6)
        self.post('/estoque/saida',self.dados(quantidade='1'))
        self.assertEqual(len(self.resumo()['estoque_baixo']),1)
        self.assertEqual(self.resumo()['sem_estoque'],[])

    def test_paginas_e_perfis(self):
        for path in ['/dashboard/','/alertas/']:
            self.assertEqual(self.client.get(path).status_code,302)
        for perfil in ['admin','operador']:
            self.client = self.app.test_client()
            self.login(perfil)
            for path in ['/dashboard/','/alertas/']:
                response=self.client.get(path)
                self.assertEqual(response.status_code,200)
                html=response.get_data(as_text=True)
                self.assertIn('Sem estoque',html)
                self.assertNotIn('em construcao',html)
                self.assertNotIn(self.password_hash,html)

    def test_escape_e_vazio(self):
        self.login()
        self.sql("UPDATE produtos SET nome='<script>alert(1)</script>'")
        html=self.client.get('/alertas/').get_data(as_text=True)
        self.assertIn('&lt;script&gt;',html)
        self.assertNotIn('<script>alert(1)</script>',html)
        self.sql("UPDATE produtos SET status='INATIVO'")
        for path in ['/dashboard/','/alertas/']:
            self.assertIn('Nenhum produto ativo',self.client.get(path).get_data(as_text=True))
