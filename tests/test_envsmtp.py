import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from unittest.mock import MagicMock

import dotenv
import pytest
from pydantic import NameEmail, ValidationError

from envsmtp import EmailAttachment, EmailMessage, get_bool_env

dotenv.load_dotenv()
SMTP_ENV_VARS = ("SMTP_USER", "SMTP_PASS", "SMTP_TEST")
README_PATH = Path(__file__).parent.parent / "README.md"


def email_body() -> str:
    return f"envsmtp test {datetime.now().isoformat()}"


def smtp_env_ready() -> bool:
    return all(os.getenv(var_name) for var_name in SMTP_ENV_VARS)


def smtp_no_auth_env_ready() -> bool:
    has_sender = os.getenv("SMTP_FROM") or os.getenv("SMTP_USER")
    has_test_recipient = os.getenv("SMTP_TEST")
    no_auth = get_bool_env("SMTP_NO_AUTH", default=False)
    return bool(has_sender and has_test_recipient and no_auth)


SIMPLE_MESSAGE = EmailMessage(
    sender=NameEmail(name="Test Sender", email="sender@example.com"),
    recipients=NameEmail(name="Test Recipient", email="recipient@example.com"),
    subject="envsmtp test",
    body=email_body(),
)


def test_bytes_attachment():
    attachment = EmailAttachment(content=b"just_some_bytes", filename="test.txt")
    assert isinstance(attachment.content, bytes)
    assert len(attachment.content) > 0
    assert isinstance(attachment.filename, str)
    with pytest.raises(ValueError):
        attachment = EmailAttachment(content=b"just_some_bytes")


def test_path_attachment():
    attachment = EmailAttachment(content=README_PATH)
    assert isinstance(attachment.content, bytes)
    assert len(attachment.content) > 0
    assert isinstance(attachment.filename, str)


def test_attachment_name_change():
    newname = "other.md"
    attachment = EmailAttachment(content=README_PATH, filename=newname)
    assert isinstance(attachment.content, bytes)
    assert len(attachment.content) > 0
    assert isinstance(attachment.filename, str)
    assert attachment.filename == newname


def test_content_disposition():
    attachment = EmailAttachment(content=README_PATH)
    mime_part = attachment.as_mime_part()
    assert mime_part["Content-Disposition"] == f'attachment; filename="{attachment.filename}"'


def test_bad_attachment():
    with pytest.raises(ValidationError):
        EmailAttachment(content=Path("nothing_here_bla_bla.jpg"))


@pytest.mark.skipif(smtp_env_ready(), reason="All required SMTP_* environment variables are set")
def test_missing_env_variables():
    with pytest.raises(EnvironmentError):
        SIMPLE_MESSAGE.model_copy().smtp_send()


@pytest.mark.skipif(not smtp_no_auth_env_ready(), reason="Missing SMTP_FROM/SMTP_TEST environment variables")
def test_basic_send_no_tls_ssl_auth(monkeypatch: pytest.MonkeyPatch):
    mock_server = MagicMock()
    monkeypatch.setattr(smtplib, "SMTP", lambda *_args, **_kwargs: mock_server)
    monkeypatch.setenv("SMTP_USE_TLS", "false")
    monkeypatch.setenv("SMTP_USE_SSL", "false")
    monkeypatch.setenv("SMTP_NO_AUTH", "true")

    msg = SIMPLE_MESSAGE.model_copy()
    msg.sender = NameEmail(name="No Auth Sender", email="noauth@example.com")

    assert msg.smtp_send() is True
    mock_server.starttls.assert_not_called()
    mock_server.login.assert_not_called()
    mock_server.sendmail.assert_called_once()
    sender_arg = mock_server.sendmail.call_args[0][0]
    assert sender_arg == "noauth@example.com"


@pytest.mark.skipif(not smtp_env_ready(), reason="Missing SMTP_USER/SMTP_PASS/SMTP_TEST environment variables")
def test_env_variables():
    assert os.getenv("SMTP_USER") is not None
    assert os.getenv("SMTP_PASS") is not None
    assert os.getenv("SMTP_TEST") is not None


@pytest.mark.skipif(not smtp_env_ready(), reason="Missing SMTP_USER/SMTP_PASS/SMTP_TEST environment variables")
def test_basic_send():
    msg = SIMPLE_MESSAGE.model_copy()
    assert isinstance(msg.attachments, list | tuple), "Should default to empty list for attachments"
    assert len(msg.attachments) == 0
    assert isinstance(msg.as_mime(), MIMEMultipart)
    assert msg.smtp_send() is True


@pytest.mark.skipif(not smtp_env_ready(), reason="Missing SMTP_USER/SMTP_PASS/SMTP_TEST environment variables")
def test_one_attachment():
    msg = SIMPLE_MESSAGE.model_copy()
    msg.body += "ONE ATTACHMENT"
    msg.attachments = EmailAttachment(content=README_PATH)
    assert isinstance(msg.as_mime(), MIMEMultipart)
    assert msg.smtp_send() is True


@pytest.mark.skipif(not smtp_env_ready(), reason="Missing SMTP_USER/SMTP_PASS/SMTP_TEST environment variables")
def test_multi_attachments():
    msg = SIMPLE_MESSAGE.model_copy()
    msg.body += "TWO ATTACHMENTS"
    msg.attachments = [
        EmailAttachment(content=README_PATH),
        EmailAttachment(content=b"random_bytes", filename="test.txt"),
    ]
    assert isinstance(msg.as_mime(), MIMEMultipart)
    assert msg.smtp_send() is True
