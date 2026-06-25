import os
import ssl
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
RECIPIENTS = os.environ["RECIPIENTS"]


def send_email(subject, html_body, attachment_path=None):
    msg = EmailMessage()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENTS
    msg["Subject"] = subject
    msg.set_content("This briefing is best viewed in an HTML email client.")  # plain-text fallback
    msg.add_alternative(html_body, subtype="html")

    if attachment_path:
        with open(attachment_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
                filename=os.path.basename(attachment_path),
            )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)


if __name__ == "__main__":
    send_email(
        subject="Monitoring — test",
        html_body="<h1>Test</h1><p>If you can read this, HTML email works.</p>",
    )
    print(f"Sent test to {RECIPIENTS}")