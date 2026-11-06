
from docker_manager import DockerManager
from database import Database


def main():

    docker_manager = DockerManager()
    banco = Database()

    try:

        print("\n========== COLETA E ARMAZENAMENTO ==========\n")

        containers = docker_manager.listar_containers()

        for container in containers:

            if container["status"] != "running":
                continue

            nome = container["nome"]

            metricas = docker_manager.coletar_metricas(nome)

            if metricas:

                banco.inserir_metrica(metricas)

        print("\n========== HISTÓRICO RECENTE ==========\n")

        historico = banco.consultar_historico(limite=20)

        for registro in historico:

            print(f"Container: {registro['container_name']}")
            print(f"Data: {registro['timestamp']}")
            print(f"CPU: {registro['cpu_percent']}%")
            print(f"RAM: {registro['memory_mb']} MB")

            print("-" * 40)

    finally:

        docker_manager.fechar_conexao()
        banco.fechar_conexao()


if __name__ == "__main__":
    main()
