# Arquitetura

## Visao geral

O projeto segue uma separacao simples em camadas:

- **app/routes/**: camada de apresentacao/controle. Recebe requisicoes
  HTTP e devolve respostas (paginas HTML), delegando regras de negocio
  para a camada de services.
- **app/services/**: camada de regras de negocio (ex: validar entrada e
  saida de estoque, calcular status de alerta).
- **app/templates/**: camada de visualizacao (HTML + Jinja2).
- **app/static/**: arquivos estaticos (CSS, JavaScript, imagens).
- **database/**: definicao da estrutura do banco de dados (SQL).

## Fluxo basico (planejado)

1. O usuario acessa uma rota (ex: `/estoque/entrada`).
2. A rota correspondente em `app/routes/` recebe a requisicao.
3. A rota chama uma funcao da camada `app/services/` para aplicar as
   regras de negocio (ex: validar se a entrada e valida).
4. O resultado e usado para renderizar um template HTML de resposta.

## Banco de dados

Inicialmente SQLite (arquivo local), com scripts SQL padronizados em
`database/schema.sql`, de forma a facilitar uma futura migracao para
MySQL sem necessidade de reescrever a logica da aplicacao.

> Este documento sera detalhado ao longo do desenvolvimento do projeto.
