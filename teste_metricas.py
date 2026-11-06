from docker_manager import DockerManager

def main():

    docker_manager = DockerManager()

    try:

        containers = docker_manager.listar_containers()

        print("\n========== MONITORAMENTO ==========\n")

        for container in containers:

            if container["status"] != "running":
                continue

            nome = container["nome"]

            metricas = docker_manager.coletar_metricas(nome)

            if metricas:

                print(f"Container: {metricas['nome']}")
                print(f"CPU: {metricas['cpu_percent']}%")

                print(
                    f"RAM: {metricas['memory_mb']} MB "
                    f"({metricas['memory_percent']}%)"
                )

                print(
                    f"Rede recebida: "
                    f"{metricas['network_received_mb']} MB"
                )

                print(
                    f"Rede enviada: "
                    f"{metricas['network_sent_mb']} MB"
                )

                print("-" * 45)

    finally:
        docker_manager.fechar_conexao()


if __name__ == "__main__":
    main()
