import os
import boto3
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

NOTION_INTEGRATION_SECRET = os.getenv("NOTION_INTEGRATION_SECRET")
NOTION_REGISTERED_USERS_DATABASE_ID = os.getenv("NOTION_REGISTERED_USERS_DATABASE_ID")
TABLE_NAME = os.getenv("TABLE_NAME")
CSV_FILE = os.getenv("CSV_FILE")

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

def create_notion_page(properties, args):
    notion.pages.create(
        parent={"database_id": NOTION_REGISTERED_USERS_DATABASE_ID},
        properties=get_page(properties, args)
    )

def update_notion_page(page_id, properties, args):
    notion.pages.update(
        page_id=page_id,
        properties=get_page(properties, args)
    )

def query_notion_database(properties, args):
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
        database_id=NOTION_REGISTERED_USERS_DATABASE_ID,
        filter={ "and": and_filter}
    )
    return response.get('results', [])

def export_users():
    session = boto3.Session(profile_name='EffectiveBassoonDeveloper')
    dynamodb = session.client('dynamodb')
    paginator = dynamodb.get_paginator('scan')

    scan_iterator = paginator.paginate(
        TableName=TABLE_NAME,
        FilterExpression='sk = :metadata',
        ExpressionAttributeValues={':metadata': {'S': 'metadata'}}
    )

    rows = []

    for page in scan_iterator:
        for item in page.get('Items', []):
            email = item.get('google_email', {}).get('S', '')
            remaining = item.get('remaining_credits', {}).get('N', '0')
            rows.append({
                'Email': email,
                'Remaining credits': int(remaining)
            })


    # Write to Notion
    database = notion.databases.retrieve(NOTION_REGISTERED_USERS_DATABASE_ID)
    for row in rows:
        # Check if the user already exists in Notion
        existing_users = query_notion_database(database['properties'], row)
        if len(existing_users) > 0:
            page_id = existing_users[0]['id']
            update_notion_page(page_id, database['properties'], row)
            print(f"Updated user: {row['Email']}")
        else:
            row["Last onboarding email"] = 0 # Default value
            create_notion_page(database['properties'], row)
            print(f"Created user: {row['Email']}")