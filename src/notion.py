import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

NOTION_INTEGRATION_SECRET = os.getenv("NOTION_INTEGRATION_SECRET")

notion = Client(auth=NOTION_INTEGRATION_SECRET)

def get_page(properties, args):
    page = {}
    for key, value in properties.items():
        if key not in args:
            print(f"Missing argument for property: {key}")
            continue
        if value['type'] == 'title':
            page[key] = {
                'title': [
                    {
                        'text': {
                            'content': args[key]
                        }
                    }
                ]
            }
        elif value['type'] == 'number':
            page[key] = {
                'number': args[key]
            }
        elif value['type'] == 'date':
            page[key] = {
                'date': {
                    'start': args[key]
                }
            }
        else:
            print(f"Unsupported property type: {value['type']}")

    return page

def get_database(database_id: str):
    return notion.databases.retrieve(database_id)

def create_page(properties, database_id, args):
    notion.pages.create(
        parent={"database_id": database_id},
        properties=get_page(properties, args)
    )

def update_page(page_id, properties, args):
    notion.pages.update(
        page_id=page_id,
        properties=get_page(properties, args)
    )

def query_database(properties, database_id, args):
    and_filter = []
    for key, value in properties.items():
        if key not in args:
            print(f"Missing argument for property: {key}")
            continue
        if value['type'] == 'title' or value['type'] == 'rich_text':
            and_filter.append({
                "property": key,
                "rich_text": {
                    "equals": args[key]
                }
            })
        else:
            print(f"Unsupported property type: {value['type']}")
    response = notion.databases.query(
        database_id=database_id,
        filter={ "and": and_filter}
    )
    return response.get('results', [])