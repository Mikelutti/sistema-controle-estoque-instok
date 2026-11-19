# InStok — categorias, setores e produtos

## Objetivo e decisões

Implementar o escopo enviado em 03/11/2026: consulta por usuários autenticados,
cadastro/edição/inativação por ADMINISTRADOR, preservando dados e histórico.
Flask → services → repositories → SQLite, com templates Jinja2 e visual atual.
Execução no diretório atual para preservar e utilizar a entrega de usuários ainda
não commitada. Nenhum commit/push ou alteração do banco real está autorizado.

O schema existente já suporta o escopo; não será necessária migração. Nomes de
categorias/setores e códigos de produtos terão strip e comparação sensível a
maiúsculas, como o UNIQUE BINARY existente. Inativos continuam reservando valores.
Limites: nome 150, descrição opcional 2000, código 80 caracteres; estoque mínimo
inteiro de 0 até 9223372036854775807 (limite INTEGER do SQLite). IDs positivos.
Essas escolhas de limites são decisões de implementação, documentadas na interface.

Validações de ator, duplicidade, categoria e saldo são feitas junto da escrita em
BEGIN IMMEDIATE. Categorias podem ser inativadas preservando produtos vinculados;
um produto pode manter sua categoria inativa, mas nunca receber uma nova associação
inativa. Produtos/setores com qualquer saldo positivo não podem ser inativados.
O cadastro não cria linhas de estoque e a edição não modifica saldos.

## Sequência e arquivos

- [x] Confirmar a regressão inicial de 41 testes e registrar o hash do banco.
- [x] Categorias: testar cadastro, edição, duplicidade, inativação e autorização;
  implementar categoria_repository.py, categoria_service.py, routes/categorias.py.
- [x] Setores: mesmos contratos, com bloqueio por saldo; implementar
  setor_repository.py, setor_service.py, routes/setores.py e consultas de saldo
  no estoque_repository.py. Consultas recebem a conexão da transação do service.
- [x] Produtos: testar código, categoria ativa/inativa, estoque mínimo, saldo e
  histórico; implementar produto_repository.py, produto_service.py, routes/produtos.py.
- [x] Interface: templates compartilhados de listagem/formulário em cadastros/,
  wrappers dos três módulos e CSS próprio, preservando o visual. HTTP 400 mantém
  dados e mensagens; 404 para registro ausente; 403 para operador em formulários.
- [x] Corrigir InStok na interface/documentação, preservando URLs e caminho do
  frontend de terceiros. Ajustar teste de autenticação para rotas parametrizadas.
- [x] Executar suíte completa, revisão independente e navegação em SQLite
  descartável: cadastro/edição/erros/inativação, operador, temas e largura 390px.
- [x] Documentar resultados, roteiro de prévia e comparar hash do banco real.

Helpers compartilhados: cadastro_service.py (validação textual/integer,
RegistroNaoEncontrado, autorização transacional e conflito de unicidade).
As funções públicas específicas de cada service mantêm os nomes do domínio;
templates compartilham apresentação, sem SQL ou regras de negócio.

## Critérios de conclusão e foco de revisão

Testes de integração em tests/test_cadastros.py verificam HTTP e SQLite real
temporário, incluindo campos enormes, inteiros fora de faixa, categoria inativa
preservada na edição, tentativa de forjar perfil/status/saldo, edição que conflita
com outro registro, status alterado durante sessão e integridade referencial.
Falhas de validação não podem gravar parcialmente nem vazar exceções SQL.
Teste concorrente deve demonstrar que a categoria não é associada com uma leitura
anterior ao lock de escrita. Saldo em qualquer setor deve bloquear inativação.

Hash inicial do banco real:
8BFF7B91E5C89BCDBB5CC85D813C40F04A64932AF174B4FDD69CA5E74256EFF8.


## Resultado em 03/11/2026

- Baseline confirmado: 41 testes aprovados antes da implementação.
- Onze testes iniciais dos novos cadastros demonstraram rotas/operações ausentes.
- Ampliação com seis testes de limites de IDs, preservação de saldo positivo,
  autorização nos services, perda de permissão e concorrência. IDs de URL zero
  ou fora de faixa inicialmente produziram exceção; corrigidos para resposta 404.
- Suíte completa: 58 testes aprovados em 25,851 segundos, todos com SQLite
  temporário. Revisão independente repetiu a suíte: 58 aprovados, sem achados.
- Navegador: criação e edição de categoria, setor e produto; nome obrigatório,
  duplicidade e formulário preservado; bloqueio por saldo para setor/produto;
  inativação de setor/produto sem saldo e categoria vinculada; edição mantendo
  categoria inativa; operador consulta três listas e não acessa formulário.
- Visual: InStok no login, logo, títulos e rodapé; temas claro/escuro;
  formulário e tabela em 390×844, menu móvel e fechamento por Escape.
- SHA256 final do banco real idêntico ao inicial. Sem alteração de schema.
- git diff --check sem erros de whitespace; apenas avisos de conversão LF/CRLF.
- Prévia descartável encerrada. O README contém comando e roteiro reproduzíveis.
- Nenhum commit/push. Mudanças anteriores de usuários e arquivo alheio
  `ntent .gitignore` foram preservados.

### Arquivos desta etapa

- app/database/connection.py: helper de leitura que reutiliza conexão transacional.
- app/repositories/{categoria,setor,produto}_repository.py: consultas e persistência.
- app/repositories/estoque_repository.py: existência de saldo por setor/produto.
- app/services/{cadastro,categoria,setor,produto}_service.py: validações e transações.
- app/routes/{cadastros,categorias,setores,produtos}.py: formulários e erros HTTP.
- app/security.py: operador limitado às listagens dos três novos módulos.
- app/templates/cadastros/{index,formulario}.html: apresentação compartilhada.
- app/templates/{categorias,setores,produtos}/{index,formulario}.html: integração.
- app/static/css/cadastros.css: temas e comportamento responsivo.
- app/templates/base.html, auth/login.html, erro.html e usuarios/{index,formulario}.html:
  correção da marca para InStok.
- tests/test_cadastros.py: 17 testes com múltiplos cenários por módulo.
- tests/test_auth.py: validação de login nas novas URLs parametrizadas.
- README.md, docs/plano-integracao-frontend.md e este plano: documentação e nome.

### Limitações deliberadas

Movimentações, inventário, alertas, dashboard e relatórios continuam pendentes.
Não há reativação, exclusão física, paginação ou filtros nesta entrega.
As movimentações futuras precisam validar produto/setor ativo sob transação;
nenhuma rotina de entrada/saída/transferência foi adicionada aqui.
