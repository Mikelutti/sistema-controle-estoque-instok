"""
app/repositories/estoque_repository.py

Responsabilidade:
- Repository CENTRAL do sistema: executa todo o SQL relacionado a
  entidade "estoques" (tabela "estoques" definida em
  database/schema.sql), que guarda a quantidade de cada produto por
  setor (produto_id, setor_id, quantidade).
- Esta e a UNICA camada autorizada a montar/executar queries de estoque.
- Recebe conexoes de app/database/connection.py.
- E consumida exclusivamente por app/services/estoque_service.py e
  app/services/alerta_service.py.

IMPORTANTE:
A quantidade atual de um produto NUNCA e armazenada na tabela
"produtos". Ela sempre e calculada/consultada a partir da tabela
"estoques" (por setor) e, quando necessario, somada entre setores.

Funcoes previstas (a implementar futuramente):
- buscar_quantidade_por_setor: quantidade de um produto em um
  determinado setor.
- listar_estoque_por_setor: listar todo o estoque (produtos e
  quantidades) de um determinado setor.
- listar_setores_por_produto: listar os setores que possuem
  determinado produto em estoque.
- somar_quantidade_total: somar a quantidade total de um produto
  entre todos os setores (SUM(estoques.quantidade)).
- adicionar_quantidade: aumentar a quantidade de um produto em um
  setor (usado em entradas e no destino de transferencias).
- remover_quantidade: reduzir a quantidade de um produto em um setor
  (usado em saidas e na origem de transferencias).
- criar_registro_produto_setor: criar o vinculo produto+setor em
  "estoques" quando ainda nao existir (quantidade inicial 0).
- consultar_produtos_abaixo_do_minimo: listar produtos cuja quantidade
  total esteja abaixo ou igual ao estoque_minimo configurado.

Nesta etapa do projeto, apenas a estrutura esta preparada (sem logica
implementada), conforme solicitado.
"""


# TODO: buscar a quantidade de um produto em um determinado setor
def buscar_quantidade_por_setor(produto_id, setor_id):
    pass


# TODO: listar todo o estoque (produtos + quantidades) de um setor
def listar_estoque_por_setor(setor_id):
    pass


# TODO: listar os setores que possuem determinado produto em estoque
def listar_setores_por_produto(produto_id):
    pass


# TODO: somar a quantidade total de um produto entre todos os setores
def somar_quantidade_total(produto_id):
    pass


# TODO: adicionar quantidade ao estoque de um produto em um setor
# (usado em entradas e no destino de uma transferencia)
def adicionar_quantidade(produto_id, setor_id, quantidade):
    pass


# TODO: remover quantidade do estoque de um produto em um setor
# (usado em saidas e na origem de uma transferencia).
# Nunca deve permitir que a quantidade fique negativa.
def remover_quantidade(produto_id, setor_id, quantidade):
    pass


# TODO: criar o registro produto+setor em "estoques" quando ainda nao
# existir (quantidade inicial 0)
def criar_registro_produto_setor(produto_id, setor_id):
    pass


# TODO: consultar produtos cuja quantidade total esteja abaixo ou
# igual ao estoque_minimo configurado (para uso futuro em alertas)
def consultar_produtos_abaixo_do_minimo():
    pass
