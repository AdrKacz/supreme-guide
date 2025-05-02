import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

NOTION_INTEGRATION_SECRET = os.getenv("NOTION_INTEGRATION_SECRET")

notion = Client(auth=NOTION_INTEGRATION_SECRET)


def extract_args(properties) -> dict:
    args = {}
    for key, value in properties.items():
        print(f"Extracting {key} of type {value['type']}")
        if value["type"] == "title":
            args[key] = value["title"][0]["text"]["content"]
        elif value["type"] == "number":
            args[key] = value["number"]
        elif value["type"] == "date":
            args[key] = value["date"]["start"]
        else:
            print(f"-- Unsupported property type: {value['type']}")
    return args


def get_page(properties, args):
    page = {}
    for key, value in properties.items():
        if key not in args:
            print(f"Missing argument for property: {key}")
            continue
        print(f"Setting {key} = {args[key]}")
        if value["type"] == "title":
            page[key] = {"title": [{"text": {"content": args[key]}}]}
        elif value["type"] == "number":
            page[key] = {"number": args[key]}
        elif value["type"] == "date":
            page[key] = {"date": {"start": args[key]}}
        else:
            print(f"-- Unsupported property type: {value['type']}")

    return page


def get_database(database_id: str):
    return notion.databases.retrieve(database_id)


def create_page(properties, database_id, args):
    notion.pages.create(
        parent={"database_id": database_id}, properties=get_page(properties, args)
    )


def update_page(page_id, properties, args):
    notion.pages.update(page_id=page_id, properties=get_page(properties, args))


def query_database(properties, database_id, args, sort_by=None):
    print(f"Querying database {database_id} with args: {args}")
    and_filter = []
    for key, value in properties.items():
        if key not in args:
            print(f"Missing argument for property: {key}")
            continue
        print(f"Filtering by {key} = {args[key]}")
        if value["type"] == "title" or value["type"] == "rich_text":
            and_filter.append({"property": key, "rich_text": {"equals": args[key]}})
        else:
            print(f"-- Unsupported property type: {value['type']}")
    if sort_by:
        response = notion.databases.query(
            database_id=database_id,
            filter={"and": and_filter},
            sorts=[{"property": sort_by, "direction": "ascending"}],
        )
    else:
        response = notion.databases.query(
            database_id=database_id, filter={"and": and_filter}
        )
    return response.get("results", [])
