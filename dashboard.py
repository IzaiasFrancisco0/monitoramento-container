
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import plotly.express as px


# ==========================================
# CONFIGURAÇÕES
# ==========================================

PASTA = Path(__file__).resolve().parent
DB_PATH = PASTA / "data" / "docker_monitor.db"

st.set_page_config(
    page_title="Docker Monitor",
    page_icon="🐳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# ESTILO VISUAL
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

[data-testid="stMetric"] {
    background-color: #1c2330;
    border: 1px solid #303b4b;
    padding: 20px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #aab6c5;
}

[data-testid="stMetricValue"] {
    color: #60a5fa;
}

section[data-testid="stSidebar"] {
    background-color: #151b26;
    border-right: 1px solid #303b4b;
}

h1, h2, h3 {
    color: #f1f5f9;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #303b4b;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# CONSULTAS SQLITE
# ==========================================

def consultar_historico():

    with sqlite3.connect(DB_PATH) as conn:

        df = pd.read_sql_query("""
            SELECT
                timestamp,
                container_name,
                cpu_percent,
                memory_mb,
                memory_percent,
                network_received_mb,
                network_sent_mb
            FROM metricas_containers
            ORDER BY id ASC
        """, conn)

    if not df.empty:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            utc=True
        ).dt.tz_convert("America/Sao_Paulo")

    return df


def consultar_ultimas_metricas():

    with sqlite3.connect(DB_PATH) as conn:

        df = pd.read_sql_query("""
            SELECT *
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY container_name
                        ORDER BY id DESC
                    ) AS posicao
                FROM metricas_containers
            )
            WHERE posicao = 1
            ORDER BY container_name
        """, conn)

    if not df.empty:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            utc=True
        ).dt.tz_convert("America/Sao_Paulo")

    return df

def consultar_alertas():

    with sqlite3.connect(DB_PATH) as conn:

        df = pd.read_sql_query("""
            SELECT
                id,
                container_name,
                tipo,
                nivel,
                mensagem,
                status,
                iniciado_em,
                resolvido_em
            FROM alertas
            ORDER BY id DESC
            LIMIT 100
        """, conn)

    return df



# ==========================================
# DASHBOARD
# ==========================================

@st.fragment(run_every="30s")
def exibir_dashboard():

    historico = consultar_historico()
    ultimas = consultar_ultimas_metricas()

    # ======================================
    # CABEÇALHO
    # ======================================

    st.title("🐳 Docker Monitor")

    st.caption(
        "PAINEL DE INFRAESTRUTURA  /  MONITORAMENTO DOCKER"
    )

    if historico.empty:

        st.warning("Nenhuma métrica encontrada no banco.")

        return

    if ultimas.empty:

        st.warning("Nenhum container encontrado.")

        return

    # ======================================
    # FILTROS
    # ======================================

    st.sidebar.title("⚙️ Configurações")

    st.sidebar.caption("FILTROS DO MONITORAMENTO")

    containers = ["Todos"] + sorted(
        ultimas["container_name"].unique().tolist()
    )

    container_selecionado = st.sidebar.selectbox(
        "Container",
        containers
    )

    periodo = st.sidebar.selectbox(
        "Período histórico",
        [
            "Última hora",
            "Últimas 6 horas",
            "Últimas 24 horas",
            "Últimos 7 dias",
            "Todo histórico"
        ]
    )

    periodos = {
        "Última hora": timedelta(hours=1),
        "Últimas 6 horas": timedelta(hours=6),
        "Últimas 24 horas": timedelta(hours=24),
        "Últimos 7 dias": timedelta(days=7)
    }

    # Cópias para não alterar os dados originais

    dados = historico.copy()
    dados_atuais = ultimas.copy()

    if periodo != "Todo histórico":

        limite = (
            datetime.now().astimezone()
            - periodos[periodo]
        )

        dados = dados[
            dados["timestamp"] >= limite
        ]

    if container_selecionado != "Todos":

        dados = dados[
            dados["container_name"]
            == container_selecionado
        ]

        dados_atuais = dados_atuais[
            dados_atuais["container_name"]
            == container_selecionado
        ]

    st.sidebar.divider()

    st.sidebar.markdown(
        "**Status do painel**"
    )

    st.sidebar.success("Banco SQLite conectado")

    st.sidebar.caption(
        "Atualização automática: 30 segundos"
    )

    # ======================================
    # INDICADORES
    # ======================================

    total = len(dados_atuais)

    cpu_media = dados_atuais["cpu_percent"].mean()

    ram_total = dados_atuais["memory_mb"].sum()

    ram_media = dados_atuais["memory_percent"].mean()

    st.subheader("Visão geral")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🐳 Containers monitorados",
        total
    )

    col2.metric(
        "⚡ CPU média",
        f"{cpu_media:.2f}%"
    )

    col3.metric(
        "🧠 RAM utilizada",
        f"{ram_total:.2f} MB"
    )

    col4.metric(
        "📊 RAM média",
        f"{ram_media:.2f}%"
    )

    st.divider()

    # ======================================
    # ABAS
    # ======================================

    aba_visao, aba_containers, aba_historico, aba_alertas = st.tabs([
        "📊 Visão geral",
        "🐳 Containers",
        "📅 Histórico",
        "🚨 Alertas"
    ])

    # ======================================
    # ABA VISÃO GERAL
    # ======================================

    with aba_visao:

        st.subheader("Consumo de recursos")

        if dados.empty:

            st.info(
                "Não existem medições para o período selecionado."
            )

        else:

            col1, col2 = st.columns(2)

            with col1:

                grafico_cpu = px.line(
                    dados,
                    x="timestamp",
                    y="cpu_percent",
                    color="container_name",
                    markers=True,
                    template="plotly_dark",
                    title="Utilização de CPU",
                    labels={
                        "timestamp": "Horário",
                        "cpu_percent": "CPU (%)",
                        "container_name": "Container"
                    }
                )

                grafico_cpu.update_layout(
                    hovermode="x unified",
                    legend_title_text="Containers"
                )

                st.plotly_chart(
                    grafico_cpu,
                    use_container_width=True
                )

            with col2:

                grafico_ram = px.line(
                    dados,
                    x="timestamp",
                    y="memory_mb",
                    color="container_name",
                    markers=True,
                    template="plotly_dark",
                    title="Utilização de memória RAM",
                    labels={
                        "timestamp": "Horário",
                        "memory_mb": "RAM (MB)",
                        "container_name": "Container"
                    }
                )

                grafico_ram.update_layout(
                    hovermode="x unified",
                    legend_title_text="Containers"
                )

                st.plotly_chart(
                    grafico_ram,
                    use_container_width=True
                )

            st.subheader("Tráfego de rede acumulado")

            grafico_rede = px.line(
                dados,
                x="timestamp",
                y=[
                    "network_received_mb",
                    "network_sent_mb"
                ],
                color="container_name",
                template="plotly_dark",
                labels={
                    "timestamp": "Horário",
                    "value": "Tráfego (MB)",
                    "variable": "Tipo",
                    "container_name": "Container"
                }
            )

            st.plotly_chart(
                grafico_rede,
                use_container_width=True
            )

    # ======================================
    # ABA CONTAINERS
    # ======================================

    with aba_containers:

        st.subheader("Detalhamento dos containers")

        tabela = dados_atuais[
            [
                "container_name",
                "cpu_percent",
                "memory_mb",
                "memory_percent",
                "network_received_mb",
                "network_sent_mb"
            ]
        ].copy()

        tabela.columns = [
            "Container",
            "CPU (%)",
            "RAM (MB)",
            "RAM (%)",
            "Rede recebida (MB)",
            "Rede enviada (MB)"
        ]

        st.dataframe(
            tabela,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Os valores de rede são acumulados desde o início "
            "do container."
        )

    # ======================================
    # ABA HISTÓRICO
    # ======================================

    with aba_historico:

        st.subheader("Histórico de medições")

        st.write(
            f"Registros encontrados: {len(dados)}"
        )

        historico_tabela = dados.sort_values(
            "timestamp",
            ascending=False
        )

        st.dataframe(
            historico_tabela,
            use_container_width=True,
            hide_index=True
        )

        csv = historico_tabela.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="📥 Exportar histórico CSV",
            data=csv,
            file_name="docker_monitor_historico.csv",
            mime="text/csv"
        )


    # ======================================
    # ABA ALERTAS
    # ======================================

    with aba_alertas:

        st.subheader("🚨 Central de alertas")

        alertas_df = consultar_alertas()

        if alertas_df.empty:

            st.success("Nenhum alerta registrado.")

        else:

            ativos = alertas_df[
                alertas_df["status"] == "ATIVO"
            ]

            criticos = ativos[
                ativos["nivel"] == "CRITICO"
            ]

            atencao = ativos[
                ativos["nivel"] == "ATENCAO"
            ]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Alertas ativos",
                len(ativos)
            )

            col2.metric(
                "Críticos",
                len(criticos)
            )

            col3.metric(
                "Atenção",
                len(atencao)
            )

            st.divider()

            st.markdown("### Alertas em andamento")

            if ativos.empty:

                st.success("Todos os alertas estão resolvidos.")

            else:

                for _, alerta in ativos.iterrows():

                    if alerta["nivel"] == "CRITICO":

                        st.error(
                            f"🔴 {alerta['container_name']} | "
                            f"{alerta['tipo']} | "
                            f"{alerta['mensagem']}"
                        )

                    else:

                        st.warning(
                            f"🟡 {alerta['container_name']} | "
                            f"{alerta['tipo']} | "
                            f"{alerta['mensagem']}"
                        )

                    st.caption(
                        f"Iniciado em: {alerta['iniciado_em']}"
                    )

            st.divider()

            st.markdown("### Histórico de alertas")

            tabela_alertas = alertas_df.copy()

            tabela_alertas.columns = [
                "ID",
                "Container",
                "Tipo",
                "Nível",
                "Mensagem",
                "Status",
                "Iniciado em",
                "Resolvido em"
            ]

            st.dataframe(
                tabela_alertas,
                use_container_width=True,
                hide_index=True
            )


    # ======================================
    # RODAPÉ
    # ======================================

    st.divider()

    st.caption(
        "Docker Monitor | Python + Docker SDK + SQLite + Streamlit"
    )

    st.caption(
        "Última atualização: "
        + datetime.now().astimezone().strftime(
            "%d/%m/%Y às %H:%M:%S"
        )
    )


# ==========================================
# EXECUÇÃO
# ==========================================

if not DB_PATH.exists():

    st.error("Banco de dados não encontrado.")

else:

    exibir_dashboard()
