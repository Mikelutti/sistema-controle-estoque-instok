"""
app/repositories/produto_repository.py

Responsabilidade:
- Executar todo o SQL relacionado a entidade "produtos" (tabela
  "produtos" definida em database/schema.sql).
- Esta e a UNICA camada autorizada a montar/executar queries de produtos.
- Recebe conexoes de app/database/connection.py.
- E consumida exclusivamente por app/services/produto_service.py.

IMPORTANTE:
A quantidade atual de um produto NUNCA e armazenada na tabela
"produtos". Isso e responsabilidade da tabela "estoques", tratada em
app/repositories/estoque_repository.py.

Funcoes previstas (a implementar futuramente):
- listar_produtos: retornar todos os produtos cadastrados (ativos).
- buscar_produto_por_id: retornar um produto a partir do seu ID.
- buscar_produto_por_codigo: retornar um produto a partir do codigo.
- inserir_produto: criar um novo registro de produto.
- atualizar_produto: atualizar dados de um produto existente.
- inativar_produto: marcar um produto como inativo (exclusao logica).
- consultar_estoque_minimo: retornar o valor de estoque_minimo
  configurado para um produto.

Nesta etapa do projeto, apenas a estrutura esta preparada (sem logica
implementada), conforme solicitado.
"""


# TODO: listar todos os produtos cadastrados (considerar apenas ativos)
def listar_produtos():
    pass


# TODO: buscar produto por ID
def buscar_produto_por_id(produto_id):
    pass


# TODO: buscar produto por codigo
def buscar_produto_por_codigo(codigo):
    pass


# TODO: inserir um novo produto
def inserir_produto(*args, **kwargs):
    pass


# TODO: atualizar dados de um produto existente
def atualizar_produto(produto_id, *args, **kwargs):
    pass


# TODO: inativar produto (exclusao logica, nunca fisica)
def inativar_produto(produto_id):
    pass


# TODO: consultar o estoque_minimo configurado para um produto
def consultar_estoque_minimo(produto_id):
    pass
