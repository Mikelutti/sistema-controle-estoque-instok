from pathlib import Path

from app.database.connection import obter_conexao, fechar_conexao


def inicializar_banco():
    caminho_schema = Path("database/schema.sql")

    if not caminho_schema.exists():
        print("ERRO: database/schema.sql nao foi encontrado.")
        return

    conexao = obter_conexao()

    try:
        schema = caminho_schema.read_text(encoding="utf-8")

        conexao.executescript(schema)
        conexao.commit()

        print("Schema executado com sucesso.")

        # Verifica as tabelas existentes no banco
        tabelas = conexao.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name != 'sqlite_sequence'
            ORDER BY name
            """
        ).fetchall()

        print("\nTabelas encontradas:")

        for tabela in tabelas:
            print(f"- {tabela['name']}")

    except Exception as erro:
        conexao.rollback()
        print(f"Erro ao criar banco: {erro}")

    finally:
        fechar_conexao(conexao)


if __name__ == "__main__":
    inicializar_banco()