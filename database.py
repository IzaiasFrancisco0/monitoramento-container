
import sqlite3

from pathlib import Path
from datetime import datetime


PASTA = Path(__file__).resolve().parent
PASTA_DADOS = PASTA / "data"

PASTA_DADOS.mkdir(exist_ok=True)

DB_PATH = PASTA_DADOS / "docker_monitor.db"


class Database:

    def __init__(self):
        """
        Inicializa a conexão com SQLite.
        """

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.row_factory = sqlite3.Row

        self.criar_tabela()

    def criar_tabela(self):
        """
        Cria a tabela de histórico de métricas.
        """

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS metricas_containers (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp TEXT NOT NULL,

                container_name TEXT NOT NULL,

                cpu_percent REAL,

                memory_mb REAL,

                memory_percent REAL,

                network_received_mb REAL,

                network_sent_mb REAL

            )
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_container_timestamp
            ON metricas_containers (
                container_name,
                timestamp
            )
        """)

        self.conn.commit()

        print("[INFO] Tabela de métricas preparada.")

    def inserir_metrica(self, metricas):
        """
        Insere uma medição no banco de dados.
        """

        timestamp = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

        try:

            self.conn.execute("""
                INSERT INTO metricas_containers (

                    timestamp,
                    container_name,
                    cpu_percent,
                    memory_mb,
                    memory_percent,
                    network_received_mb,
                    network_sent_mb

                )

                VALUES (?, ?, ?, ?, ?, ?, ?)

            """, (

                timestamp,
                metricas["nome"],
                metricas["cpu_percent"],
                metricas["memory_mb"],
                metricas["memory_percent"],
                metricas["network_received_mb"],
                metricas["network_sent_mb"]

            ))

            self.conn.commit()

            print(
                f"[INFO] Métrica registrada: {metricas['nome']}"
            )

        except sqlite3.Error as erro:

            self.conn.rollback()

            print(f"[ERRO] Falha ao salvar métrica: {erro}")

    def consultar_historico(self, container_name=None, limite=100):
        """
        Consulta o histórico de métricas.

        Permite filtrar por container e limitar resultados.
        """

        try:

            if container_name:

                cursor = self.conn.execute("""
                    SELECT *
                    FROM metricas_containers
                    WHERE container_name = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (container_name, limite))

            else:

                cursor = self.conn.execute("""
                    SELECT *
                    FROM metricas_containers
                    ORDER BY id DESC
                    LIMIT ?
                """, (limite,))

            return [
                dict(registro)
                for registro in cursor.fetchall()
            ]

        except sqlite3.Error as erro:

            print(f"[ERRO] Falha ao consultar histórico: {erro}")

            return []

    def fechar_conexao(self):
        """
        Fecha a conexão com SQLite.
        """

        self.conn.close()

        print("[INFO] Conexão SQLite encerrada.")
