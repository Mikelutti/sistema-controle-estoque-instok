"""
run.py

Ponto de entrada da aplicacao Flask.

Responsabilidade:
- Importar a fabrica de aplicacao (create_app) definida em app/__init__.py
- Instanciar a aplicacao Flask
- Executar o servidor de desenvolvimento

Este arquivo NAO deve conter regras de negocio nem definicao de rotas.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True apenas para desenvolvimento local.
    # Em producao, este valor deve vir de uma variavel de ambiente/configuracao.
    app.run(debug=True)

from app import create_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)