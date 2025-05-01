import smtplib
import csv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup # type: ignore
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs, urljoin
import uuid
from src.list_templates import list_templates
from dotenv import load_dotenv # type: ignore
load_dotenv()

SMTP_SERVER_NAME = os.getenv("SMTP_SERVER_NAME")
SMTP_PORT = os.getenv("SMTP_PORT")

SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

APP_DOMAIN = os.getenv("APP_DOMAIN")
PIXEL_DOMAIN = os.getenv("PIXEL_DOMAIN")

def send_emails(html_template_index: int):
    template_names = list_templates()
    if html_template_index < 0 or html_template_index >= len(template_names):
        raise ValueError("Invalid template index")
    html_template_path = template_names[html_template_index]
    # Load the HTML template
    with open(html_template_path, 'r', encoding='utf-8') as f:
        original_html = f.read()

    template_name = os.path.splitext(os.path.basename(html_template_path))[0].split('#')[1]
    print(f"Using template: {template_name}")

    # Get the list of recipients from the CSV file (column "email")
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        recipients = [row['email'] for row in reader]
    
    if not recipients:
        raise ValueError("No recipients found in the CSV file")

    with smtplib.SMTP(SMTP_SERVER_NAME, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        for email in recipients:
            print(f"Sending email to {email}")
            # Modify the HTML for this recipient
            soup = BeautifulSoup(original_html, 'html.parser')

            for a in soup.find_all('a', href=True):
                parsed_url = urlparse(a['href'])
                if APP_DOMAIN in parsed_url.netloc:
                    # Parse existing query, add new UTM params
                    query = parse_qs(parsed_url.query)
                    query.update({
                        'utm_source': email,
                        'utm_medium': 'email',
                        'utm_campaign': 'onboarding',
                        'utm_content': template_name
                    })
                    new_query = urlencode(query, doseq=True)
                    a['href'] = urlunparse(parsed_url._replace(query=new_query))

            # Add a pixel tracker
            pixel_query = urlencode({
                'email': email,
                'title': template_name,
                'uuid': str(uuid.uuid4()), # Prevent caching
            })
            pixel_url = urljoin(f"https://{PIXEL_DOMAIN}/", f"pixel?{pixel_query}")
            print(f"Pixel URL: {pixel_url}")
            img_tag = soup.new_tag('img', src=pixel_url, width="1", height="1")
            soup.body.append(img_tag)

            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = template_name
            msg['From'] = "Adrien Kaczmarek <adrien.kaczmarek@le-studio-k.fr>"
            msg['To'] = email

            msg.attach(MIMEText(str(soup), 'html'))

            # Send email
            server.sendmail(msg['From'], email, msg.as_string())
            print(f"Sent email to {email}")