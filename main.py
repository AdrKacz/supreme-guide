import fire
from src.send_email import send_email
from src.update_users import update_users
from src.list_templates import list_templates


def onboarding():
    """
    Runs the onboarding campaign.
    Send emails to users who should receive them.
    Update the Notion database.
    """
    templates = list_templates('onboarding') # List all templates
    users = update_users() # Get the latest users from DynamoDB and update Notion
    for user in users:
        if user['Remaining credits'] == 0 and user['Last onboarding email'] == 0:
            user['Last onboarding email'] = 1 # Skip the first onboarding as this user already used all their credits
        if user['Last onboarding email'] < len(templates):
            # Last onboarding email is 1-indexed and templates are 0-indexed, so to get the next template we do +1 - 1 = +0
            # TODO: Send the email
            users['Last onboarding email'] += 1 # Increment the last onboarding email sent

if __name__ == "__main__":
    fire.Fire({
        'onboarding': onboarding,
        'send_emails': send_email,
        'update_users': update_users,
        'list_templates': list_templates
    })
