# Motivo obrigatório — InStok

Etapa de alinhamento com a avaliação, executada em 11/11/2026.
Entradas, saídas e transferências novas exigem motivo não vazio após remover
espaços nas extremidades, até 2000 caracteres. O campo técnico continua
observacao, preservando schema, histórico, relatórios e integrações existentes.
A validação ocorre no service antes de qualquer alteração de saldo ou histórico.
O formulário possui required e ajuda explicando a finalidade do motivo.

Sem migração ou preenchimento artificial dos registros antigos. Administradores
e operadores mantêm a autorização de movimentar; o usuário vem da sessão.

Testes em tests/test_motivo.py: motivo omitido, vazio, espaços, nulo, tipo inválido,
limite de tamanho, normalização e exigência no HTML dos três formulários.
Confirmar que uma tentativa inválida não grava evento nem altera saldo.

Roteiro manual em banco descartável: abrir Entrada, tentar enviar sem motivo;
preencher motivo, registrar e conferir o texto no Histórico e no CSV. Repetir
Saída e Transferência com saldo suficiente. O banco real não deve ser usado.
