import os
from src.notion import (get_database, query_database)
import subprocess
import time
from contextlib import contextmanager
from dotenv import load_dotenv
from pathlib import Path
import httpx
load_dotenv()
NOTION_REGISTERED_ONBOARDING_DATABASE_ID = os.getenv("NOTION_REGISTERED_ONBOARDING_DATABASE_ID")

@contextmanager
def run_server():
    print("Starting server...")
    proc = subprocess.Popen(
        ["npm", "run", "start"],
        cwd=Path(__file__).parent.parent / 'mail',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    try:
        time.sleep(5)  # Wait for the server to start
        yield
    finally:
        proc.terminate()
        proc.wait()
        print("Server stopped.")


def list_templates():
    database = get_database(NOTION_REGISTERED_ONBOARDING_DATABASE_ID)
    pages = query_database(database['properties'], NOTION_REGISTERED_ONBOARDING_DATABASE_ID, {})
    urls = [page['properties']['Template']['url'] for page in pages]
    encoded_configs = [url.split('/')[-1] for url in urls]

    templates = []
    with run_server():
        for cfg in encoded_configs:
            r = httpx.get(f'http://localhost:3000/template/{cfg}')
            r.raise_for_status()
            templates.append(r.text)
    return templates