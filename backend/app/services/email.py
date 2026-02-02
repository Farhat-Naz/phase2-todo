"""
Email service for sending transactional emails.

Supports multiple providers:
- SendGrid (recommended for production)
- AWS SES (alternative provider)

Required environment variables:
- EMAIL_PROVIDER: "sendgrid" or "aws_ses"
- SENDGRID_API_KEY: SendGrid API key (if using SendGrid)
- AWS_SES_REGION, AWS_SES_ACCESS_KEY_ID, AWS_SES_SECRET_ACCESS_KEY (if using AWS SES)
- EMAIL_FROM_ADDRESS: Sender email (must be verified in provider)
- EMAIL_FROM_NAME: Sender display name
- FRONTEND_URL: Frontend base URL for email links
"""
import os
from typing import Optional
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Email configuration from environment
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "sendgrid")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
AWS_SES_REGION = os.getenv("AWS_SES_REGION", "us-east-1")
AWS_SES_ACCESS_KEY_ID = os.getenv("AWS_SES_ACCESS_KEY_ID", "")
AWS_SES_SECRET_ACCESS_KEY = os.getenv("AWS_SES_SECRET_ACCESS_KEY", "")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS", "noreply@example.com")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "TodoApp")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email using the configured provider.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_content: HTML email body
        text_content: Plain text email body (optional, fallback for HTML)

    Returns:
        bool: True if email sent successfully, False otherwise

    Raises:
        Exception: If email provider is not configured properly

    Example:
        success = await send_email(
            to_email="user@example.com",
            subject="Welcome to TodoApp",
            html_content="<h1>Welcome!</h1>",
            text_content="Welcome!"
        )
    """
    try:
        if EMAIL_PROVIDER == "sendgrid":
            return await _send_via_sendgrid(to_email, subject, html_content, text_content)
        elif EMAIL_PROVIDER == "aws_ses":
            return await _send_via_aws_ses(to_email, subject, html_content, text_content)
        else:
            logger.error(f"Unknown email provider: {EMAIL_PROVIDER}")
            return False
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def _send_via_sendgrid(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """Send email using SendGrid API."""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=(EMAIL_FROM_ADDRESS, EMAIL_FROM_NAME),
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        if text_content:
            message.plain_text_content = text_content

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code in [200, 201, 202]:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"SendGrid returned status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"SendGrid error: {str(e)}")
        return False


async def _send_via_aws_ses(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """Send email using AWS SES."""
    try:
        import boto3
        from botocore.exceptions import ClientError

        client = boto3.client(
            'ses',
            region_name=AWS_SES_REGION,
            aws_access_key_id=AWS_SES_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SES_SECRET_ACCESS_KEY
        )

        body = {
            'Html': {'Data': html_content, 'Charset': 'UTF-8'}
        }
        if text_content:
            body['Text'] = {'Data': text_content, 'Charset': 'UTF-8'}

        response = client.send_email(
            Source=f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>",
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': body
            }
        )

        logger.info(f"Email sent successfully to {to_email} (MessageId: {response['MessageId']})")
        return True

    except ClientError as e:
        logger.error(f"AWS SES error: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        logger.error(f"AWS SES error: {str(e)}")
        return False


async def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send password reset email with reset link (US2).

    Args:
        email: User's email address
        token: Password reset token (plain text, not hashed)

    Returns:
        bool: True if email sent successfully, False otherwise

    Security:
        - Token expires after 24 hours (enforced at API layer)
        - Token can only be used once (enforced at API layer)
        - Link format: {FRONTEND_URL}/reset-password?token={token}

    Example:
        success = await send_password_reset_email(
            email="user@example.com",
            token="abc123def456"
        )
    """
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    subject = "Reset Your Password - TodoApp"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #4F46E5;
                color: white !important;
                text-decoration: none;
                border-radius: 6px;
                margin: 20px 0;
            }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Reset Your Password</h1>
            <p>You requested to reset your password for your TodoApp account.</p>
            <p>Click the button below to create a new password:</p>
            <a href="{reset_link}" class="button">Reset Password</a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{reset_link}</p>
            <p><strong>This link will expire in 24 hours.</strong></p>
            <p>If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.</p>
            <div class="footer">
                <p>This is an automated message from TodoApp. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Reset Your Password

    You requested to reset your password for your TodoApp account.

    Click the link below to create a new password:
    {reset_link}

    This link will expire in 24 hours.

    If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.

    ---
    This is an automated message from TodoApp. Please do not reply to this email.
    """

    return await send_email(email, subject, html_content, text_content)


async def send_verification_email(email: str, token: str) -> bool:
    """
    Send email verification email with verification link (US3).

    Args:
        email: User's email address
        token: Email verification token (plain text, not hashed)

    Returns:
        bool: True if email sent successfully, False otherwise

    Security:
        - Token expires after 24 hours (enforced at API layer)
        - Token deleted after successful verification (enforced at API layer)
        - Link format: {FRONTEND_URL}/verify-email?token={token}

    Example:
        success = await send_verification_email(
            email="user@example.com",
            token="abc123def456"
        )
    """
    verification_link = f"{FRONTEND_URL}/verify-email?token={token}"

    subject = "Verify Your Email - TodoApp"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #10B981;
                color: white !important;
                text-decoration: none;
                border-radius: 6px;
                margin: 20px 0;
            }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to TodoApp!</h1>
            <p>Thank you for signing up. Please verify your email address to activate your account.</p>
            <p>Click the button below to verify your email:</p>
            <a href="{verification_link}" class="button">Verify Email</a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{verification_link}</p>
            <p><strong>This link will expire in 24 hours.</strong></p>
            <p>If you didn't create a TodoApp account, you can safely ignore this email.</p>
            <div class="footer">
                <p>This is an automated message from TodoApp. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Welcome to TodoApp!

    Thank you for signing up. Please verify your email address to activate your account.

    Click the link below to verify your email:
    {verification_link}

    This link will expire in 24 hours.

    If you didn't create a TodoApp account, you can safely ignore this email.

    ---
    This is an automated message from TodoApp. Please do not reply to this email.
    """

    return await send_email(email, subject, html_content, text_content)


async def send_email_changed_notification(old_email: str, new_email: str) -> bool:
    """
    Send notification to old email when email address is changed (US7).

    Args:
        old_email: User's previous email address
        new_email: User's new email address (partially masked)

    Returns:
        bool: True if email sent successfully, False otherwise

    Security:
        - Notifies user of security-relevant account changes
        - Partially masks new email for privacy (e.g., "n***@example.com")
        - Provides support contact for unauthorized changes

    Example:
        success = await send_email_changed_notification(
            old_email="old@example.com",
            new_email="n***@example.com"
        )
    """
    subject = "Your Email Address Was Changed - TodoApp"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .alert {{
                background-color: #FEF3C7;
                border-left: 4px solid #F59E0B;
                padding: 15px;
                margin: 20px 0;
            }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Email Address Changed</h1>
            <div class="alert">
                <strong>Security Alert:</strong> Your TodoApp account email address was recently changed.
            </div>
            <p><strong>Old email:</strong> {old_email}</p>
            <p><strong>New email:</strong> {new_email}</p>
            <p>If you made this change, no further action is needed.</p>
            <p><strong>If you did not make this change:</strong></p>
            <ul>
                <li>Your account may be compromised</li>
                <li>Contact our support team immediately</li>
                <li>Change your password as soon as possible</li>
            </ul>
            <div class="footer">
                <p>This is an automated security notification from TodoApp. Please do not reply to this email.</p>
                <p>For support, contact: support@example.com</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Email Address Changed

    SECURITY ALERT: Your TodoApp account email address was recently changed.

    Old email: {old_email}
    New email: {new_email}

    If you made this change, no further action is needed.

    If you did not make this change:
    - Your account may be compromised
    - Contact our support team immediately
    - Change your password as soon as possible

    ---
    This is an automated security notification from TodoApp. Please do not reply to this email.
    For support, contact: support@example.com
    """

    return await send_email(old_email, subject, html_content, text_content)
