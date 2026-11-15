# Dashboard e alertas — InStok

Etapa autorizada em 09/11/2026. Preservar alterações locais e não fazer commit/push.

Decisão: manter Flask/Jinja2 e consultar o inventário existente em uma única leitura.
Somar em Python para evitar overflow do INTEGER do SQLite. Apenas produtos ativos,
inclusive associados a categorias inativas. Mínimo global por produto, sem limite
por setor no schema: zero = sem estoque; 0 < saldo <= mínimo = baixo; demais normais.
Alertas exclusivos, calculados a cada GET, sem persistência nem alterações de schema.
Administrador e operador consultam ambas as páginas, protegidas pela sessão existente.

Plano: substituir teste fictício de alertas por testes de limites, soma entre setores,
inativos, overflow, atualização após movimentos, permissões, escape e estado vazio;
implementar alerta_service.obter_resumo; conectar routes/dashboard.py e alertas.py;
substituir templates provisórios; dashboard.css responsivo; atualizar README;
executar regressão completa e verificar interface. Bancos exclusivamente temporários.

Relatórios e motivo obrigatório foram implementados em etapas posteriores. A documentação acadêmica completa continua pendente.


Validação realizada: 81 testes aprovados em 37,955 segundos, bancos temporários.
Testes novos primeiro demonstraram ausência de classificação e páginas reais.
Conferência no navegador: login de administrador, indicadores iniciais (1 produto,
0 unidades, 1 sem estoque, 0 baixo) e listagem de alertas consistente com o painel.
Prévia isolada na porta 5059. Sem commits, push ou alterações no banco real.
