
import sqlite3

from pathlib import Path
from datetime import datetime


PASTA = Path(__file__).resolve().parent
DB_PATH = PASTA / "data" / "docker_monitor.db"

LIMITE_CPU = 80
LIMITE_CPU_CRITICO = 95

LIMITE_RAM = 80
LIMITE_RAM_CRITICO = 95


class AlertManager:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

        self.criar_tabelas()

    def agora(self):

        return datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

    def criar_tabelas(self):

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS alertas (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                container_name TEXT NOT NULL,

                tipo TEXT NOT NULL,

                nivel TEXT NOT NULL,

                mensagem TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'ATIVO',

                iniciado_em TEXT NOT NULL,

                resolvido_em TEXT

            )
        """)

        self.conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_alerta_ativo
            ON alertas (container_name, tipo)
            WHERE status = 'ATIVO'
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS estado_containers (

                container_name TEXT PRIMARY KEY,

                status TEXT NOT NULL

            )
        """)

        self.conn.commit()

        print("[INFO] Sistema de alertas preparado.")


    def registrar_alerta(
        self,
        container,
        tipo,
        nivel,
        mensagem
    ):

        cursor = self.conn.execute("""
            SELECT id, nivel
            FROM alertas
            WHERE container_name = ?
            AND tipo = ?
            AND status = 'ATIVO'
        """, (container, tipo))

        alerta = cursor.fetchone()

        if alerta:

            if alerta["nivel"] != nivel:

                self.conn.execute("""
                    UPDATE alertas
                    SET nivel = ?,
                        mensagem = ?
                    WHERE id = ?
                """, (
                    nivel,
                    mensagem,
                    alerta["id"]
                ))

                self.conn.commit()

                return (
                    f"[ALTERAÇÃO] {container}: "
                    f"{nivel} - {mensagem}"
                )

            return None

        self.conn.execute("""
            INSERT INTO alertas (
                container_name,
                tipo,
                nivel,
                mensagem,
                status,
                iniciado_em
            )
            VALUES (?, ?, ?, ?, 'ATIVO', ?)
        """, (
            container,
            tipo,
            nivel,
            mensagem,
            self.agora()
        ))

        self.conn.commit()

        return (
            f"[ALERTA {nivel}] {container}: {mensagem}"
        )

    
    def resolver_alerta(self, container, tipo):

        cursor = self.conn.execute("""
            UPDATE alertas
            SET status = 'RESOLVIDO',
                resolvido_em = ?
            WHERE container_name = ?
            AND tipo = ?
            AND status = 'ATIVO'
        """, (
            self.agora(),
            container,
            tipo
        ))

        self.conn.commit()

        if cursor.rowcount > 0:

            return (
                f"[RECUPERAÇÃO] {container}: "
                f"Alerta de {tipo} resolvido."
            )

        return None


    def encerrar_alerta(self, container, tipo):

        mensagem = (
            f"Alerta de {tipo} encerrado porque "
            f"o container {container} parou."
        )

        cursor = self.conn.execute("""
            UPDATE alertas
            SET status = 'RESOLVIDO',
                mensagem = ?,
                resolvido_em = ?
            WHERE container_name = ?
            AND tipo = ?
            AND status = 'ATIVO'
        """, (
            mensagem,
            self.agora(),
            container,
            tipo
        ))

        self.conn.commit()

        if cursor.rowcount > 0:

            return (
                f"[ENCERRAMENTO] {container}: "
                f"{mensagem}"
            )

        return None
 

    def verificar_metricas(self, metricas):

        mensagens = []

        nome = metricas["nome"]

        cpu = float(metricas["cpu_percent"])
        ram = float(metricas["memory_percent"])


        if cpu > LIMITE_CPU_CRITICO:

            resultado = self.registrar_alerta(
                nome,
                "CPU",
                "CRITICO",
                f"Consumo crítico de CPU: {cpu:.2f}%"
            )

        elif cpu > LIMITE_CPU:

            resultado = self.registrar_alerta(
                nome,
                "CPU",
                "ATENCAO",
                f"Consumo elevado de CPU: {cpu:.2f}%"
            )

        else:

            resultado = self.resolver_alerta(
                nome,
                "CPU"
            )

        if resultado:
            mensagens.append(resultado)


        if ram > LIMITE_RAM_CRITICO:

            resultado = self.registrar_alerta(
                nome,
                "RAM",
                "CRITICO",
                f"Consumo crítico de RAM: {ram:.2f}%"
            )

        elif ram > LIMITE_RAM:

            resultado = self.registrar_alerta(
                nome,
                "RAM",
                "ATENCAO",
                f"Consumo elevado de RAM: {ram:.2f}%"
            )

        else:

            resultado = self.resolver_alerta(
                nome,
                "RAM"
            )

        if resultado:
            mensagens.append(resultado)

        return mensagens


    def verificar_status_containers(self, containers):

        mensagens = []

        for container in containers:

            nome = container["nome"]
            status_atual = container["status"]

            cursor = self.conn.execute("""
                SELECT status
                FROM estado_containers
                WHERE container_name = ?
            """, (nome,))

            anterior = cursor.fetchone()

            if anterior is None:

                self.conn.execute("""
                    INSERT INTO estado_containers (
                        container_name,
                        status
                    )
                    VALUES (?, ?)
                """, (nome, status_atual))

                self.conn.commit()

                continue

            status_anterior = anterior["status"]


            if (
                status_anterior == "running"
                and status_atual != "running"
            ):

                resultado = self.registrar_alerta(
                    nome,
                    "CONTAINER",
                    "CRITICO",
                    f"Container deixou de executar. "
                    f"Status atual: {status_atual}"
                )

                if resultado:
                    mensagens.append(resultado)


                for tipo in ["CPU", "RAM"]:

                    resultado = self.encerrar_alerta(
                        nome,
                        tipo
                    )

                    if resultado:
                        mensagens.append(resultado)


            elif (
                status_anterior != "running"
                and status_atual == "running"
            ):

                resultado = self.resolver_alerta(
                    nome,
                    "CONTAINER"
                )

                if resultado:
                    mensagens.append(resultado)



            self.conn.execute("""
                UPDATE estado_containers
                SET status = ?
                WHERE container_name = ?
            """, (status_atual, nome))

            self.conn.commit()

        return mensagens


    def fechar_conexao(self):

        self.conn.close()

        print("[INFO] Conexão do sistema de alertas encerrada.")
