from requests import Response, post
from typing import List
import os

class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    # FROM_EMAIL = os.environ.get("FROM_EMAIL")

    @classmethod
    def send_email(cls, email: List[str], subject: str, text, html) -> Response:
        if cls.MAILGUN_DOMAIN is None or cls.MAILGUN_API_KEY is None:
            raise MailgunException("Failed to load mailgun domain or api key.")
        response = post(f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
                    auth=("api", cls.MAILGUN_API_KEY),
                    data={"from": f"<mailgun@{cls.MAILGUN_DOMAIN}>",
                          "to": email,
                          "subject": subject,
                          "text": text,
                          "html": html})
        if response.status_code != 200:
            raise MailgunException("Error in sending confirmation email, user registration failed.")
