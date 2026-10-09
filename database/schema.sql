-- =====================================================================
-- schema.sql
--
-- Responsabilidade:
-- Estrutura conceitual do banco de dados do Sistema de Controle de Estoque.
--
-- Preparado inicialmente para SQLite, mas escrito de forma simples e
-- padronizada (tipos e sintaxe basica) para facilitar uma futura
-- migracao para MySQL.
--
-- Relacionamentos planejados:
--   categorias   1:N  produtos
--   produtos     1:N  estoques
--   setores      1:N  estoques
--   usuarios     1:N  movimentacoes
--   produtos     1:N  movimentacoes
--   setores podem ser origem e destino de movimentacoes (transferencias)
--
-- Regra de classificacao do estoque (aplicada futuramente na camada de
-- servico, nao via trigger neste momento):
--   quantidade = 0                -> SEM ESTOQUE
--   quantidade <= estoque_minimo  -> ESTOQUE BAIXO
--   quantidade > estoque_minimo   -> ESTOQUE NORMAL
--
-- Nesta etapa do projeto NAO sao criadas triggers ou automacoes complexas.
-- =====================================================================


-- Usuarios do sistema (responsaveis por realizar movimentacoes)
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,      -- nunca armazenar senha em texto puro
    criado_em TEXT DEFAULT (datetime('now'))
);


-- Categorias de produtos
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT
);


-- Produtos cadastrados no sistema
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    categoria_id INTEGER NOT NULL,
    estoque_minimo INTEGER NOT NULL DEFAULT 0,
    criado_em TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
);


-- Setores/localizacoes onde o estoque fica armazenado
CREATE TABLE IF NOT EXISTS setores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT
);


-- Quantidade de cada produto por setor
CREATE TABLE IF NOT EXISTS estoques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    setor_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 0,
    atualizado_em TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (produto_id) REFERENCES produtos (id),
    FOREIGN KEY (setor_id) REFERENCES setores (id)
);


-- Historico de movimentacoes de estoque (entrada, saida, transferencia)
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,            -- 'ENTRADA', 'SAIDA' ou 'TRANSFERENCIA'
    produto_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    setor_origem_id INTEGER,       -- usado em saidas e transferencias
    setor_destino_id INTEGER,      -- usado em entradas e transferencias
    quantidade INTEGER NOT NULL,
    data_movimentacao TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (produto_id) REFERENCES produtos (id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    FOREIGN KEY (setor_origem_id) REFERENCES setores (id),
    FOREIGN KEY (setor_destino_id) REFERENCES setores (id)
);
