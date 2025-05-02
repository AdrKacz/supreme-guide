import fire
import os
from src.send_template import send_template
from src.send_email import send_email
from src.get_users import get_users
from src.list_templates import list_templates
from src.notion import create_page, update_page
from dotenv import load_dotenv

load_dotenv()

OWNER_EMAIL = os.getenv("OWNER_EMAIL")
NOTION_REGISTERED_USERS_DATABASE_ID = os.getenv("NOTION_REGISTERED_USERS_DATABASE_ID")


def onboarding():
    """
    Runs the onboarding campaign.
    Send emails to users who should receive them.
    Update the Notion database.
    """
    templates = list_templates()  # List all templates
    users, user_properties = get_users()  # Get the latest users from DynamoDB
    email_sent = {}
    for user in users:
        if (
            user.args["Remaining credits"] == 0
            and user.args["Last onboarding email"] == 0
        ):
            user.args["Last onboarding email"] = (
                1  # Skip the first onboarding as this user already used all their credits
            )
        if user.args["Last onboarding email"] < len(templates):
            # Last onboarding email is 1-indexed and templates are 0-indexed, so to get the next template we do +1 - 1 = +0
            send_template(
                user.args["Email"], templates[user.args["Last onboarding email"]]
            )
            email_sent[user.args["Email"]] = templates[
                user.args["Last onboarding email"]
            ].name
            user.args["Last onboarding email"] += (
                1  # Increment the last onboarding email sent
            )
        if user.page_id:
            print(f"Updating user {user.args['Email']}")
            update_page(user.page_id, user_properties, user.args)
        else:
            print(f"Creating user {user.args['Email']}")
            create_page(user_properties, NOTION_REGISTERED_USERS_DATABASE_ID, user.args)

    print(f"Sending analytics to owner ({OWNER_EMAIL})")
    send_email(
        to=OWNER_EMAIL,
        subject="List of emails sent for onboarding campaign",
        body=f"Sent {len(email_sent)} emails:\n"
        + "\n".join(
            [f"- {email}: {template}" for email, template in email_sent.items()]
        ),
    )


if __name__ == "__main__":
    fire.Fire(
        {
            "onboarding": onboarding,
            "send_template": send_template,
            "get_users": get_users,
            "list_templates": list_templates,
        }
    )
