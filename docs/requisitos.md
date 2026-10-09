# Requisitos

## Requisitos funcionais (previstos)

- RF01: o sistema deve permitir login e logout de usuarios.
- RF02: o sistema deve permitir cadastrar, editar e listar produtos.
- RF03: o sistema deve permitir cadastrar, editar e listar categorias.
- RF04: o sistema deve permitir cadastrar, editar e listar setores.
- RF05: o sistema deve permitir registrar entrada de produtos no estoque.
- RF06: o sistema deve permitir registrar saida de produtos do estoque,
  impedindo que a quantidade fique negativa.
- RF07: o sistema deve permitir transferencia de produtos entre setores.
- RF08: o sistema deve manter historico de todas as movimentacoes.
- RF09: o sistema deve alertar quando um produto estiver com estoque
  baixo (quantidade <= estoque_minimo) ou sem estoque (quantidade = 0).
- RF10: o sistema deve exibir relatorios basicos de estoque e movimentacoes.

## Requisitos nao funcionais (previstos)

- RNF01: o sistema deve ser simples o suficiente para fins academicos.
- RNF02: o banco de dados inicial sera SQLite, com estrutura organizada
  para permitir futura migracao para MySQL.
- RNF03: nenhuma senha ou credencial deve ser armazenada diretamente no
  codigo-fonte.

> Este documento sera detalhado ao longo do desenvolvimento do projeto.
