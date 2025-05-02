import os
from src.notion import get_database, query_database
import subprocess
import time
from contextlib import contextmanager
from dotenv import load_dotenv
from pathlib import Path
import httpx
from src.data.template import Template

load_dotenv()
NOTION_REGISTERED_ONBOARDING_DATABASE_ID = os.getenv(
    "NOTION_REGISTERED_ONBOARDING_DATABASE_ID"
)


@contextmanager
def run_server():
    print("Starting server...")
    proc = subprocess.Popen(
        ["npm", "run", "start"],
        cwd=Path(__file__).parent.parent / "mail",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        time.sleep(5)  # Wait for the server to start
        yield
    finally:
        proc.terminate()
        proc.wait()
        print("Server stopped.")


def list_templates() -> list[Template]:
    database = get_database(NOTION_REGISTERED_ONBOARDING_DATABASE_ID)
    pages = query_database(
        database["properties"], NOTION_REGISTERED_ONBOARDING_DATABASE_ID, {}, "Order"
    )
    templates: list[Template] = []
    for page in pages:
        name = page["properties"]["Name"]["title"][0]["text"]["content"]
        wait = page["properties"]["Wait (days)"]["number"]
        url = page["properties"]["Template"]["url"]
        encoded_config = url.split("/")[-1]
        templates.append(Template(name=name, wait=wait, encoded_config=encoded_config))

    with run_server():
        for template in templates:
            r = httpx.get(f"http://localhost:3000/template/{template.encoded_config}")
            r.raise_for_status()
            template.html = r.text
    return templates
