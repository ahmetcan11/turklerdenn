import smtplib, ssl
from email.message import EmailMessage
from typing import List

from fastapi import HTTPException

from schemas.Otp.otp_schema import OtpCreate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(otp_code: str, otp_in: OtpCreate):
    email_address = "info@turklerden.com"  # type Email

    # create email
    msg = EmailMessage()
    msg['Subject'] = "First Email"
    msg['From'] = email_address
    msg['To'] = otp_in.recipient_id  # type Email
    msg.set_content(
        f"""\
    Code : {otp_code}  
    """,

    )
    # send email
    with smtplib.SMTP_SSL('smtp.office365.com', 587) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)

    return "email successfully sent"


def send_email2(otp_code: str, otp_in: OtpCreate):
    port = 587  # For starttls
    smtp_server = "smtp.office365.com"
    sender_email = "info@turklerden.com"
    receiver_email = otp_in.recipient_id
    subject = "Subject: Verify Email"

    message_body = f"""\
    Verification Code : {otp_code}
    """

    # Combine subject and message body
    message = 'Subject: {}\n\n{}'.format(subject, message_body)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
    except smtplib.SMTPRecipientsRefused as e:
        # Handle the SMTPRecipientsRefused exception here
        # You can log the error or take appropriate action
        print("SMTPRecipientsRefused error:", e)
        raise HTTPException(status_code=400, detail="Bad Request: Email recipient refused") from e


def reset_email(subject: str, recipient: str, message: str):
    port = 587  # For starttls
    smtp_server = "smtp.office365.com"
    sender_email = "info@turklerden.com"
    receiver_email = recipient
    # Combine subject and message body

    # Create an instance of MIMEMultipart
    msg = MIMEMultipart()

    # Set the email content type to HTML
    msg.attach(MIMEText(message, 'html'))

    # Configure email headers
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    # Connect to the SMTP server using TLS
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient, msg.as_string())

    # message = 'Subject: {}\n\n{}'.format(subject, message)
    # context = ssl.create_default_context()
    # with smtplib.SMTP(smtp_server, port) as server:
    #     server.ehlo()  # Can be omitted
    #     server.starttls(context=context)
    #     server.ehlo()  # Can be omitted
    #     server.login(sender_email, password)
    #     server.sendmail(sender_email, receiver_email, message)
