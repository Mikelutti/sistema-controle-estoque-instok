"""
app/repositories/setor_repository.py

Responsabilidade:
- Executar todo o SQL relacionado a entidade "setores" (tabela
  "setores" definida em database/schema.sql).
- Esta e a UNICA camada autorizada a montar/executar queries de setores.
- Recebe conexoes de app/database/connection.py.
- E consumida exclusivamente por app/services/setor_service.py.

Funcoes previstas (a implementar futuramente):
- listar_setores: retornar todos os setores cadastrados (ativos).
- buscar_setor: retornar um setor a partir do seu ID.
- inserir_setor: criar um novo registro de setor.
- atualizar_setor: atualizar dados de um setor existente.
- inativar_setor: marcar um setor como inativo (exclusao logica).

Nesta etapa do projeto, apenas a estrutura esta preparada (sem logica
implementada), conforme solicitado.
"""


# TODO: listar todos os setores cadastrados (considerar apenas ativos)
def listar_setores():
    pass


# TODO: buscar setor por ID
def buscar_setor(setor_id):
    pass


# TODO: inserir um novo setor
def inserir_setor(*args, **kwargs):
    pass


# TODO: atualizar dados de um setor existente
def atualizar_setor(setor_id, *args, **kwargs):
    pass


# TODO: inativar setor (exclusao logica, nunca fisica)
def inativar_setor(setor_id):
    pass
