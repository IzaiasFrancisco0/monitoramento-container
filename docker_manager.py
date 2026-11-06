
import docker
from docker.errors import DockerException, NotFound


class DockerManager:

    def __init__(self):
        """
        Inicializa a conexão com o Docker Engine.
        """
        try:
            self.client = docker.from_env()
            self.client.ping()

            print("[INFO] Conectado ao Docker Engine.")

        except DockerException as erro:
            raise RuntimeError(
                f"Não foi possível conectar ao Docker: {erro}"
            )

    def listar_containers(self):
        """
        Lista todos os containers, incluindo os parados.
        """
        try:
            containers = self.client.containers.list(all=True)

            resultado = []

            for container in containers:
                resultado.append({
                    "nome": container.name,
                    "id": container.short_id,
                    "status": container.status,
                    "imagem": container.image.tags,
                    "criado_em": container.attrs.get("Created")
                })

            return resultado

        except DockerException as erro:
            print(f"[ERRO] Falha ao listar containers: {erro}")
            return []

    def consultar_container(self, identificador):
        """
        Consulta informações detalhadas de um container.
        """
        try:
            container = self.client.containers.get(identificador)
            container.reload()

            detalhes = {
                "nome": container.name,
                "id": container.short_id,
                "status": container.status,
                "imagem": container.image.tags,
                "criado_em": container.attrs.get("Created"),
                "comando": container.attrs.get(
                    "Config", {}
                ).get("Cmd"),
                "portas": container.attrs.get(
                    "NetworkSettings", {}
                ).get("Ports"),
                "reinicializacoes": container.attrs.get(
                    "RestartCount", 0
                )
            }

            return detalhes

        except NotFound:
            print(
                f"[ERRO] Container '{identificador}' não encontrado."
            )
            return None

        except DockerException as erro:
            print(f"[ERRO] Falha ao consultar container: {erro}")
            return None

    def coletar_metricas(self, identificador):
        """
        Coleta métricas de CPU, memória e rede
        de um container em execução.
        """
        try:
            container = self.client.containers.get(identificador)
            container.reload()

            if container.status != "running":
                print(
                    f"[AVISO] Container {identificador} "
                    "não está em execução."
                )
                return None

            stats = container.stats(stream=False)

            # ==================================
            # CPU
            # ==================================

            cpu_stats = stats["cpu_stats"]
            precpu_stats = stats["precpu_stats"]

            cpu_delta = (
                cpu_stats["cpu_usage"]["total_usage"]
                - precpu_stats["cpu_usage"]["total_usage"]
            )

            system_delta = (
                cpu_stats["system_cpu_usage"]
                - precpu_stats["system_cpu_usage"]
            )

            online_cpus = cpu_stats.get("online_cpus")

            if not online_cpus:
                online_cpus = len(
                    cpu_stats["cpu_usage"].get(
                        "percpu_usage", []
                    )
                )

            if (
                cpu_delta > 0
                and system_delta > 0
                and online_cpus > 0
            ):
                cpu_percent = (
                    (cpu_delta / system_delta)
                    * online_cpus
                    * 100
                )
            else:
                cpu_percent = 0.0

            # ==================================
            # MEMÓRIA
            # ==================================

            memory_stats = stats["memory_stats"]

            memory_usage = memory_stats["usage"]
            memory_limit = memory_stats["limit"]

            memory_percent = (
                (memory_usage / memory_limit) * 100
                if memory_limit > 0 else 0.0
            )

            memory_mb = memory_usage / (1024 * 1024)

            # ==================================
            # REDE
            # ==================================

            networks = stats.get("networks") or {}

            bytes_received = sum(
                interface.get("rx_bytes", 0)
                for interface in networks.values()
            )

            bytes_sent = sum(
                interface.get("tx_bytes", 0)
                for interface in networks.values()
            )

            # ==================================
            # RESULTADO
            # ==================================

            return {
                "nome": container.name,
                "cpu_percent": round(cpu_percent, 2),
                "memory_mb": round(memory_mb, 2),
                "memory_percent": round(memory_percent, 2),
                "memory_limit_mb": round(
                    memory_limit / (1024 * 1024), 2
                ),
                "network_received_mb": round(
                    bytes_received / (1024 * 1024), 2
                ),
                "network_sent_mb": round(
                    bytes_sent / (1024 * 1024), 2
                )
            }

        except NotFound:
            print(
                f"[ERRO] Container '{identificador}' não encontrado."
            )
            return None

        except (
            DockerException,
            KeyError,
            TypeError,
            ZeroDivisionError
        ) as erro:
            print(f"[ERRO] Falha ao coletar métricas: {erro}")
            return None

    def fechar_conexao(self):
        """
        Fecha a conexão com o Docker Engine.
        """
        self.client.close()
        print("[INFO] Conexão encerrada.")
