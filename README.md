# Sistema de Controle de Estoque

Sistema academico para gerenciamento e rastreabilidade de materiais.

## Funcionalidades previstas

- Login
- Usuarios
- Produtos
- Categorias
- Setores
- Entrada
- Saida
- Transferencia
- Inventario
- Historico de movimentacoes
- Alertas de estoque baixo
- Alertas de produtos sem estoque
- Relatorios
- Dashboard

## Tecnologias

- Python
- Flask
- HTML
- CSS
- JavaScript
- SQL
- SQLite (inicialmente)
- Git
- GitHub

## Status

Em desenvolvimento.

## Estrutura do projeto

```
sistema-controle-estoque/
├── app/
│   ├── __init__.py         -> fabrica da aplicacao Flask (create_app)
│   ├── routes/              -> rotas HTTP de cada modulo do sistema
│   ├── services/             -> regras de negocio (validacoes, alertas)
│   ├── templates/            -> paginas HTML (Jinja2), organizadas por modulo
│   └── static/                -> CSS, JavaScript e imagens
│
├── database/
│   ├── schema.sql            -> estrutura das tabelas do banco de dados
│   └── seed.sql               -> dados iniciais de exemplo
│
├── docs/                        -> documentacao do projeto (escopo, requisitos, etc)
├── tests/                        -> testes automatizados
│
├── run.py                        -> ponto de entrada da aplicacao
├── requirements.txt              -> dependencias do projeto
├── .gitignore
└── README.md
```

## Como executar (ambiente de desenvolvimento)

1. Crie e ative um ambiente virtual Python.
2. Instale as dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Execute a aplicacao:
   ```
   python run.py
   ```

## Observacoes

- Este projeto esta em fase inicial: a estrutura de pastas e arquivos
  esta pronta, mas grande parte da logica ainda sera implementada
  (marcada com comentarios `TODO`).
- Nenhuma senha ou credencial deve ser adicionada diretamente no codigo.
