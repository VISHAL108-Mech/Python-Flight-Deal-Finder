"""Email alert helpers for the flight deal notifier."""

import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

# SMTP credentials are loaded from environment variables in a local .env file.
EMAIL = os.getenv("SMTP_GMAIL_ID")
PASSWORD = os.getenv("SMTP_GMAIL_PASSWORD")


class NotificationManager:
    """Send low-price flight alerts using the configured Gmail SMTP account."""

    def __init__(self):
        """Store the Gmail credentials used by all outgoing email alerts."""
        self.email = EMAIL
        self.password = PASSWORD

    def send_notification(self, message):
        """Send a single message to the configured sender address."""
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=self.email, password=self.password)
            connection.sendmail(
                from_addr=self.email,
                to_addrs=self.email,
                msg=message.encode("utf-8"),
            )

    def send_email(self, message, user_email):
        """Send one alert to each email address in a user list."""
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=self.email, password=self.password)
            for email in user_email:
                connection.sendmail(
                    from_addr=self.email,
                    to_addrs=email,
                    msg=message.encode("utf-8"),
                )
