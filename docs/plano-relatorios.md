# Relatórios — InStok

Etapa autorizada em 11/11/2026. Escopo: consultas e CSV de movimentações,
estoque atual por setor/categoria e alertas globais por produto. Sem mudanças
no schema, no banco real, commits ou push.

## Regras e decisões

- Administrador e operador ativos consultam e exportam; visitante precisa entrar.
- Filtros combinados por produto e categoria em todos os relatórios. Listas incluem
  cadastros inativos para permitir localizar o histórico.
- Movimentações: datas inclusivas em UTC, tipo e setor (origem OU destino).
  Preservar eventos de produtos inativos; nomes e categorias são os atuais.
- Estoque: saldos atuais por setor, inclusive produtos inativos e produtos sem
  movimentação. Não representa saldo em uma data passada. Mínimo é global, não por setor.
- Alertas: produtos ativos com saldo zero ou positivo até o mínimo, somando todos
  os setores em Python para não estourar o INTEGER do SQLite. Não aceita filtro de setor.
- Filtros incompatíveis são recusados com mensagem e HTTP 400, sem serem ignorados.
- CSV: mesmos filtros, nova consulta no download, UTF-8 com BOM, separador ponto e
  vírgula, escape CSV e neutralização de células com prefixo de fórmula.
- Sem paginação ou limite de registros nesta entrega; grandes volumes exigirão
  paginação e exportação em lotes antes de adoção em escala. Sem PDF nesta etapa.

## Arquivos e execução

Repository `app/repositories/relatorio_repository.py`: SELECTs parametrizados.
Service `app/services/relatorio_service.py`: validação, agregação de alertas e CSV.
Routes `app/routes/relatorios.py`: GET `/relatorios/` e `/relatorios/exportar`.
Template `app/templates/relatorios/index.html`: filtros e tabela com CSS dos cadastros.
Testes `tests/test_relatorios.py`: bancos descartáveis, limites de datas, filtros,
CSV, permissões, cadastros inativos, escape HTML e ausência de escrita.

## Roteiro manual

Usar a prévia temporária descrita no README. Registrar entrada de 10, saída de 2
e transferência de 3. Consultar as três operações em Relatórios. Filtrar por saída
e conferir apenas uma linha. Filtrar pelo setor destino da transferência e conferir
o evento. Baixar CSV e comparar as colunas e registros. Consultar estoque por setor
e conferir 5 na origem e 3 no destino. Definir mínimo 8 e conferir alerta de estoque
baixo com saldo total 8, sem duplicação por setor. Testar período inválido, filtros
sem resultado e acesso como operador. Conferir largura de 390px e temas.

## Resultado da validação

88 testes aprovados em 38,244 segundos; 7 testes específicos também passaram
após ajuste final do template. Conferência visual no navegador pendente.
Banco real preservado (SHA256 8BFF7B91E5C89BCDBB5CC85D813C40F04A64932AF174B4FDD69CA5E74256EFF8).
