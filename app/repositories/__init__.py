"""
app/repositories/__init__.py

Responsabilidade:
- Marcar o diretorio "repositories" como um pacote Python.
- Esta camada e a UNICA responsavel por executar SQL relacionado as
  entidades do sistema (usuarios, categorias, produtos, setores,
  estoque, movimentacoes).
- Os repositories recebem conexoes fornecidas por
  app/database/connection.py.
- Sao consumidos exclusivamente pela camada app/services/.

IMPORTANTE:
- Rotas (app/routes/) NUNCA devem chamar repositories diretamente.
- Services (app/services/) NUNCA devem executar SQL diretamente;
  sempre delegam para esta camada.
"""
