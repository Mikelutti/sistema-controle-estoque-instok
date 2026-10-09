"""
app/services/__init__.py

Responsabilidade:
- Marcar o diretorio "services" como um pacote Python.
- Esta camada concentra as REGRAS DE NEGOCIO do sistema, separadas das
  rotas (app/routes/). As rotas chamam funcoes daqui; os services nao
  devem conhecer detalhes de HTTP (request/response).
"""
