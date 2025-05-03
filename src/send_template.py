import smtplib
from os import getenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs, urljoin
import uuid
from src.data.template import Template

USE_TEMPLATE = True  # Make sure to set this to True in production


def send_template(email: str, template: Template) -> None:
    print(f"Sending <{template.name}> to {email}")
    if not USE_TEMPLATE:
        print(f"Skipping email to {email} because USE_TEMPLATE is set to False")
        return
    with smtplib.SMTP(getenv("SMTP_SERVER_NAME"), getenv("SMTP_PORT")) as server:
        server.starttls()
        server.login(getenv("SMTP_USERNAME"), getenv("SMTP_PASSWORD"))
        # Modify the HTML for this recipient
        soup = BeautifulSoup(template.html, "html.parser")

        for a in soup.find_all("a", href=True):
            parsed_url = urlparse(a["href"])
            if getenv("APP_DOMAIN") in parsed_url.netloc:
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
        pixel_url = urljoin(
            f"https://{getenv('PIXEL_DOMAIN')}/", f"pixel?{pixel_query}"
        )
        print(f"-- Pixel URL: {pixel_url}")
        img_tag = soup.new_tag("img", src=pixel_url, width="1", height="1")
        soup.body.append(img_tag)

        # Create email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = template.name
        msg["From"] = getenv("MARKETING_EMAIL")
        msg["To"] = email

        msg.attach(MIMEText(str(soup), "html"))

        # Send email
        server.sendmail(msg["From"], email, msg.as_string())
        print(f"-- Sent {template.name} to {email}")
