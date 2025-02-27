import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from helper import wrap_link

load_dotenv()

MERGE_API_KEY = os.getenv("MERGE_API_KEY")
MERGE_ACCOUNT_TOKEN = os.getenv("MERGE_ACCOUNT_TOKEN")
MERGE_BASE_URL = os.getenv("MERGE_BASE_URL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
SENDGRID_TO_EMAIL = os.getenv("SENDGRID_TO_EMAIL")
NETSUITE_ACCOUNT_ID = os.getenv("NETSUITE_ACCOUNT_ID")


def check_unpaid_bills():
    """Check for unpaid bills and send email notification if any are overdue."""
    # Just get invoices (ACCOUNTS_PAYABLE) that have not been paid (status=OPEN)
    url = (
        f"{MERGE_BASE_URL}/invoices"
        "?type=ACCOUNTS_PAYABLE&status=OPEN"
    )

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {MERGE_API_KEY}",
            "X-Account-Token": MERGE_ACCOUNT_TOKEN,
        },
    )
    response.raise_for_status()

    decoded_response = response.json()
    invoices = decoded_response["results"]
    if not invoices:
        print("No invoices found")
        return

    invoice_html = ""

    for invoice in invoices:
        # Parse ISO format datetime string. Merge always returns in UTC
        due_date = datetime.fromisoformat(invoice["due_date"])

        # Compare due date with current datetime in UTC
        if due_date < datetime.now(timezone.utc):
            invoice_html += (
                f"<li>Invoice {wrap_link(NETSUITE_ACCOUNT_ID, invoice['remote_id'])} "
                f"(${int(invoice['total_amount'])}) is due on "
                f"{due_date.strftime('%B %d, %Y')}</li>"
            )

    # We can send a text, email, slack msg, etc. Good place to explore
    # Zapier. We'll choose to send an email.
    # Let's use plaintext for now. For production,
    # switch to SendGrid's template feature.

    email_html = (
        "<p>The following invoices are due:</p>"
        f"<div><ol>{invoice_html}</ol></div>"
    )

    sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=SENDGRID_TO_EMAIL,
        subject="Unpaid invoices",
        html_content=email_html,
    )
    sendgrid_client.send(message)


if __name__ == "__main__":
    check_unpaid_bills()
