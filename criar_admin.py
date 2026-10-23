from getpass import getpass

from app.services.usuario_service import cadastrar_usuario


def criar_admin():
    print("=== CRIAR ADMINISTRADOR ===")

    nome = input("Nome: ").strip()
    usuario = input("Usuario: ").strip()
    email = input("E-mail: ").strip()

    # getpass evita mostrar a senha enquanto ela e digitada.
    senha = getpass("Senha: ")

    try:
        usuario_id = cadastrar_usuario(
            nome=nome,
            usuario=usuario,
            email=email,
            senha=senha,
            nivel_acesso="ADMINISTRADOR",
        )

        print()
        print("Administrador criado com sucesso!")
        print(f"ID: {usuario_id}")

    except ValueError as erro:
        print(f"Erro: {erro}")

    except Exception as erro:
        print(f"Erro inesperado: {erro}")


if __name__ == "__main__":
    criar_admin()