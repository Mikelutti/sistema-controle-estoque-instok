"""
app/services/alerta_service.py

Responsabilidade: regras de negocio relacionadas aos alertas de estoque.

Regra de classificacao planejada para cada produto:
- quantidade == 0                  -> "SEM ESTOQUE"
- quantidade <= estoque_minimo     -> "ESTOQUE BAIXO"
- quantidade > estoque_minimo      -> "ESTOQUE NORMAL"

Funcoes previstas (a implementar futuramente):
- verificar_estoque_baixo: verificar se quantidade atual <= estoque_minimo.
- verificar_sem_estoque: identificar produtos com quantidade igual a zero.
- obter_status_estoque: retornar o status textual do estoque de um produto
  (SEM ESTOQUE / ESTOQUE BAIXO / ESTOQUE NORMAL).

Nesta etapa do projeto, apenas a estrutura esta preparada (sem logica
implementada), conforme solicitado.
"""


# TODO: verificar se a quantidade atual esta abaixo ou igual ao estoque minimo
def verificar_estoque_baixo(*args, **kwargs):
    pass


# TODO: identificar produtos sem estoque (quantidade == 0)
def verificar_sem_estoque(*args, **kwargs):
    pass


# TODO: retornar o status do estoque de um produto
# (SEM ESTOQUE / ESTOQUE BAIXO / ESTOQUE NORMAL)
def obter_status_estoque(*args, **kwargs):
    pass
