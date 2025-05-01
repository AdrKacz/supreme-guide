import fire # type: ignore
from src.send_emails import send_emails
from src.export_users import export_users
from src.list_templates import list_templates


if __name__ == "__main__":
    fire.Fire({
        'send_emails': send_emails,
        'export_users': export_users,
        'list_templates': list_templates
    })
