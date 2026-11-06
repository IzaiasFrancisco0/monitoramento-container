import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv


# Carrega as configurações do arquivo .env
PASTA_PROJETO = Path(__file__).resolve().parent
load_dotenv(PASTA_PROJETO / ".env")


class EmailNotifier:

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_email = os.getenv("SMTP_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.email_destino = os.getenv("EMAIL_DESTINO")

        configuracoes = [
            self.smtp_host,
            self.smtp_email,
            self.smtp_password,
            self.email_destino
        ]

        if not all(configuracoes):
            raise ValueError(
                "Configurações de e-mail ausentes no arquivo .env"
            )

    def enviar_email(self, assunto, mensagem):

        email = EmailMessage()
        email["Subject"] = assunto
        email["From"] = self.smtp_email
        email["To"] = self.email_destino
        email.set_content(mensagem)

        try:
            with smtplib.SMTP(
                self.smtp_host,
                self.smtp_port,
                timeout=20
            ) as servidor:

                servidor.ehlo()
                servidor.starttls()
                servidor.ehlo()

                servidor.login(
                    self.smtp_email,
                    self.smtp_password
                )

                servidor.send_message(email)

            print("[EMAIL] Notificação enviada com sucesso!")
            return True

        except (smtplib.SMTPException, OSError) as erro:
            print(f"[EMAIL] Erro ao enviar notificação: {erro}")
            return False


if __name__ == "__main__":

    notifier = EmailNotifier()

    resultado = notifier.enviar_email(
        assunto="Teste - Docker Monitor",
        mensagem=(
            "Olá!\n\n"
            "Este é um teste de envio de e-mail do projeto "
            "Docker Monitor.\n\n"
            "Se você recebeu esta mensagem, a integração "
            "com o Gmail está funcionando corretamente.\n"
        )
    )

    if resultado:
        print("Teste concluído.")
    else:
        print("Não foi possível enviar o e-mail.")
