import os
import csv
import boto3 # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()

TABLE_NAME = os.getenv("TABLE_NAME")
CSV_FILE = os.getenv("CSV_FILE")

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
                'email': email,
                'remaining_credits': int(remaining)
            })

    # Write to CSV
    with open(CSV_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['email', 'remaining_credits'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} users to {CSV_FILE}")