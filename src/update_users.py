import os
import boto3
from dotenv import load_dotenv
from src.notion import (
    get_database,
    create_page,
    update_page,
    query_database
)

load_dotenv()

TABLE_NAME = os.getenv("TABLE_NAME")
CSV_FILE = os.getenv("CSV_FILE")
NOTION_REGISTERED_USERS_DATABASE_ID = os.getenv("NOTION_REGISTERED_USERS_DATABASE_ID")

def update_users():
    session = boto3.Session(profile_name='EffectiveBassoonDeveloper')
    dynamodb = session.client('dynamodb')
    paginator = dynamodb.get_paginator('scan')

    scan_iterator = paginator.paginate(
        TableName=TABLE_NAME,
        FilterExpression='sk = :metadata',
        ExpressionAttributeValues={':metadata': {'S': 'metadata'}}
    )

    users = []

    for page in scan_iterator:
        for item in page.get('Items', []):
            email = item.get('google_email', {}).get('S', '')
            remaining = item.get('remaining_credits', {}).get('N', '0')
            users.append({
                'Email': email,
                'Remaining credits': int(remaining)
            })


    # Write to Notion
    database = get_database(NOTION_REGISTERED_USERS_DATABASE_ID)
    for user in users:
        # Check if the user already exists in Notion
        existing_users = query_database(database['properties'], NOTION_REGISTERED_USERS_DATABASE_ID, user)
        if len(existing_users) > 0:
            page_id = existing_users[0]['id']
            update_page(page_id, database['properties'], user)
            print(f"Updated user: {user['Email']}")
        else:
            user["Last onboarding email"] = 0 # Default value
            create_page(database['properties'], NOTION_REGISTERED_USERS_DATABASE_ID, user)
            print(f"Created user: {user['Email']}")
    
    return users