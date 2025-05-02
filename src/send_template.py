import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs, urljoin
import uuid
from src.data.template import Template
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER_NAME = os.getenv("SMTP_SERVER_NAME")
SMTP_PORT = os.getenv("SMTP_PORT")

SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

APP_DOMAIN = os.getenv("APP_DOMAIN")
PIXEL_DOMAIN = os.getenv("PIXEL_DOMAIN")

MARKETING_EMAIL = os.getenv("MARKETING_EMAIL")

USE_TEMPLATE = False  # Make sure to set this to True in production


def send_template(email: str, template: Template) -> None:
    print(f"Sending {template.name} to {email}")
    if not USE_TEMPLATE:
        print(f"Skipping email to {email} because USE_TEMPLATE is set to False")
        return
    with smtplib.SMTP(SMTP_SERVER_NAME, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        # Modify the HTML for this recipient
        soup = BeautifulSoup(template.html, "html.parser")

        for a in soup.find_all("a", href=True):
            parsed_url = urlparse(a["href"])
            if APP_DOMAIN in parsed_url.netloc:
                # Parse existing query, add new UTM params
                query = parse_qs(parsed_url.query)
                query.update(
                    {
                        "utm_source": email,
                        "utm_medium": "email",
                        "utm_campaign": "onboarding",
                        "utm_content": template.name,
                    }
                )
                new_query = urlencode(query, doseq=True)
                a["href"] = urlunparse(parsed_url._replace(query=new_query))

        # Add a pixel tracker
        pixel_query = urlencode(
            {
                "email": email,
                "title": template.name,
                "uuid": str(uuid.uuid4()),  # Prevent caching
            }
        )
        pixel_url = urljoin(f"https://{PIXEL_DOMAIN}/", f"pixel?{pixel_query}")
        print(f"-- Pixel URL: {pixel_url}")
        img_tag = soup.new_tag("img", src=pixel_url, width="1", height="1")
        soup.body.append(img_tag)

        # Create email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = template.name
        msg["From"] = MARKETING_EMAIL
        msg["To"] = email

        msg.attach(MIMEText(str(soup), "html"))

        # Send email
        server.sendmail(msg["From"], email, msg.as_string())
        print(f"-- Sent {template.name} to {email}")
