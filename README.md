# InStok — Sistema de Controle de Estoque

Projeto acadêmico em Python, Flask, Jinja2, HTML/CSS/JavaScript e SQLite.
Arquitetura: routes → services → repositories → database/connection.

## Primeiro acesso no Windows

Abra o PowerShell na pasta do projeto, onde estão `requirements.txt` e `run.py`.
Instale o Python 3 com o comando `python` disponível (versão validada: 3.14.7).
Prepare o ambiente uma vez:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Demonstração para a equipe

```powershell
.\.venv\Scripts\python.exe demo.py
```

Acesse http://127.0.0.1:5058. Contas **exclusivas desta prévia descartável**:
`admin` e `operador`, senha `senha-somente-dos-testes`. Nunca use essas credenciais
em instalação real. Encerre com Ctrl+C; uma nova execução começa com dados novos.

Roteiro: entre como admin, cadastre um operador, edite nome/login/e-mail, saia,
entre como esse operador e abra `/usuarios/` para conferir o bloqueio. Retorne
como admin, inative a conta e confira que seu login deixou de funcionar. Tente
inativar o único admin e confira a validação. Em largura de 390px, confira o
formulário em uma coluna, a rolagem horizontal da tabela e o menu móvel.

A prévia também cria **Categoria inicial**, **Setor inicial**, **Destino** e
**Produto inicial**, sem saldo e sem histórico no banco descartável. Registre
entrada de 10 no Setor inicial, saída de 3 e transferência de 4 para Destino:
o inventário deve mostrar 3 na origem e 4 no destino, com três eventos no histórico.
Uma saída de 99 deve falhar sem alterar os saldos. Use esses registros para
verificar o bloqueio de inativação por saldo. Cadastre outra categoria, um
setor e um produto; edite-os e tente duplicar nome/código. Inative a nova categoria
e confira que o produto mantém o vínculo, mas novos produtos não podem escolhê-la.
Inative o novo produto e o novo setor, que não possuem saldo. Entre como operador
e confira as três listagens e o bloqueio de `/produtos/formulario`.

### Instalação local com dados persistentes

Em uma instalação nova, execute na raiz do projeto, na ordem abaixo. O primeiro
script cria as tabelas. No segundo, informe nome, login, e-mail e senha do administrador.
A senha deve ter entre 8 e 256 caracteres e fica oculta enquanto você digita.

```powershell
$env:DATABASE_PATH = "instance/instok.db"
.\.venv\Scripts\python.exe inicializar_banco.py
.\.venv\Scripts\python.exe criar_admin.py
```

Depois das mensagens de sucesso, execute no mesmo terminal:

```powershell
$env:DATABASE_PATH = "instance/instok.db"
$env:SECRET_KEY = (& .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))")
$env:FLASK_DEBUG = "false"
.\.venv\Scripts\python.exe run.py
```

Entre em http://127.0.0.1:5000 com o login criado. Em instalações existentes,
inicie pelo comando de execução com a chave configurada. Guarde a chave fora do Git
para reutilizá-la entre sessões. Trocar a chave desconecta os usuários.

`.env.example` documenta as variáveis, mas **run.py não carrega `.env`
automaticamente**. Defina-as no ambiente. `DATABASE_PATH` aceita caminho absoluto
ou relativo à raiz do projeto; o padrão é `instance/controle_estoque.db`.
`FLASK_DEBUG=true` é apenas para desenvolvimento. Em hospedagem HTTPS, configure
`SESSION_COOKIE_SECURE=true`; o servidor de desenvolvimento Flask não é uma
configuração de produção.

## Estado atual

Implementados nesta etapa: login com hash de senha, sessão, logout por POST,
proteção das páginas internas, gestão de usuários restrita a administradores,
CSRF e testes com banco temporário. Status e perfil são revalidados em cada
requisição autenticada. A sessão dura até oito horas sem renovação; o uso da
aplicação renova esse prazo. A sessão não contém senhas ou hashes.

O gerenciamento de usuários inclui listagem de ativos e inativos, cadastro,
edição de dados/perfil e inativação, restritos a administradores. Categorias,
setores e produtos também possuem listagem, cadastro, edição e inativação.
Operadores consultam esses três cadastros; administradores podem alterá-los.
Entradas, saídas, transferências, inventário por setor e histórico estão
implementados. Dashboard e alertas exibem dados reais de produtos ativos.
Relatórios permite consultar movimentações, estoque atual e alertas, com CSV. Os links de navegação não indicam que esses módulos estejam
concluídos. Login, menu lateral e temas usam o visual desenvolvido pela equipe,
adaptado aos templates Flask. O login é por usuário cadastrado, sem seleção de
perfil ou credenciais demonstrativas.

## Frontend integrado

Referência: [frontend da equipe, commit f999815](https://github.com/Mikelutti/sistema-controle-estoque-instok/commit/f999815540e44fd1ca8e051efb99d355382860e1),
arquivos `InStock Controle de Estoque frontend/index.html`, `styles.css` e
`script.js`. A adaptação preserva a paleta azul-marinho, composição do login,
menu lateral e temas. A fonte Manrope vem do Google Fonts com fallback Arial
quando o serviço não está disponível.

O JavaScript controla tema, visibilidade da senha e menu móvel. A preferência
de tema é o único dado salvo em localStorage. Login, logout e navegação usam
formulários e URLs reais; autenticação e permissões permanecem no servidor.
Não foram importados produtos, movimentos ou indicadores demonstrativos.

Verificação manual: entrar com uma conta existente, alternar tema, navegar
entre páginas e sair. Em tela estreita, abrir/fechar o menu e usar Escape.
O menu de usuários só aparece para administradores. Administradores e operadores
ativos podem registrar movimentações. O nome exibido na aplicação é **InStok**; caminhos
de arquivos do frontend de terceiros e a chave técnica de preferência de tema
foram preservados.

## Categorias, setores e produtos

Entre como administrador e abra o módulo no menu. Use **Cadastrar**, **Editar**
ou **Inativar → Confirmar inativação**. A listagem inclui ativos e inativos;
o operador consulta os registros sem acesso a formulários ou alterações.

- Categorias e setores: nome obrigatório de até 150 caracteres e descrição
  opcional de até 2000 caracteres.
- Produtos: código obrigatório e único de até 80 caracteres, nome, descrição,
  categoria e estoque mínimo inteiro não negativo. O máximo aceito é
  9223372036854775807, limite do INTEGER SQLite.
- Espaços nas extremidades são removidos. Nomes de categorias/setores e códigos
  de produtos diferenciam maiúsculas de minúsculas, acompanhando o UNIQUE atual:
  `P1` e `p1` são códigos diferentes. Inativos continuam reservando nomes/códigos.
- Uma categoria inativa não pode receber novas associações. Produtos já
  vinculados podem manter essa categoria durante a edição; a listagem identifica
  o vínculo inativo. Inativar a categoria não inativa seus produtos.
- Produtos e setores com qualquer saldo positivo não podem ser inativados.
  Registros, vínculos e histórico são preservados. Não há exclusão física ou
  reativação pela interface nesta etapa.
- Cadastro/edição de produtos não cria ou modifica saldos. Estoque mínimo é
  um parâmetro cadastral, não representa a quantidade disponível.

Autorização, duplicidade, categoria e saldo são revalidados na mesma transação
de escrita. Não foi necessária mudança de schema. As movimentações também
validam status e saldo dentro de sua própria transação.

## Movimentar estoque

ADMINISTRADOR e OPERADOR ativos podem usar **Entrada de produtos**, **Saída de
produtos** e **Transferências**. Selecione um produto ativo, os setores ativos e
uma quantidade inteira positiva. O motivo da movimentação é obrigatório (até 2000 caracteres), registrado no campo observação do histórico.

- Entrada soma unidades no destino; saída retira da origem e recusa saldo
  insuficiente. Transferência exige dois setores diferentes e conserva o total.
- Ator vem da sessão. Status e saldo são revalidados sob `BEGIN IMMEDIATE`;
  saldo e um evento de histórico são gravados na mesma transação. Falhas não
  deixam transferência parcial. Saldo por produto/setor respeita INTEGER SQLite.
- **Inventário** mostra quantidades por produto/setor, produtos sem movimentação
  e registros inativos existentes. **Histórico** mostra responsável, origem,
  destino e observação; horários são UTC. Não há edição/exclusão de histórico.
- Produto ativo pode movimentar mesmo com categoria inativa já vinculada.
  Produtos/setores inativos não movimentam. Cadastros com saldo continuam
  protegidos contra inativação.
- Após sucesso, a página redireciona ao inventário. Em erro, o formulário mantém
  os dados. Não reenvie intencionalmente a mesma operação: POSTs distintos são
  novas movimentações; não há chave de idempotência para retentativas de APIs.

Relatórios de consulta e exportação CSV também estão implementados. Não há ajuste direto de
saldo, estorno, edição do histórico, filtros ou paginação nesta entrega.

## Gerenciar usuários

Entre como administrador e abra **Usuários** no menu. Use **Cadastrar usuário**
para criar uma conta ou **Editar** para alterar seus dados/perfil. A senha inicial
deve ter de 8 a 256 caracteres; é armazenada somente como hash e nunca reaparece
no formulário. Edição não modifica senha nem status.

E-mails são normalizados para minúsculas e sem espaços nas extremidades; logins
são sensíveis a maiúsculas. Login/e-mail de contas inativas continuam reservados.
Validação de duplicidade exclui o próprio registro na edição. Conflitos de
unicidade retornam mensagem de validação, sem erro 500.

**Inativar → Confirmar inativação** bloqueia login e sessões existentes, mantendo
o registro e suas referências no histórico. O último administrador ativo não
pode ser inativado nem rebaixado. Essas verificações e a escrita compartilham
uma transação SQLite `BEGIN IMMEDIATE`, incluindo a revalidação do administrador
que executa a operação. Não há reativação, exclusão física ou recuperação de senha.

## Testes

Sem dependências adicionais: usa `unittest` da biblioteca padrão.

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -B testar_banco.py
```

Cada teste de integração cria SQLite em diretório temporário e o remove ao
terminar. `create_app` aceita configuração explícita; em `TESTING`, exige
`DATABASE_PATH` isolado e bloqueia o banco local. Não use o banco real em testes.
O script `testar_banco.py` executa somente os testes de constraints temporários
e retorna código diferente de zero se houver falha.

Há cobertura real em `test_auth.py`, `test_config.py`, `test_database.py`,
`test_script.py`, `test_usuarios.py`, `test_cadastros.py`, `test_estoque.py` e
`test_transferencias.py`. Em 05/11/2026, a suíte completa passou com **75 testes**,
incluindo rollback, saídas concorrentes e regressão de login, usuários e cadastros.
Em 09/11/2026, a suíte passou com **81 testes**, incluindo seis testes reais de
alertas/dashboard. Apenas `test_produtos.py` ainda contém um placeholder
`assert True`, não contabilizado pelo unittest; produtos têm cobertura real
em `test_cadastros.py`.

## Segurança e pendências

- Visitantes acessam login e arquivos estáticos; telas internas exigem sessão.
- O módulo de usuários exige ADMINISTRADOR. Categorias, setores e produtos permitem
  consulta pelo OPERADOR e alterações apenas pelo ADMINISTRADOR. A autorização do ator vem do banco; somente
  administradores podem atribuir o perfil de outra conta pelo formulário.
- Formulários POST devem conter `csrf_token`; APIs futuras podem enviar
  `X-CSRF-Token`. A validação também cobre PUT/PATCH/DELETE.
- Logout é POST com CSRF. Não reutilize links GET para encerrar sessões.
- A auditoria encontrou uma conta irregular produzida pelo script antigo.
  Ela não foi alterada; hashes inválidos não autenticam. O saneamento do banco
  depende de autorização separada.
- Limitação de tentativas de login e configuração de hospedagem ficam para a
  revisão de segurança antes de exposição pública.
- Nunca versione `.env`, banco local, ambiente virtual, senhas ou chaves.

Os planos e o progresso estão em `docs/plano-autenticacao.md`,
`docs/plano-integracao-frontend.md`, `docs/plano-usuarios.md` e
`docs/plano-cadastros.md` e `docs/plano-estoque.md`.

## Dashboard e alertas

Administrador e operador podem consultar `/dashboard/` e `/alertas/`.
O painel mostra produtos ativos, unidades totais, produtos sem estoque e com
estoque baixo. Os alertas listam código, nome, categoria, saldo total e mínimo.
O saldo é somado entre todos os setores, sem duplicar produtos. Produtos inativos
não entram; produtos ativos com categoria inativa continuam sendo considerados.

- Sem estoque: saldo zero, inclusive produtos sem movimentação.
- Estoque baixo: saldo positivo menor ou igual ao mínimo.
- Estoque normal: saldo acima do mínimo. Mínimo zero não oculta saldo zero.

Os indicadores são recalculados ao abrir ou atualizar a página; não há atualização
automática em segundo plano. Transferências conservam o saldo total do produto.

Na prévia temporária descrita acima, o Produto inicial começa sem estoque.
Edite seu mínimo para 5. Registre entrada de 5: ele passa para estoque baixo.
Registre mais 1: passa para normal. Uma saída de 6 volta a exibi-lo sem estoque.
Confira o dashboard e os alertas após cada operação. Nenhuma dessas verificações
deve ser feita no banco real.

## Relatórios

Abra **Relatórios** no menu como administrador ou operador. Escolha movimentações,
estoque atual ou alertas e clique **Consultar**. Produto e categoria valem para os
três relatórios. Movimentações aceita período inclusivo em UTC, tipo e setor de
origem ou destino. Estoque aceita setor e mostra o saldo atual, inclusive de inativos.
Alertas soma todos os setores de produtos ativos; não aceita setor ou período.
Limpe os filtros incompatíveis ao trocar de relatório; a página mostra os erros.

**Exportar CSV** baixa o resultado dos mesmos filtros, consultado novamente no
momento do download. Formato UTF-8 com BOM e ponto e vírgula, adequado para abrir
em planilhas. Os campos textuais com prefixo de fórmula recebem apóstrofo de proteção.
Nomes e categorias são os cadastros atuais. Não há relatório financeiro, saldo
histórico em determinada data, PDF ou paginação nesta etapa.

Testes do módulo: `.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_relatorios.py`.
Roteiro de validação: `docs/plano-relatorios.md`.

O banco definitivo desta instalação é `instance/instok.db`. Configure DATABASE_PATH nessa localização ao iniciar cada terminal. O login aceita até 15 envios por minuto por endereço de conexão e processo Flask. Instalações com vários processos precisam coordenar o limite na infraestrutura.
