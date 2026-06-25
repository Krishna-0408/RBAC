import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL="krishnaramasamy294@gmail.com"
PASSWORD="myyj xghw kfsn cxsy"


def send_email(to_email: str, role: str):

    subject = "Registration Successful"

    if role == "admin":
        body = f"""
Hello,

Welcome!

You are registered successfully.

Role : ADMIN

You have full access to the application.

Thank you.
"""

    else:
        body = f"""
Hello,

Welcome!

You are registered successfully.

Role : USER

You have limited access to the application.

Thank you.
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, PASSWORD)

    server.sendmail(
        EMAIL,
        to_email,
        msg.as_string()
    )

    server.quit()