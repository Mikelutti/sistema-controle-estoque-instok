"""
app/services/auth_service.py

Responsabilidade: regras de negocio relacionadas a autenticacao.

Funcoes previstas (a implementar futuramente):
- validar_login: verificar se as credenciais informadas correspondem
  a um usuario existente.
- validar_usuario_ativo: impedir login de usuarios inativos.
- verificar_senha: comparar a senha informada com o hash armazenado
  (nunca comparar senha em texto puro).
- controlar regras adicionais relacionadas a autenticacao (ex: numero
  de tentativas, expiracao de sessao) quando definidas futuramente.

IMPORTANTE:
Este service nunca deve armazenar ou comparar senha em texto puro.
Sempre utilizar hash (ex: werkzeug.security ou biblioteca equivalente,
a ser definida futuramente).

Nesta etapa do projeto, apenas a estrutura esta preparada (sem logica
implementada), conforme solicitado.
"""


# TODO: implementar validacao de login (usuario + senha)
def validar_login(*args, **kwargs):
    pass


# TODO: implementar validacao de usuario ativo (impedir login de
# usuarios inativos)
def validar_usuario_ativo(*args, **kwargs):
    pass


# TODO: implementar verificacao de senha via hash
# (nunca comparar senha em texto puro)
def verificar_senha(*args, **kwargs):
    pass
