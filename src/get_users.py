from os import getenv
import boto3
from src.data.user import User
from src.notion import get_database, query_database, extract_args


def get_users() -> tuple[list[User], dict]:
    session = boto3.Session(profile_name="EffectiveBassoonDeveloper")
    dynamodb = session.client("dynamodb")
    paginator = dynamodb.get_paginator("scan")

    scan_iterator = paginator.paginate(
        TableName=getenv("TABLE_NAME"),
        FilterExpression="sk = :metadata",
        ExpressionAttributeValues={":metadata": {"S": "metadata"}},
    )

    users: list[User] = []

    for page in scan_iterator:
        for item in page.get("Items", []):
            email = item.get("google_email", {}).get("S", "")
            remaining = item.get("remaining_credits", {}).get("N", "0")
            users.append(
                User(args={"Email": email, "Remaining credits": int(remaining)})
            )

    # Write to Notion
    database_id = getenv("NOTION_REGISTERED_USERS_DATABASE_ID")
    database = get_database(database_id)
    for user in users:
        # Check if the user already exists in Notion
        existing_users = query_database(
            database["properties"],
            database_id,
            {"Email": user.args["Email"]},
        )
        if len(existing_users) > 0:
            user.page_id = existing_users[0]["id"]
            extracted_args = extract_args(existing_users[0]["properties"])
            if isinstance(extracted_args["Remaining credits"], int):
                user.args["Credits used since last update"] = (
                    extracted_args["Remaining credits"] - user.args["Remaining credits"]
                )
            user.args = {**extract_args(existing_users[0]["properties"]), **user.args}
        else:
            user.args["Last onboarding email"] = 0  # Default value

    return users, database["properties"]
