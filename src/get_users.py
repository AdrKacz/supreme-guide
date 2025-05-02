import os
import boto3
from src.data.user import User
from src.notion import get_database, query_database
from dotenv import load_dotenv
load_dotenv()

TABLE_NAME = os.getenv("TABLE_NAME")
CSV_FILE = os.getenv("CSV_FILE")
NOTION_REGISTERED_USERS_DATABASE_ID = os.getenv("NOTION_REGISTERED_USERS_DATABASE_ID")

def get_users() -> tuple[list[User], dict]:
    session = boto3.Session(profile_name='EffectiveBassoonDeveloper')
    dynamodb = session.client('dynamodb')
    paginator = dynamodb.get_paginator('scan')

    scan_iterator = paginator.paginate(
        TableName=TABLE_NAME,
        FilterExpression='sk = :metadata',
        ExpressionAttributeValues={':metadata': {'S': 'metadata'}}
    )

    users: list[User] = []

    for page in scan_iterator:
        for item in page.get('Items', []):
            email = item.get('google_email', {}).get('S', '')
            remaining = item.get('remaining_credits', {}).get('N', '0')
            users.append(User(args={
                'Email': email,
                'Remaining credits': int(remaining)
            }))


    # Write to Notion
    database = get_database(NOTION_REGISTERED_USERS_DATABASE_ID)
    for user in users:
        # Check if the user already exists in Notion
        existing_users = query_database(database['properties'], NOTION_REGISTERED_USERS_DATABASE_ID, user.args)
        if len(existing_users) > 0:
            user.page_id = existing_users[0]['id']
            user.args = {
                **existing_users[0]['properties'], # TODO: update to get the value only and not the whole object
                **user.args
            }
        else:
            user.args["Last onboarding email"] = 0 # Default value
    
    return users, database['properties']