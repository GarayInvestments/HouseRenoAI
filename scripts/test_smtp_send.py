#!/usr/bin/env python3
"""
Test SMTP email sending via Gmail with noreply@houserenovatorsllc.com alias
This verifies that the Gmail SMTP relay works with the custom domain alias
"""
import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail SMTP configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Credentials (use environment variables for security)
SMTP_USER = os.getenv("SMTP_USER", "steve@garayinvestments.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # 16-char App Password

# Email configuration
FROM_EMAIL = "House Renovators <noreply@houserenovatorsllc.com>"
TO_EMAIL = os.getenv("TEST_EMAIL", "steve@houserenovatorsllc.com")  # Change to test recipient

def test_smtp_send():
    """Send a test email via Gmail SMTP with custom alias"""
    
    if not SMTP_PASSWORD:
        print("Error: SMTP_PASSWORD not set in environment variables")
        print("Set it in .env file or export SMTP_PASSWORD=your_app_password")
        return False
    
    print(f"Testing SMTP send...")
    print(f"Host: {SMTP_HOST}:{SMTP_PORT}")
    print(f"User: {SMTP_USER}")
    print(f"From: {FROM_EMAIL}")
    print(f"To: {TO_EMAIL}")
    print("-" * 50)
    
    try:
        # Create email message
        msg = EmailMessage()
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg["Subject"] = "SMTP Test - House Renovators noreply alias"
        
        # Set HTML content
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2563eb;">SMTP Test Successful!</h2>
            <p>This is a test email from <strong>noreply@houserenovatorsllc.com</strong> via Gmail SMTP relay.</p>
            <p>If you receive this, your Gmail SMTP configuration is working correctly with the custom domain alias.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                House Renovators LLC © 2025<br>
                This is an automated test message.
            </p>
        </body>
        </html>
        """
        
        msg.set_content("This is a test of noreply@houserenovatorsllc.com via Google SMTP.")
        msg.add_alternative(html_content, subtype='html')
        
        # Send via Gmail SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        print("✅ Email sent successfully!")
        print(f"Check {TO_EMAIL} for the test message")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("Verify your App Password is correct and 2FA is enabled")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_smtp_send()
    exit(0 if success else 1)
