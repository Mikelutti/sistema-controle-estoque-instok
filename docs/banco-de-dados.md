# Banco de Dados

## Tabelas planejadas

- `usuarios`
- `categorias`
- `produtos`
- `setores`
- `estoques`
- `movimentacoes`

## Relacionamentos planejados

- `categorias` 1:N `produtos`
- `produtos` 1:N `estoques`
- `setores` 1:N `estoques`
- `usuarios` 1:N `movimentacoes`
- `produtos` 1:N `movimentacoes`
- `setores` podem ser origem e destino em `movimentacoes` (transferencias)

## Regra de status do estoque (aplicada na camada de servico)

- quantidade = 0 -> **SEM ESTOQUE**
- quantidade <= estoque_minimo -> **ESTOQUE BAIXO**
- quantidade > estoque_minimo -> **ESTOQUE NORMAL**

A estrutura conceitual das tabelas esta em `database/schema.sql`.

> Este documento sera detalhado ao longo do desenvolvimento do projeto.
