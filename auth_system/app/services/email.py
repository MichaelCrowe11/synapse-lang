"""
Email Service for sending notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
):
    """Send an email using SMTP."""
    
    if not settings.SMTP_HOST:
        # If no SMTP configured, just log the email
        logger.info(f"Email would be sent to {to_email}: {subject}")
        logger.debug(f"Email body: {body}")
        return
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = to_email
        
        # Add text and HTML parts
        msg.attach(MIMEText(body, 'plain'))
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
    
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise

async def send_verification_email(
    email: str,
    name: str,
    token: str
):
    """Send email verification."""
    
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    subject = "Verify Your Synapse Account"
    
    body = f"""
Hello {name},

Welcome to Synapse! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hours.

If you didn't create an account, please ignore this email.

Best regards,
The Synapse Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Synapse!</h1>
        </div>
        <div class="content">
            <h2>Hello {name},</h2>
            <p>Thank you for signing up for Synapse. To complete your registration, please verify your email address.</p>
            <p style="text-align: center;">
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 5px;">
                {verification_url}
            </p>
            <div class="footer">
                <p>This link will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hours.</p>
                <p>If you didn't create an account, please ignore this email.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    await send_email(email, subject, body, html_body)

async def send_password_reset_email(
    email: str,
    name: str,
    token: str
):
    """Send password reset email."""
    
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    subject = "Reset Your Synapse Password"
    
    body = f"""
Hello {name},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hours.

If you didn't request a password reset, please ignore this email and your password will remain unchanged.

Best regards,
The Synapse Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Password Reset Request</h1>
        </div>
        <div class="content">
            <h2>Hello {name},</h2>
            <p>We received a request to reset your password. Click the button below to set a new password:</p>
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 5px;">
                {reset_url}
            </p>
            <div class="warning">
                <strong>Security Note:</strong> If you didn't request a password reset, please ignore this email and your password will remain unchanged.
            </div>
            <div class="footer">
                <p>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hours.</p>
                <p>For security reasons, this is an automated email and replies will not be monitored.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    await send_email(email, subject, body, html_body)

async def send_subscription_confirmation(
    email: str,
    name: str,
    tier: str,
    billing_cycle: str
):
    """Send subscription confirmation email."""
    
    subject = f"Subscription Confirmed - {tier.title()} Plan"
    
    body = f"""
Hello {name},

Your subscription to Synapse {tier.title()} plan has been confirmed!

Subscription Details:
- Plan: {tier.title()}
- Billing Cycle: {billing_cycle.title()}
- Status: Active

You can manage your subscription at any time from your account dashboard.

Thank you for choosing Synapse!

Best regards,
The Synapse Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .details {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Subscription Confirmed!</h1>
        </div>
        <div class="content">
            <h2>Hello {name},</h2>
            <p>Thank you for subscribing to Synapse! Your subscription is now active.</p>
            <div class="details">
                <h3>Subscription Details</h3>
                <p><strong>Plan:</strong> {tier.title()}</p>
                <p><strong>Billing Cycle:</strong> {billing_cycle.title()}</p>
                <p><strong>Status:</strong> Active</p>
            </div>
            <p style="text-align: center;">
                <a href="{settings.FRONTEND_URL}/dashboard" class="button">Go to Dashboard</a>
            </p>
            <div class="footer">
                <p>You can manage your subscription at any time from your account dashboard.</p>
                <p>If you have any questions, please don't hesitate to contact our support team.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    await send_email(email, subject, body, html_body)