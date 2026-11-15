# InStok — movimentações, inventário e histórico

Próxima entrega autorizada em 05/11/2026 ao prosseguir com o projeto.
Base: 58 testes, cadastros e usuários ainda com alterações locais preservadas.
Sem commit/push, migração ou escrita no banco real.

## Decisões

ADMINISTRADOR e OPERADOR ativos podem registrar ENTRADA, SAIDA e TRANSFERENCIA.
Ator vem exclusivamente da sessão e é revalidado sob BEGIN IMMEDIATE. Produto e
setores devem existir e estar ativos; categoria inativa não invalida produtos
ativos já vinculados. Quantidade inteira positiva até o limite INTEGER SQLite;
saldo por produto/setor não pode exceder esse limite. Motivo obrigatório até 2000 caracteres nas novas movimentações (regra atualizada em 11/11/2026).
Origem e destino distintos. Entrada: somente destino; saída: somente origem;
transferência: ambos. Saldo e um único evento de histórico são gravados juntos.
Qualquer falha reverte a operação inteira. Sem edição/exclusão de histórico.

Inventário lista também produtos sem saldo e registros inativos existentes;
histórico mostra dados persistidos, ator e origem/destino, com horário UTC do banco.
Sem ajustes manuais de saldo, alertas, dashboard ou relatórios nesta entrega.
PRG evita reenvio ao atualizar página; não há garantia de idempotência entre
requisições POST distintas (integração/API com retentativas fica para outra etapa).

## Tarefas

- [x] Confirmar regressão e hash do banco real.
- [x] Escrever testes de HTTP/SQLite temporário: entrada, saída, transferência,
  quantidade inválida, saldo insuficiente, status, CSRF, autorização e ator forjado.
- [x] Implementar estoque_repository.py e movimentacao_repository.py com conexões
  compartilhadas; movimentacao_service.py para consulta e estoque_service.py para
  regras de movimentação. Reutilizar validadores de cadastro e transacao_escrita.
- [x] Integrar routes/estoque.py e movimentacoes.py, templates de formulário,
  inventário/histórico e estilos existentes. Preservar formulário em erro 400.
- [x] Testar rollback de transferência/histórico, concorrência de saídas,
  limite numérico, referências e bloqueios de inativação após movimentações.
- [x] Executar suíte completa, revisão independente e fluxos no navegador com
  banco descartável, incluindo operador e tela estreita.
- [x] Atualizar README, registrar resultados e comparar hash do banco real.

## Arquivos

Repositories: app/repositories/{estoque,movimentacao}_repository.py.
Services: app/services/{estoque,movimentacao}_service.py.
HTTP: app/routes/{estoque,movimentacoes}.py; templates/estoque/*,
templates/movimentacoes/index.html; CSS compartilhado de cadastros.
Testes: tests/test_estoque.py, tests/test_transferencias.py.

Hash inicial: 8BFF7B91E5C89BCDBB5CC85D813C40F04A64932AF174B4FDD69CA5E74256EFF8.

## Resultado em 05/11/2026

- Baseline: 58 testes aprovados. Testes novos falharam antes da implementação,
  demonstrando rotas POST e lógica de movimentação ausentes.
- Suíte final: 75 testes aprovados em 35,330s, exclusivamente em SQLite temporário.
- Revisão independente: sem achados materiais; repetiu os 17 testes específicos
  de estoque e transferências, todos aprovados.
- Navegador como operador: entrada de 10 no Setor inicial, saída de 3 e transferência
  de 4 para Destino. Inventário confirmou 3 na origem e 4 no destino; histórico
  confirmou exatamente três eventos com responsável e observações.
- Tentativa de saída de 99 negada sem alterar saldo nem registrar novo evento.
- Layout verificado em 390×844, menu móvel e temas claro/escuro; largura mínima
  do histórico ajustada para manter cabeçalhos legíveis com rolagem horizontal.
- Hash final do banco real idêntico ao inicial; git diff --check sem erros.
- Nenhum commit/push. Alterações anteriores de usuários/cadastros preservadas.
- A pedido do usuário, prévia temporária permanece aberta em 127.0.0.1:5058 para
  continuar testando. Dados e credenciais dessa prévia são descartáveis.
- Arquivos desta etapa: repositories e services de estoque/movimentações,
  respectivas rotas, templates/estoque/*, templates/movimentacoes/index.html,
  CSS compartilhado cadastros.css, tests/test_estoque.py e test_transferencias.py,
  README.md e este plano. Nenhuma alteração de schema.
- Pendências: alertas, dashboard, relatórios, filtros/paginação e futura política
  de estorno/idempotência. Histórico referencia nomes atuais dos cadastros; não
  há snapshot histórico de nomes, nem alteração/apagamento de movimentos.
