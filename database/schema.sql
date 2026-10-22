-- ============================================================
-- BANCO DE DADOS - SISTEMA DE CONTROLE DE ESTOQUE
-- SQLite
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- USUARIOS
-- ============================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome TEXT NOT NULL,

    usuario TEXT NOT NULL UNIQUE,

    email TEXT NOT NULL UNIQUE,

    senha_hash TEXT NOT NULL,

    nivel_acesso TEXT NOT NULL
        CHECK (nivel_acesso IN ('ADMINISTRADOR', 'OPERADOR')),

    status TEXT NOT NULL DEFAULT 'ATIVO'
        CHECK (status IN ('ATIVO', 'INATIVO')),

    data_cadastro TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ============================================================
-- CATEGORIAS
-- ============================================================

CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome TEXT NOT NULL UNIQUE,

    descricao TEXT,

    status TEXT NOT NULL DEFAULT 'ATIVO'
        CHECK (status IN ('ATIVO', 'INATIVO')),

    data_cadastro TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ============================================================
-- PRODUTOS
-- ============================================================

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    codigo TEXT NOT NULL UNIQUE,

    nome TEXT NOT NULL,

    descricao TEXT,

    categoria_id INTEGER NOT NULL,

    estoque_minimo INTEGER NOT NULL DEFAULT 0
        CHECK (estoque_minimo >= 0),

    status TEXT NOT NULL DEFAULT 'ATIVO'
        CHECK (status IN ('ATIVO', 'INATIVO')),

    data_cadastro TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (categoria_id)
        REFERENCES categorias(id)
);


-- ============================================================
-- SETORES
-- ============================================================

CREATE TABLE IF NOT EXISTS setores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome TEXT NOT NULL UNIQUE,

    descricao TEXT,

    status TEXT NOT NULL DEFAULT 'ATIVO'
        CHECK (status IN ('ATIVO', 'INATIVO')),

    data_cadastro TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ============================================================
-- ESTOQUES
-- Quantidade de cada produto em cada setor
-- ============================================================

CREATE TABLE IF NOT EXISTS estoques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    produto_id INTEGER NOT NULL,

    setor_id INTEGER NOT NULL,

    quantidade INTEGER NOT NULL DEFAULT 0
        CHECK (quantidade >= 0),

    UNIQUE (produto_id, setor_id),

    FOREIGN KEY (produto_id)
        REFERENCES produtos(id),

    FOREIGN KEY (setor_id)
        REFERENCES setores(id)
);


-- ============================================================
-- MOVIMENTACOES
-- ============================================================

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    produto_id INTEGER NOT NULL,

    usuario_id INTEGER NOT NULL,

    tipo TEXT NOT NULL
        CHECK (tipo IN ('ENTRADA', 'SAIDA', 'TRANSFERENCIA')),

    quantidade INTEGER NOT NULL
        CHECK (quantidade > 0),

    setor_origem_id INTEGER,

    setor_destino_id INTEGER,

    observacao TEXT,

    data_hora TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (produto_id)
        REFERENCES produtos(id),

    FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id),

    FOREIGN KEY (setor_origem_id)
        REFERENCES setores(id),

    FOREIGN KEY (setor_destino_id)
        REFERENCES setores(id),

    CHECK (
        setor_origem_id IS NULL
        OR setor_destino_id IS NULL
        OR setor_origem_id <> setor_destino_id
    )
);


-- ============================================================
-- INDICES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_produtos_nome
ON produtos(nome);

CREATE INDEX IF NOT EXISTS idx_produtos_categoria
ON produtos(categoria_id);

CREATE INDEX IF NOT EXISTS idx_estoques_produto
ON estoques(produto_id);

CREATE INDEX IF NOT EXISTS idx_estoques_setor
ON estoques(setor_id);

CREATE INDEX IF NOT EXISTS idx_movimentacoes_produto
ON movimentacoes(produto_id);

CREATE INDEX IF NOT EXISTS idx_movimentacoes_usuario
ON movimentacoes(usuario_id);

CREATE INDEX IF NOT EXISTS idx_movimentacoes_data
ON movimentacoes(data_hora);