"""
Mock Email Backend for Development/Demo
Stores emails in database for professional inbox display.
"""
from django.core.mail.backends.base import BaseEmailBackend
from .models import SentEmail


class MockEmailBackend(BaseEmailBackend):
    """
    Mock email backend that stores emails in the database (SentEmail model).
    Used for development and demonstrations.
    Emails are displayed in a professional inbox view at /debug/sent-emails/
    """

    def send_messages(self, email_messages):
        """Store email messages in database."""
        if not email_messages:
            return 0

        msg_count = 0
        for message in email_messages:
            try:
                # Extract email details
                to_email = ', '.join(message.to) if message.to else 'unknown'
                subject = message.subject or '(No Subject)'
                body = message.body or ''
                html_body = None

                # Check if email has HTML alternative
                if hasattr(message, 'alternatives'):
                    for alternative_body, mime_type in message.alternatives:
                        if mime_type == 'text/html':
                            html_body = alternative_body
                            break

                # Store in database
                SentEmail.objects.create(
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    html_body=html_body
                )
                msg_count += 1
            except Exception as e:
                print(f"Error storing email: {str(e)}")

        return msg_count
