import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()


SMTP_SERVER_NAME = os.getenv("SMTP_SERVER_NAME")
SMTP_PORT = os.getenv("SMTP_PORT")

SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_email(to: str, subject: str, body: str) -> None:
    print(f"Sending email to {to}")
    with smtplib.SMTP(SMTP_SERVER_NAME, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = "Adrien Kaczmarek <adrien.kaczmarek@le-studio-k.fr>"
        msg["To"] = to
        server.sendmail(SMTP_USERNAME, to, msg.as_string())
        print(f"-- Sent email to {to}")
