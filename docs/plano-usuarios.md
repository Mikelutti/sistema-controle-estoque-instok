# Gerenciamento de usuários

Escopo autorizado: listagem, cadastro, edição e inativação pela interface.
Sem commit, push, migração ou escrita no banco real.

1. Testar contratos HTTP com SQLite temporário: permissões, CSRF, validação,
   duplicidade, edição, último administrador, sessões e histórico.
2. Implementar repository com conexão compartilhada e transação de escrita;
   service valida dados e preserva o último administrador ativo na mesma transação.
3. Integrar rotas e templates ao visual existente, com mensagens e layout móvel.
4. Executar regressão, testar no navegador com banco descartável, revisar diff
   e comparar o hash do banco real.

Dependências: conexão/transação → repositories → services → rotas → templates.
Login permanece sensível a maiúsculas; e-mail é normalizado com strip/lower.
Cadastros novos exigem senha de pelo menos oito caracteres; senhas existentes
não são alteradas. O cadastro por script continua disponível para instalação.
Nenhuma página recebe hashes; consultas destinadas à autenticação são separadas.
Não haverá reativação, exclusão física nem recuperação de senha nesta entrega.

## Validação em 30/10/2026

- Oito testes iniciais demonstraram falhas antes da implementação (rotas ausentes).
- Suíte ampliada para 41 testes, incluindo duas inativações simultâneas,
  autorização do ator no service, hash preservado na edição e escape de HTML.
- Revisão independente somente leitura: nenhum achado concreto; 41 testes
  aprovados pelo revisor, exclusivamente em bancos temporários.
- Navegador em banco descartável: login admin, cadastro de operador, edição,
  login operador e acesso administrativo bloqueado, inativação e login negado.
- Layout verificado em desktop e 390×844: formulário em uma coluna, tabela com
  rolagem horizontal, tema escuro, menu móvel e fechamento por Escape.
- Mantidos Flask/Jinja2/SQLite, arquitetura em camadas e identidade visual da equipe.
- Banco real preservado; hash inicial desta etapa:
  8BFF7B91E5C89BCDBB5CC85D813C40F04A64932AF174B4FDD69CA5E74256EFF8.
- Sem commit ou push; arquivo alheio `ntent .gitignore` preservado.

Arquivos: connection.py (transação), usuario_repository.py (SQL e projeções
públicas), usuario_service.py (regras), routes/usuarios.py, templates/usuarios/*,
static/css/usuarios.css, global.css e partial de mensagens, tests/test_usuarios.py,
tests/test_auth.py (cobertura de rotas parametrizadas), README.md e este plano.
