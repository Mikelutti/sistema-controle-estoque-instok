# Etapa 1 — Autenticação e isolamento de testes

Plano da auditoria autorizado em 28/10/2026. Stack preservada: Flask,
Jinja2, Werkzeug e sqlite3. Sem commits, push ou alteração do banco local.

## Decisões desta entrega

- Configuração por variáveis de ambiente e por `create_app(test_config=None)`.
  SECRET_KEY obrigatória, sem segredo padrão; `.env` não é carregado automaticamente.
- Testes com unittest e SQLite em diretório temporário, sem nova dependência.
  TESTING exige caminho explícito e recusa o banco local do projeto.
- Sessão guarda apenas o ID. Usuário ativo e perfil são consultados a cada
  requisição; a camada HTTP recebe somente dados públicos do usuário.
- Todas as telas internas exigem autenticação; gestão de usuários exige
  ADMINISTRADOR. Demais permissões de escrita serão definidas nos respectivos CRUDs.
- CSRF nos métodos que alteram estado, inclusive login e logout. Logout via POST.
- Login funcional e navegação simples; as outras páginas continuam provisórias.
- Corrigir o script de teste para usar exclusivamente banco temporário.
  A conta irregular existente não será modificada nesta etapa.

## Execução e testes

1. Configuração e conexão: testes de chave ausente, configuração injetável,
   caminho isolado, foreign keys e bloqueio do banco real; implementar e verificar.
2. Autenticação e autorização: testes de formulário, credenciais, inativação,
   perfil atualizado, CSRF e logout; implementar services, proteção HTTP e templates.
3. Script seguro e documentação: testar constraints em banco temporário,
   documentar instalação/execução e rodar a suíte completa.
4. Revisão independente e correção de achados relevantes; comparar hash do banco
   local e revisar diff antes da entrega.

Arquivos principais: app/__init__.py, app/database/connection.py,
app/services/auth_service.py, app/routes/auth.py, app/security.py (novo),
app/templates/base.html, app/templates/auth/login.html,
app/templates/erro.html (novo), app/static/css/global.css,
app/static/css/login.css, run.py, .env.example, testar_banco.py,
tests/test_auth.py, tests/test_config.py (novo), tests/test_database.py (novo), README.md.

Dependências: configuração → conexão isolada → autenticação → proteção HTTP
e CSRF → interface. O script e os testes nunca devem depender do banco real.

## Progresso

- Auditoria concluída; implementação iniciada após autorização.
- Execução no diretório existente, sem operações Git de escrita; plano registrado
  aqui para manter o progresso verificável. Nenhum frontend adicional foi localizado.
- Etapa 1 (configuração): 7 testes falharam antes da implementação e passaram
  após a correção. Ajuste do teste para resolver aliases de caminhos do Windows.
- Etapa 2 (autenticação): formulário/CSRF e proteção de rotas falharam antes
  da implementação; os 16 testes de autenticação passaram após a correção.
- Etapa 3 (script): a verificação bloqueou sua tentativa de abrir o banco real
  antes da alteração. O script agora executa três testes reais de constraints
  em banco temporário. Suíte completa: 27 testes aprovados.
- Revisão independente somente leitura concluída, sem achados bloqueantes ou
  menores; o revisor repetiu a suíte (27 aprovados).
- Login, navegação até dashboard e logout confirmados no navegador com fixture
  temporária. A prévia foi encerrada ao terminar a verificação.
- `git diff --check` sem erros. SHA256 do banco local antes/depois idêntico:
  ED24DEA5F81F0E442963B0E226E354B4422CE1DCD55604C737A4E77DA0678A33.
- Pendências deliberadas: CRUDs e permissões de escrita, frontend externo,
  limitação de tentativas/hospedagem pública e saneamento autorizado da conta
  irregular. Sessões Flask não têm revogação centralizada de cópias de cookies;
  migrar para sessões no servidor, se esse requisito surgir, é outra entrega.
- Nenhum commit, push, migração ou alteração do banco local foi realizado.
