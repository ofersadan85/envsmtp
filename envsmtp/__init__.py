import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from typing import Any, Sequence

import dotenv
from pydantic import BaseModel, Field, FilePath, NameEmail

COMMASPACE = ", "


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value


def get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name, default=str(default))
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


class EmailAttachment(BaseModel):
    content: FilePath | bytes
    filename: str = ""

    def model_post_init(self, __context: Any) -> None:
        if isinstance(self.content, Path | str):
            path = Path(self.content)
            assert path.is_file(), f"No file found at: {path} (Should be caught by FilePath validation)"
            if not self.filename:
                self.filename = path.name
            self.content = path.read_bytes()
        if not self.filename:
            raise ValueError("Attempted to send bytes without filename")

    def as_mime_part(self) -> MIMEApplication:
        assert isinstance(self.content, bytes), "Content should be bytes at this point"
        mime_part = MIMEApplication(self.content, self.filename)
        mime_part["Content-Disposition"] = f'attachment; filename="{self.filename}"'
        return mime_part


def sender_from_env() -> NameEmail:
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
    if SMTP_FROM_NAME and SMTP_FROM_EMAIL:
        return NameEmail(name=SMTP_FROM_NAME, email=SMTP_FROM_EMAIL)
    SMTP_FROM = os.getenv("SMTP_FROM") or os.getenv("SMTP_USER")
    if not SMTP_FROM:
        raise EnvironmentError("Missing required environment variable: SMTP_FROM or SMTP_USER")
    return NameEmail(name=SMTP_FROM.split("@")[0], email=SMTP_FROM)


class EmailMessage(BaseModel):
    sender: NameEmail = Field(default_factory=sender_from_env)
    recipients: NameEmail | list[NameEmail]
    subject: str = ""
    body: str = ""
    rtl: bool = False
    attachments: EmailAttachment | Sequence[EmailAttachment] = ()
    send: bool = False

    def as_mime(self) -> MIMEMultipart:
        if isinstance(self.recipients, NameEmail):
            self.recipients = [self.recipients]
        if isinstance(self.attachments, EmailAttachment):
            self.attachments = [self.attachments]

        mime = MIMEMultipart()
        mime["From"] = str(self.sender)
        mime["To"] = COMMASPACE.join(r.email for r in self.recipients)
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
        SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        SMTP_USE_TLS = get_bool_env("SMTP_USE_TLS", default=True)
        SMTP_USE_SSL = get_bool_env("SMTP_USE_SSL", default=False)
        SMTP_NO_AUTH = get_bool_env("SMTP_NO_AUTH", default=False)
        RECIPIENT = os.getenv("SMTP_TEST", mime["To"])
        if SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.ehlo()
        if SMTP_USE_TLS and not SMTP_USE_SSL:
            server.starttls()
            server.ehlo()

        if SMTP_NO_AUTH:
            sender_address = self.sender.email
        else:
            SMTP_USER = get_required_env("SMTP_USER")
            SMTP_PASS = get_required_env("SMTP_PASS")
            server.login(SMTP_USER, SMTP_PASS)
            sender_address = SMTP_USER

        server.sendmail(sender_address, RECIPIENT.split(COMMASPACE), str(mime))
        server.close()
        return True
