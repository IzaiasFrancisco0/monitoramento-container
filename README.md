# 🐳 Docker Monitor

**Sistema de monitoramento de containers Docker desenvolvido em Python.**

O Docker Monitor é um projeto de monitoramento de infraestrutura que permite acompanhar o consumo de recursos dos containers Docker, armazenar métricas em banco de dados, identificar situações críticas e enviar notificações automáticas por e-mail.

O projeto foi desenvolvido com foco em administração de sistemas, monitoramento de infraestrutura, automação e análise de desempenho.

## 🚀 Funcionalidades

- **Monitoramento de containers:** identificação e acompanhamento dos containers Docker em execução.
- **Monitoramento de CPU:** coleta do percentual de utilização do processador.
- **Monitoramento de memória RAM:** acompanhamento do consumo de memória dos containers.
- **Monitoramento de rede:** coleta de dados de tráfego recebido e enviado.
- **Banco de dados SQLite:** armazenamento histórico das métricas coletadas.
- **Sistema de alertas:** identificação de consumo elevado ou crítico de CPU e RAM.
- **Notificações por e-mail:** envio automático de alertas e notificações de recuperação utilizando SMTP do Gmail.
- **Dashboard interativo:** visualização de métricas, containers monitorados e histórico de alertas.
- **Exportação de dados:** possibilidade de exportar informações para análise.

## 🛠️ Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Linguagem principal |
| Docker SDK | Comunicação com a API do Docker |
| SQLite | Armazenamento das informações |
| Streamlit | Desenvolvimento do dashboard |
| Pandas | Manipulação de dados |
| Plotly | Visualização de métricas e gráficos |
| SMTP | Envio de notificações por e-mail |
| Python-dotenv | Gerenciamento de variáveis de ambiente |
| Linux Ubuntu | Ambiente de execução |

## 📂 Estrutura do projeto

```text
docker-monitor/
│
├── config/
│   └── settings.py
│
├── data/
│   └── docker_monitor.db
│
├── app.py
├── docker_manager.py
├── monitor.py
├── database.py
├── alerts.py
├── email_notifier.py
├── dashboard.py
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

*Estrutura de referência do projeto; alguns arquivos e diretórios ainda podem estar em desenvolvimento.*

## ⚙️ Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/IzaiasFrancisco0/monitoramento-container.git
```

### 2. Acessar a pasta

```bash
cd docker-monitor
```

### 3. Criar ambiente virtual

```bash
python3 -m venv venv
```

### 4. Ativar o ambiente virtual

Linux:

```bash
source venv/bin/activate
```

Windows:

```powershell
venv\Scripts\activate
```

### 5. Instalar dependências

```bash
pip install -r requirements.txt
```

### 6. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=seuemail@gmail.com
SMTP_PASSWORD=sua_senha_de_app

EMAIL_DESTINO=destino@gmail.com
```

Para utilizar o envio de e-mails pelo Gmail, é necessário configurar uma senha de app na Conta Google.

**Importante:** nunca publique o arquivo `.env` ou suas credenciais no GitHub.

## ▶️ Executando o projeto

O Docker precisa estar instalado e em execução, e o usuário deve possuir permissão para acessar o serviço.

### Iniciar o monitoramento

Em um terminal:

```bash
python monitor.py
```

O monitor coleta as métricas dos containers em intervalos de 30 segundos.

### Iniciar o dashboard

Em outro terminal:

```bash
python -m streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501
```

Acesse pelo navegador:

```text
http://IP_DO_SERVIDOR:8501
```

## 🚨 Sistema de alertas

O sistema possui limites configuráveis para identificar situações de consumo elevado de recursos.

| Recurso | Atenção | Crítico |
|---|---:|---:|
| CPU | Acima de 80% | Acima de 95% |
| RAM | Acima de 80% | Acima de 95% |

Quando uma condição é identificada, o sistema registra o evento no banco de dados e pode enviar uma notificação por e-mail.

Os alertas também são atualizados ou encerrados quando as condições voltam ao normal.

## 📧 Notificações por e-mail

O projeto utiliza SMTP do Gmail para enviar notificações automáticas.

Os eventos notificados incluem:

- Novos alertas.
- Alterações de severidade.
- Recuperação de recursos.
- Encerramento de alertas associados a containers parados.

## 📊 Dashboard

O dashboard foi desenvolvido com Streamlit e Plotly para facilitar a visualização das informações coletadas.

Entre os dados apresentados estão:

- Quantidade de containers monitorados.
- Consumo de CPU e memória.
- Tráfego de rede.
- Histórico de métricas.
- Alertas ativos e resolvidos.
- Histórico de ocorrências.

## 🔮 Melhorias futuras

- Monitoramento de uptime e downtime.
- Visualização de logs dos containers.
- Integração com Docker Compose.
- Melhorias na gestão de configurações.
- Novos indicadores de desempenho.
- Aprimoramento da interface do dashboard.

