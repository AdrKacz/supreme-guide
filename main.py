import load_env  # noqa: F401
import fire
from os import getenv
from src.send_template import send_template
from src.send_email import send_email
from src.get_users import get_users
from src.list_templates import list_templates
from src.notion import create_page, update_page
from datetime import datetime, timedelta


def onboarding():
    """
    Runs the onboarding campaign.
    Send emails to users who should receive them.
    Update the Notion database.
    """
    templates = list_templates()  # List all templates
    users, user_properties = get_users()  # Get the latest users from DynamoDB
    email_sent = {}
    now = datetime.now()
    for user in users:
        # if user.args["Email"] != "adrien.kaczmarek@gmail.com":
        #     print(f"Skipping user {user.args['Email']}")
        #     continue
        if (
            user.args["Remaining credits"] == 0
            and user.args["Last onboarding email"] == 0
        ):
            # Skip the first onboarding as this user already used all their credits
            user.args["Last onboarding email"] = 1
            user.args["Next onboarding email"] = now.strftime("%Y-%m-%d")

        all_sent = user.args["Last onboarding email"] >= len(templates)
        # Check now day is on the day or after the next onboarding email date
        is_time_to_send = now.strftime("%Y-%m-%d") >= (
            user.args["Next onboarding email"] or "0000-00-00"
        )
        if not all_sent and is_time_to_send:
            # Last onboarding email is 1-indexed and templates are 0-indexed, so to get the next template we do +1 - 1 = +0
            template = templates[user.args["Last onboarding email"]]
            send_template(user.args["Email"], template)
            next_onboarding_email_date = now + timedelta(days=template.wait)
            user.args["Next onboarding email"] = next_onboarding_email_date.strftime(
                "%Y-%m-%d"
            )

            email_sent[user.args["Email"]] = template.name
            # Increment the last onboarding email sent
            user.args["Last onboarding email"] += 1
        else:
            print(
                f"Skipping {user.args['Email']}, already sent {user.args['Last onboarding email']} emails and next email is scheduled for {user.args['Next onboarding email']}"
            )
        if user.page_id:
            print(f"Updating {user.args['Email']}")
            update_page(user.page_id, user_properties, user.args)
        else:
            print(f"Creating {user.args['Email']}")
            create_page(
                user_properties,
                getenv("NOTION_REGISTERED_USERS_DATABASE_ID"),
                user.args,
            )

    print(f"Sending analytics to owner ({getenv('OWNER_EMAIL')})")
    send_email(
        to=getenv("OWNER_EMAIL"),
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
            "send_email": send_email,
        }
    )
