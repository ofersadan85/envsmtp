import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from pathlib import Path

import dotenv
import pytest
from pydantic import ValidationError

from envsmtp import EmailAttachment, EmailMessage

dotenv.load_dotenv()
SMTP_ENV_VARS = ("SMTP_USER", "SMTP_PASS", "SMTP_TEST")


def email_body() -> str:
    return f"envsmtp test {datetime.now().isoformat()}"


def smtp_env_ready() -> bool:
    return all(os.getenv(var_name) for var_name in SMTP_ENV_VARS)


simple_msg = dict(
    sender="sender@example.com",
    recipients="recipient@example.com",
    subject="envsmtp test",
    body=email_body(),
)


def test_bytes_attachment():
    attachment = EmailAttachment(content=b"just_some_bytes", filename="test.txt")
    assert isinstance(attachment.content, bytes)
    assert len(attachment.content) > 0
    assert isinstance(attachment.filename, str)


def test_path_attachment():
    attachment = EmailAttachment(content="README.md")
    assert isinstance(attachment.content, bytes)
    assert len(attachment.content) > 0
    assert isinstance(attachment.filename, str)


def test_attachment_name_change():
    newname = "other.md"
    attachment = EmailAttachment(content=Path("README.md"), filename=newname)
    assert isinstance(attachment.content, bytes)
    assert len(attachment.content) > 0
    assert isinstance(attachment.filename, str)
    assert attachment.filename == newname


def test_bad_attachment():
    no_file = "nothing_here_bla_bla.jpg"
    with pytest.raises(ValidationError):
        EmailAttachment(content=Path(no_file))
    with pytest.raises(ValueError):
        EmailAttachment(content=no_file)


@pytest.mark.skipif(not smtp_env_ready(), reason="Missing SMTP_USER/SMTP_PASS/SMTP_TEST environment variables")
def test_env_variables():
    assert os.getenv("SMTP_USER") is not None
    assert os.getenv("SMTP_PASS") is not None
    assert os.getenv("SMTP_TEST") is not None


@pytest.mark.skipif(not smtp_env_ready(), reason="Missing SMTP_USER/SMTP_PASS/SMTP_TEST environment variables")
def test_basic_send():
    msg = EmailMessage(**simple_msg)
    assert len(msg.attachments) == 0
    assert isinstance(msg.as_mime(), MIMEMultipart)
    assert msg.smtp_send() is True


@pytest.mark.skipif(not smtp_env_ready(), reason="Missing SMTP_USER/SMTP_PASS/SMTP_TEST environment variables")
def test_one_attachment():
    attachments = EmailAttachment(content="README.md")
    attachment_msg = simple_msg.copy()
    attachment_msg["body"] += "ONE ATTACHMENT"
    attachment_msg.update(attachments=attachments)
    msg = EmailMessage(**attachment_msg)
    assert isinstance(msg.attachments, EmailAttachment)
    assert isinstance(msg.as_mime(), MIMEMultipart)
    assert msg.smtp_send() is True


@pytest.mark.skipif(not smtp_env_ready(), reason="Missing SMTP_USER/SMTP_PASS/SMTP_TEST environment variables")
def test_multi_attachments():
    attachments = [
        EmailAttachment(content="README.md"),
        EmailAttachment(content=b"random_bytes", filename="test.txt"),
    ]
    attachment_msg = simple_msg.copy()
    attachment_msg["body"] += "TWO ATTACHMENTS"
    attachment_msg.update(attachments=attachments)
    msg = EmailMessage(**attachment_msg)
    assert len(msg.attachments) == 2
    assert isinstance(msg.as_mime(), MIMEMultipart)
    assert msg.smtp_send() is True
