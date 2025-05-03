import smtplib
from os import getenv
from email.mime.text import MIMEText


def send_email(to: str, subject: str, body: str) -> None:
    print(f"Sending <{subject}> to {to}")
    with smtplib.SMTP(getenv("SMTP_SERVER_NAME"), getenv("SMTP_PORT")) as server:
        server.starttls()
        server.login(getenv("SMTP_USERNAME"), getenv("SMTP_PASSWORD"))
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = getenv("MARKETING_EMAIL")
        msg["To"] = to
        server.sendmail(msg["From"], to, msg.as_string())
        print(f"-- Sent email to {to}")
