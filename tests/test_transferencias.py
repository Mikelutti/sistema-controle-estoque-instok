"""Atomicidade da transferência e conservação da quantidade total."""
import sqlite3
import unittest
from unittest.mock import patch
from test_estoque import EstoqueFixture


class TransferenciaTests(EstoqueFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.sql('INSERT INTO estoques(produto_id,setor_id,quantidade) VALUES (1,1,10)')
        self.login('operador')

    def test_transferencia_cria_destino_e_um_unico_historico(self):
        self.assertEqual(self.post('/estoque/transferencia', self.dados()).status_code, 302)
        self.assertEqual((self.saldo(), self.saldo(2)), (5,5))
        self.assertEqual(len(self.historico()), 1)
        row = self.historico()[0]
        self.assertEqual((row['tipo'], row['usuario_id'], row['setor_origem_id'], row['setor_destino_id']),
                         ('TRANSFERENCIA',2,1,2))
        self.assertEqual(self.post('/estoque/transferencia', self.dados()).status_code, 302)
        self.assertEqual((self.saldo(), self.saldo(2)), (0,10))
        self.assertEqual(self.sql('PRAGMA foreign_key_check'), [])

    def test_origem_igual_ausente_ou_insuficiente_e_rejeitada(self):
        for data in [self.dados(setor_destino_id='1'), self.dados(quantidade='11'),
                     self.dados(setor_origem_id='999'), self.dados(setor_destino_id='999'),
                     self.dados(setor_origem_id=''), self.dados(setor_destino_id='')]:
            self.assertEqual(self.post('/estoque/transferencia', data).status_code, 400)
            self.assertEqual((self.saldo(), self.saldo(2)), (10,0))
            self.assertEqual(self.historico(), [])

    def test_falha_no_credito_reverte_debito(self):
        with patch('app.repositories.estoque_repository.adicionar_quantidade',
                   side_effect=sqlite3.OperationalError('credito falhou')):
            with self.assertLogs(self.app.logger, level='ERROR'):
                response = self.post('/estoque/transferencia', self.dados())
        self.assertEqual(response.status_code, 503)
        self.assertEqual((self.saldo(), self.saldo(2)), (10,0))
        self.assertEqual(len(self.sql('SELECT * FROM estoques')), 1)
        self.assertEqual(self.historico(), [])

    def test_falha_no_historico_reverte_ambos_os_saldos(self):
        with patch('app.repositories.movimentacao_repository.registrar_movimentacao',
                   side_effect=sqlite3.OperationalError('historico falhou')):
            with self.assertLogs(self.app.logger, level='ERROR'):
                response = self.post('/estoque/transferencia', self.dados())
        self.assertEqual(response.status_code, 503)
        self.assertEqual((self.saldo(), self.saldo(2)), (10,0))
        self.assertEqual(len(self.sql('SELECT * FROM estoques')), 1)

    def test_destino_no_limite_nao_perde_saldo_na_origem(self):
        self.sql('INSERT INTO estoques(produto_id,setor_id,quantidade) VALUES (1,2,?)', (9223372036854775807,))
        self.assertEqual(self.post('/estoque/transferencia', self.dados()).status_code, 400)
        self.assertEqual((self.saldo(), self.saldo(2)), (10,9223372036854775807))
        self.assertEqual(self.historico(), [])
