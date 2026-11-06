
import time

from docker_manager import DockerManager
from database import Database
from alerts import AlertManager
from email_notifier import EmailNotifier


# ==========================================
# CONFIGURAÇÕES
# ==========================================

INTERVALO = 30


# ==========================================
# PROCESSAR EVENTOS E ENVIAR E-MAIL
# ==========================================

def processar_eventos(eventos, email_notifier):

    for evento in eventos:

        print(evento)

        if evento.startswith("[ALERTA"):
            tipo = "Alerta detectado"

        elif evento.startswith("[ALTERAÇÃO]"):
            tipo = "Alerta atualizado"

        elif evento.startswith("[RECUPERAÇÃO]"):
            tipo = "Alerta resolvido"

        elif evento.startswith("[ENCERRAMENTO]"):
            tipo = "Alerta encerrado"

        else:
            continue

        assunto = f"Docker Monitor | {tipo}"

        mensagem = (
            "O Docker Monitor identificou um evento.\n\n"
            f"Detalhes:\n{evento}\n\n"
            "Esta é uma notificação automática do sistema "
            "de monitoramento Docker."
        )

        email_notifier.enviar_email(
            assunto,
            mensagem
        )


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================

def main():

    docker_manager = DockerManager()
    banco = Database()
    alertas = AlertManager()
    email_notifier = EmailNotifier()

    try:

        print("\n====================================")
        print("       DOCKER MONITOR INICIADO")
        print("====================================")

        print(f"Intervalo: {INTERVALO} segundos")
        print("Sistema de alertas ativado.")
        print("Notificações por e-mail ativadas.")
        print("Pressione Ctrl + C para encerrar.\n")

        while True:

            print("\n========== NOVA COLETA ==========\n")

            containers = docker_manager.listar_containers()

            # Verificar containers que pararam ou voltaram.

            eventos = alertas.verificar_status_containers(
                containers
            )

            processar_eventos(
                eventos,
                email_notifier
            )

            total_monitorados = 0

            for container in containers:

                if container["status"] != "running":
                    continue

                nome = container["nome"]

                metricas = docker_manager.coletar_metricas(nome)

                if metricas:

                    # Salvar métricas.

                    banco.inserir_metrica(metricas)

                    # Verificar limites de CPU e RAM.

                    eventos = alertas.verificar_metricas(
                        metricas
                    )

                    processar_eventos(
                        eventos,
                        email_notifier
                    )

                    print(f"Container: {nome}")
                    print(f"CPU: {metricas['cpu_percent']}%")
                    print(f"RAM: {metricas['memory_mb']} MB")
                    print("-" * 40)

                    total_monitorados += 1

            print(
                f"\n[INFO] Containers monitorados: "
                f"{total_monitorados}"
            )

            print(
                f"[INFO] Próxima coleta em {INTERVALO} segundos."
            )

            time.sleep(INTERVALO)

    except KeyboardInterrupt:

        print("\n[INFO] Monitoramento interrompido.")

    finally:

        docker_manager.fechar_conexao()
        banco.fechar_conexao()
        alertas.fechar_conexao()

        print("[INFO] Docker Monitor encerrado.")


if __name__ == "__main__":
    main()
