import os
import dotenv
import unittest
from pathlib import Path
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from pydantic.error_wrappers import ValidationError
from envsmtp import EmailMessage, EmailAttachment


def email_body() -> str:
    return f"envsmtp test {datetime.now().isoformat()}"


simple_msg = dict(
    sender="sender@example.com",
    receipients="receipient@example.com",
    subject="envsmtp test",
    body=email_body(),
)


class TestAttachments(unittest.TestCase):
    def test_bytes_attachment(self):
        attachment = EmailAttachment(content=b"justsomebytes", filename="test.txt")
        self.assertIsInstance(attachment.content, bytes)
        self.assertGreater(len(attachment.content), 0)
        self.assertIsInstance(attachment.filename, str)

    def test_path_attachment(self):
        attachment = EmailAttachment(content="README.md")
        self.assertIsInstance(attachment.content, bytes)
        self.assertGreater(len(attachment.content), 0)
        self.assertIsInstance(attachment.filename, str)

    def test_attachment_name_change(self):
        newname = "other.md"
        attachment = EmailAttachment(content=Path("README.md"), filename=newname)
        self.assertIsInstance(attachment.content, bytes)
        self.assertGreater(len(attachment.content), 0)
        self.assertIsInstance(attachment.filename, str)
        self.assertEqual(attachment.filename, newname)

    def test_bad_attachment(self):
        no_file = "nothing_here_dfkhsfda.jpg"
        self.assertRaises(ValidationError, EmailAttachment, content=Path(no_file))
        self.assertRaises(ValueError, EmailAttachment, content=no_file)


class TestSMTP(unittest.TestCase):
    def test_env_variables(self):
        dotenv.load_dotenv()
        self.assertIsNotNone(os.getenv("SMTP_USER"))
        self.assertIsNotNone(os.getenv("SMTP_PASS"))
        self.assertIsNotNone(os.getenv("SMTP_TEST"))

    def test_basic_send(self):
        msg = EmailMessage(**simple_msg)
        self.assertEqual(len(msg.attachments), 0)
        self.assertIsInstance(msg.as_mime(), MIMEMultipart)
        self.assertTrue(msg.smtp_send())

    def test_one_attachment(self):
        attachments = EmailAttachment(content="README.md")
        attachment_msg = simple_msg.copy()
        attachment_msg["body"] += "ONE ATTACHMENT"
        attachment_msg.update(attachments=attachments)
        msg = EmailMessage(**attachment_msg)
        self.assertIsInstance(msg.attachments, EmailAttachment)
        self.assertIsInstance(msg.as_mime(), MIMEMultipart)
        self.assertTrue(msg.smtp_send())

    def test_multi_attachments(self):
        attachments = [
            EmailAttachment(content="README.md"),
            EmailAttachment(content=b"randombytes", filename="test.txt"),
        ]
        attachment_msg = simple_msg.copy()
        attachment_msg["body"] += "TWO ATTACHMENTS"
        attachment_msg.update(attachments=attachments)
        msg = EmailMessage(**attachment_msg)
        self.assertEqual(len(msg.attachments), 2)
        self.assertIsInstance(msg.as_mime(), MIMEMultipart)
        self.assertTrue(msg.smtp_send())
