"""
app/repositories/usuario_repository.py

Responsabilidade:
- Executar todo o SQL relacionado a entidade "usuarios" (tabela
  "usuarios" definida em database/schema.sql).
- Esta e a UNICA camada autorizada a montar/executar queries de usuarios.
- Recebe conexoes de app/database/connection.py.
- E consumida exclusivamente por app/services/usuario_service.py e
  app/services/auth_service.py.

Funcoes previstas (a implementar futuramente):
- buscar_usuario_por_id: retornar um usuario a partir do seu ID.
- buscar_usuario_por_login: retornar um usuario a partir do login.
- buscar_usuario_por_email: retornar um usuario a partir do e-mail.
- listar_usuarios: retornar todos os usuarios cadastrados (ativos).
- inserir_usuario: criar um novo registro de usuario.
- atualizar_usuario: atualizar dados de um usuario existente.
- inativar_usuario: marcar um usuario como inativo (exclusao logica,
  nunca exclusao fisica).

Nesta etapa do projeto, apenas a estrutura esta preparada (sem logica
implementada), conforme solicitado.
"""


# TODO: buscar usuario por ID
def buscar_usuario_por_id(usuario_id):
    pass


# TODO: buscar usuario por login
def buscar_usuario_por_login(login):
    pass


# TODO: buscar usuario por e-mail
def buscar_usuario_por_email(email):
    pass


# TODO: listar todos os usuarios cadastrados (considerar apenas ativos)
def listar_usuarios():
    pass


# TODO: inserir um novo usuario
def inserir_usuario(*args, **kwargs):
    pass


# TODO: atualizar dados de um usuario existente
def atualizar_usuario(usuario_id, *args, **kwargs):
    pass


# TODO: inativar usuario (exclusao logica, nunca fisica)
def inativar_usuario(usuario_id):
    pass
