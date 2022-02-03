import os
from pathlib import Path
import ssl
import smtplib
from typing import List, Dict
from email.message import MIMEPart
from email.mime.application import MIMEApplication

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Gmail():
    sender_email = "yyysachinyyy@gmail.com"
    password = os.getenv('GMAIL_SENDER_PASSWORD')

    def __init__(self):
        # Create a multipart message and set headers
        self.message = MIMEMultipart()
        self.message["From"] = Gmail.sender_email

    def send(self, to: List, subject: str = None, body: str = None, attachments: List = []):
        # Add body to email
        self.message["To"] = ', '.join(to)
        self.message["Subject"] = subject
        self.message.attach(MIMEText(body, 'html', 'utf8'))

        # attachment is keyvalue pair [{"filepath": './tp_booking_slot_available.png', "name": 'avaliable_slots_screen_shot' }]
        for attachment in attachments:
            with open(attachment, "rb") as f:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

                # Encode file in ASCII characters to send by email    
                encoders.encode_base64(part)
                # Add header as key/value pair to attachment part
                # for filename only pass the filename which as extention then only octet-strem work
                part.add_header("Content-Disposition", 'attachment', filename=Path(attachment).name)
                self.message.attach(part)

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(Gmail.sender_email, Gmail.password)
            server.sendmail(Gmail.sender_email, to, self.message.as_string())

class SMS():
    pass


if __name__ == '__main__':
    gmail = Gmail()
    gmail.send(
        ['sachindangol@gmail.com'],
        subject='test email',
        body='hello',
        attachments=['./tp_booking_slot_available.png']
    )