import smtplib
from email.mime.text import MIMEText

EMAIL="krishnaramasamy294@gmail.com"
PASSWORD="myyj xghw kfsn cxsy"


def send_verification_mail(email,token):

    verification_link = f"http://127.0.0.1:8000/verify-email?token={token}"

    body = f"""
Hello,

Please verify your email.

Click below:

{verification_link}

Link expires in 10 minutes.
"""

    msg = MIMEText(body)
    msg["Subject"]="Verify Email"

    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(EMAIL,PASSWORD)

    server.sendmail(
        EMAIL,
        email,
        msg.as_string()
    )

    server.quit()
def send_welcome_mail(email,role):

    if role=="admin":

        body="""
Welcome

You are registered as ADMIN.

You have full access.
"""

    else:

        body="""
Welcome

You are registered as USER.

You have limited access.
"""

    msg = MIMEText(body)
    msg["Subject"]="Registration Successful"

    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(EMAIL,PASSWORD)

    server.sendmail(
        EMAIL,
        email,
        msg.as_string()
    )

    server.quit()