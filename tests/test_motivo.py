"""Motivo obrigatório, validado antes de alterar saldos ou histórico."""
import unittest
from test_estoque import EstoqueFixture
from app.services.estoque_service import movimentar


class MotivoTests(EstoqueFixture, unittest.TestCase):
    def test_http_recusa_motivo_vazio_em_todas_operacoes(self):
        self.login()
        self.post('/estoque/entrada', self.dados(quantidade='10', setor_destino_id='1'))
        for operacao in ['entrada', 'saida', 'transferencia']:
            for valor in ['', '   ', '\t\n']:
                with self.subTest(operacao=operacao, valor=valor):
                    resposta = self.post('/estoque/'+operacao, self.dados(observacao=valor))
                    self.assertEqual(resposta.status_code, 400)
                    self.assertIn('motivo', resposta.get_data(as_text=True).lower())
                    self.assertEqual((self.saldo(1), self.saldo(2)), (10, 0))
                    self.assertEqual(len(self.historico()), 1)
        dados = self.dados()
        del dados['observacao']
        self.assertEqual(self.post('/estoque/entrada', dados).status_code, 400)

    def test_service_recusa_ausente_nulo_e_invalido(self):
        with self.app.app_context():
            for valor in [None, '', '  ', 123, 'x'*2001]:
                with self.subTest(valor=valor):
                    with self.assertRaises(ValueError):
                        movimentar('ENTRADA', 1, 1, usuario_id=1,
                                   setor_destino_id=1, observacao=valor)
            with self.assertRaises(ValueError):
                movimentar('ENTRADA', 1, 1, usuario_id=1, setor_destino_id=1)
        self.assertEqual(self.historico(), [])
        self.assertEqual(self.saldo(), 0)

    def test_limite_normalizacao_e_formularios(self):
        self.login('operador')
        for operacao in ['entrada', 'saida', 'transferencia']:
            html = self.client.get('/estoque/'+operacao).get_data(as_text=True)
            self.assertRegex(html, r'<textarea[^>]*name="observacao"[^>]*required')
        motivo = 'x'*2000
        self.assertEqual(self.post('/estoque/entrada', self.dados(observacao=' '+motivo+' ')).status_code, 302)
        self.assertEqual(self.historico()[0]['observacao'], motivo)
