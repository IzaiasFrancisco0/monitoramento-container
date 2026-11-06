from docker_manager import DockerManager


def main():

    docker_manager = DockerManager()

    try:

  

        print("\n========== CONTAINERS ==========\n")

        containers = docker_manager.listar_containers()

        for container in containers:

            print(f"Nome: {container['nome']}")
            print(f"ID: {container['id']}")
            print(f"Status: {container['status']}")
            print(f"Imagem: {container['imagem']}")
            print("-" * 40)


        if containers:

            nome = containers[0]["nome"]

            print("\n========== DETALHES ==========\n")

            detalhes = docker_manager.consultar_container(nome)

            if detalhes:

                for chave, valor in detalhes.items():
                    print(f"{chave}: {valor}")

    finally:
        docker_manager.fechar_conexao()


if __name__ == "__main__":
    main()
