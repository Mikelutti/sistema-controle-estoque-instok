"""
app/repositories/categoria_repository.py

Responsabilidade:
- Executar todo o SQL relacionado a entidade "categorias" (tabela
  "categorias" definida em database/schema.sql).
- Esta e a UNICA camada autorizada a montar/executar queries de categorias.
- Recebe conexoes de app/database/connection.py.
- E consumida exclusivamente por app/services/categoria_service.py.

Funcoes previstas (a implementar futuramente):
- listar_categorias: retornar todas as categorias cadastradas (ativas).
- buscar_categoria: retornar uma categoria a partir do seu ID.
- inserir_categoria: criar um novo registro de categoria.
- atualizar_categoria: atualizar dados de uma categoria existente.
- inativar_categoria: marcar uma categoria como inativa (exclusao logica).

Nesta etapa do projeto, apenas a estrutura esta preparada (sem logica
implementada), conforme solicitado.
"""


# TODO: listar todas as categorias cadastradas (considerar apenas ativas)
def listar_categorias():
    pass


# TODO: buscar categoria por ID
def buscar_categoria(categoria_id):
    pass


# TODO: inserir uma nova categoria
def inserir_categoria(*args, **kwargs):
    pass


# TODO: atualizar dados de uma categoria existente
def atualizar_categoria(categoria_id, *args, **kwargs):
    pass


# TODO: inativar categoria (exclusao logica, nunca fisica)
def inativar_categoria(categoria_id):
    pass
