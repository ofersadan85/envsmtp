import os
import dotenv
import smtplib

from pathlib import Path
from typing import Any
from pydantic import BaseModel, NameEmail, FilePath

from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

COMMASPACE = ", "


class EmailAttachment(BaseModel):
    content: FilePath | bytes
    filename: str = ""

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if isinstance(self.content, FilePath | Path | str):
            path = Path(self.content)
            if not path.is_file():
                raise FileNotFoundError(f"No file found at: {path}")
            if not self.filename:
                self.filename = path.name
            self.content = path.read_bytes()
        if not self.filename:
            raise ValueError("Attempted to send bytes without filename")

    def as_mime_part(self) -> MIMEApplication:
        mime_part = MIMEApplication(self.content, self.filename)
        mime_part["Content-Disposition"] = f'attachment; filename="{self.filename}"'
        return mime_part


class EmailMessage(BaseModel):
    sender: NameEmail
    receipients: NameEmail | list[NameEmail]
    subject: str = ""
    body: str = ""
    rtl: bool = False
    attachments: EmailAttachment | list[EmailAttachment] = ()
    send: bool = False

    def as_mime(self) -> MIMEMultipart:
        if isinstance(self.receipients, NameEmail):
            self.receipients = [self.receipients]
        if isinstance(self.attachments, EmailAttachment):
            self.attachments = [self.attachments]

        mime = MIMEMultipart()
        mime["From"] = str(self.sender)
        mime["To"] = COMMASPACE.join(r.email for r in self.receipients)
        mime["Date"] = formatdate(localtime=True)
        mime["Subject"] = self.subject

        body_tag = '<body align="right" dir="rtl">' if self.rtl else "<body>"
        html_part = f"""<html><head></head>{body_tag}
        <div>{self.body}</div></body></html>"""
        html_part = html_part.replace("\n", "<br>")
        mime.attach(MIMEText(html_part, "html"))

        for item in self.attachments:
            mime.attach(item.as_mime_part())

        if self.send:
            self.smtp_send()

        return mime

    def smtp_send(self) -> bool:
        mime = self.as_mime()
        dotenv.load_dotenv()
        SMTP_USER = os.getenv("SMTP_USER")
        SMTP_PASS = os.getenv("SMTP_PASS")
        SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("SMTP_POST", "587"))
        SMTP_TEST = os.getenv("SMTP_TEST")
        RECEIPIENT = SMTP_TEST if SMTP_TEST else mime["To"]
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, RECEIPIENT.split(COMMASPACE), str(mime))
        server.close()
        return True
