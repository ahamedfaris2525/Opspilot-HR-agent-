import os
import smtplib
from email.message import EmailMessage


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.hr_email = os.getenv("HR_EMAIL")

    def send_email(self, subject: str, body: str):

        message = EmailMessage()

        message["From"] = "opspilot@novatech.local"
        message["To"] = self.hr_email
        message["Subject"] = subject

        message.set_content(body)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()

            server.login(
                self.smtp_username,
                self.smtp_password,
            )

            server.send_message(message)

        return {
            "status": "sent",
            "to": self.hr_email,
            "subject": subject,
        }
